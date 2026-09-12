#!/usr/bin/env python3
"""
扫一家公司的招聘板, 把观测结果记进看板。

    python3 jobs/scan_board.py airbnb                       # 自动猜 board 地址
    python3 jobs/scan_board.py union-flyte --slug union     # slug 和公司名对不上时手动给
    python3 jobs/scan_board.py --all                        # 扫所有已知 board 的公司
    python3 jobs/scan_board.py airbnb --dry                 # 只看不写

记的是**四个计数**, 不是岗位列表:

    scan_n   在招总数(全部部门)
    scan_ng  entry level / new grad 的**工程岗**   <- 你真正要看的那个数
    scan_mid 中级工程岗(不带资历前缀、也不是 ng)
    scan_sr  资深工程岗(senior / staff / principal / lead 及以上)

后三个只数工程岗 —— 把设计、运营、市场算进去会让 mid 看起来很多, 而那些跟你无关。

为什么记计数而不是岗位: 一次快照分不出「招完了」和「没开过」—— 下架的岗根本不在
API 里。但**同一家扫很多次**之后, 这几个数字的变化就能答: 某天 scan_ng 从 0 变 1
= 坑刚开(立刻投); 三个月一直 0 = 它不招 entry, 从池子里删。

只打两个公开 JSON API, 不需要 key:
    Greenhouse  https://boards-api.greenhouse.io/v1/boards/<slug>/jobs
    Ashby       https://api.ashbyhq.com/posting-api/job-board/<slug>
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date

API = "http://localhost:8766"

# 资历分档。先判 NG(它会撞上 "Associate" 这类词), 再判 SR, 都不中算 mid。
NG = re.compile(r"new.?grad|university|campus|\bgraduate\b|intern\b|entry.?level|"
                r"apprentice|associate engineer|\bjunior\b|early career", re.I)
# 结尾的罗马数字 I 只在不带资历词时才算初级 ——「Staff Software Engineer I」是 staff 档里的一级
LEVEL_I = re.compile(r"\bI\b\s*$")
SR = re.compile(r"\bsenior\b|\bstaff\b|\bprincipal\b|\blead\b|\bdirector\b|\bhead\b|"
                r"\bmanager\b|\barchitect\b|\bvp\b|\bdistinguished\b|\bfellow\b", re.I)
# 只有工程岗进 ng/mid/sr 的分档 —— 设计/运营/市场的 entry level 对你没意义。
# AI lab / 初创常把工程岗叫 Member of Technical Staff, 不带 engineer 字样
ENG = re.compile(r"engineer|developer|\bswe\b|programmer|scientist, (ml|machine)|"
                 r"technical staff|\bmts\b", re.I)
# 「Member of Technical Staff」里的 staff 不是资历 —— 判 SR 前先抹掉, 否则 MTS 全算资深
MTS = re.compile(r"member of technical staff", re.I)


def fetch(url: str):
    req = urllib.request.Request(url, headers={"accept": "application/json",
                                               "user-agent": "jobs-board-scan/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def titles(slug: str) -> tuple[list[str], str]:
    """返回 (岗位标题列表, 命中的 board 地址)。两个 ATS 都试, 先中先用。"""
    for url in (f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                f"https://api.ashbyhq.com/posting-api/job-board/{slug}"):
        try:
            d = fetch(url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            continue
        jobs = d.get("jobs") or []
        if jobs:
            return [j.get("title", "") for j in jobs], url
    return [], ""


def classify(ts: list[str]) -> dict:
    eng = [t for t in ts if ENG.search(t)]
    senior = lambda t: SR.search(MTS.sub("", t))
    ng = [t for t in eng if NG.search(t) or (LEVEL_I.search(t) and not senior(t))]
    sr = [t for t in eng if t not in ng and senior(t)]
    return {"scan_n": len(ts), "scan_ng": len(ng),
            "scan_sr": len(sr), "scan_mid": len(eng) - len(ng) - len(sr)}


def guess_slug(name: str) -> str:
    """公司名 -> ATS slug 的常见写法。对不上就 --slug 手动给。"""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def apps() -> list:
    return json.load(urllib.request.urlopen(f"{API}/api/apps"))["apps"]


def put(app_id: str, body: dict):
    req = urllib.request.Request(f"{API}/api/apps/{app_id}", method="PUT",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def scan_one(a: dict, slug: str | None, dry: bool) -> dict | None:
    # 记过 board 地址就直接用, 省一次猜错的往返
    if a.get("board") and not slug:
        try:
            d = fetch(a["board"])
            ts, url = [j.get("title", "") for j in (d.get("jobs") or [])], a["board"]
        except Exception:
            ts, url = titles(slug or guess_slug(a["n"]))
    else:
        ts, url = titles(slug or guess_slug(a["n"]))

    if not url:
        print(f"  {a['n']:22} 板子没找到 —— 用 --slug 手动指定")
        return None

    r = classify(ts)
    eng = r["scan_ng"] + r["scan_mid"] + r["scan_sr"]
    flag = "  <- 有 entry 坑!" if r["scan_ng"] else ""
    print(f"  {a['n']:22} 共 {r['scan_n']:>3} · 工程 {eng:>3}  "
          f"ng {r['scan_ng']:>2}  mid {r['scan_mid']:>3}  sr {r['scan_sr']:>3}{flag}")
    if dry:
        return r
    put(a["id"], {**r, "board": url, "scan_at": date.today().isoformat()})
    return r


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = {x for x in sys.argv[1:] if x.startswith("--")}
    slug = None
    if "--slug" in sys.argv:
        i = sys.argv.index("--slug") + 1
        slug = sys.argv[i]
        # 按位置删, 不按值删 —— slug 和公司 id 同名时(preference-model)按值会把公司也删掉
        args = [x for j, x in enumerate(sys.argv[1:], 1) if j != i and not x.startswith("--")]
    dry = "--dry" in flags

    rows = apps()
    if "--all" in flags:
        targets = [a for a in rows if a.get("board")]
        print(f"扫 {len(targets)} 家已知 board 的公司"
              f"{' (dry run)' if dry else ''}\n")
    else:
        if not args:
            raise SystemExit(__doc__)
        want = {x.lower() for x in args}
        targets = [a for a in rows if a["id"].lower() in want or a["n"].lower() in want]
        if not targets:
            raise SystemExit(f"表里没有: {', '.join(args)}")
    for a in targets:
        scan_one(a, slug, dry)


if __name__ == "__main__":
    main()
