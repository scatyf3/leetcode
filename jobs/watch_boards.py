#!/usr/bin/env python3
"""
扫 pool 里各家公司的招聘板, 只报**新出现的 entry level / new grad 岗**。

    python3 jobs/watch_boards.py --discover     # 猜并记下每家的 board 地址(第一次跑)
    python3 jobs/watch_boards.py                # 扫一遍, 打印新增
    python3 jobs/watch_boards.py --write        # 顺便把 ng 标记写回看板
    python3 jobs/watch_boards.py --entry        # 连 entry 桶一起看(很吵)

为什么要这个: **各家的 new grad 窗口不同步**。Airbnb 的 new grad 岗是 2026 年
3–4 月发的, 到 9 月已经下架, 板上只剩 Staff 起步; 而大厂 SDE 的秋招坑 9–10 月才开。
按一个统一窗口去排必然系统性错过一批。一天扫一次, 谁什么时候开都接得住。

只用标准库。Greenhouse 和 Ashby 的 job board 都有公开 JSON API, 不需要 key:

    https://boards-api.greenhouse.io/v1/boards/<slug>/jobs
    https://api.ashbyhq.com/posting-api/job-board/<slug>
    https://api.lever.co/v0/postings/<slug>?mode=json
    https://<tenant>.<wd>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs   (POST)

Workday 的 tenant/site 猜不出来, 只能手查一次填进去, 格式:
    workday:nvidia.wd5.NVIDIAExternalCareerSite
它也不返回全量, 得按关键词搜 —— 所以对 Workday 只搜 new grad 那几个词, entry 桶放弃。

抓不到的多半是自建站或 Workday(Uber / Snap / Atlassian / 各家中国区都是), 只能手查,
或者在详情弹窗的「招聘板」里手填。

状态存在 jobs/data/boards.json(已 gitignore), 结构:

    {"<公司 id>": {"kind": "greenhouse", "slug": "airbnb",
                   "jobs": {"<岗位 id>": {"title","url","bucket","first_seen","last_seen"}}}}

`first_seen` 是这个脚本第一次看到它的日期 —— 攒几个月就有了一张「谁什么时候开坑」的表,
这正是排 timeline 需要而聚合站给不了的东西。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
APPS = DATA / "applications.json"
STATE = DATA / "boards.json"
UA = {"User-Agent": "Mozilla/5.0 (jobs-board-watch)"}
PAUSE = 0.7                      # 对方是免费公开接口, 别打太快

# ── 岗位过滤 ────────────────────────────────────────────────────────────
# 明说是 new grad 的
NG = re.compile(r"new ?grad|new college grad|\bncg\b|university grad|campus hire|"
                r"early career|entry[- ]level|graduate program|graduate talent|"
                r"grad(?:uate)? 20\d\d|校招|应届", re.I)
# 工程岗
ENG = re.compile(r"software engineer|machine learning engineer|ml engineer|"
                 r"data engineer|systems? engineer|infrastructure engineer|"
                 r"platform engineer|performance engineer|research engineer", re.I)
# 资深前缀 —— 带这些的对 new grad 没意义
SENIOR = re.compile(r"\b(senior|staff|principal|lead|director|manager|head of|"
                    r"sr\.?|iii|iv|architect|distinguished|fellow)\b", re.I)
# 方向不对的
OFFTOPIC = re.compile(r"\bsre\b|on-?call|production support|audiovisual|"
                      r"sales|recruit|counsel|marketing|designer", re.I)
# 技术岗。ng 桶要额外过这一关 —— 不然「Customer Experience Associate (New Grad)」
# 这种也会混进来, 它确实是 new grad, 但不是你要的
TECH = re.compile(r"engineer|technical staff|scientist|developer|architect", re.I)


def bucket(title: str) -> str | None:
    """岗位归到哪一桶。

    'ng'    标题明说 new grad / 校招 / early career, **且**是技术岗 —— 只有这一桶值得报。
    'entry' 工程岗但不带资深前缀。**信号很弱**: 实测 731 条, OpenAI 一家就 169 条,
            那只是它们常规岗位的命名习惯, 不代表招应届。所以默认不报, 只记数,
            要看加 --entry。
    """
    if OFFTOPIC.search(title):
        return None
    if NG.search(title):
        # 非技术的 new grad 岗单独记一桶。它本身没用, 但**它的存在是个信号**:
        # 说明这家的应届通道是活的, 只是工程坑还没放出来 —— 那正是快要开的那批。
        return "ng" if TECH.search(title) else "ng_other"
    if ENG.search(title) and not SENIOR.search(title):
        return "entry"
    return None


# ── 抓板子 ──────────────────────────────────────────────────────────────
def get_json(url: str, tries: int = 2):
    """偶发超时不该让一整家掉队 —— 重试一次再放弃。"""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except (TimeoutError, urllib.error.URLError) as e:
            if i == tries - 1 or isinstance(e, urllib.error.HTTPError):
                raise
            time.sleep(2)


def parse_board(v: str) -> tuple[str, str] | None:
    """board 字段容忍两种写法: "greenhouse:airbnb", 或者直接粘一整条 API URL。

    手填的时候从浏览器地址栏拷过来是最顺手的, 不该因为格式不对就静默失败。
    """
    v = (v or "").strip()
    if not v or v == "-":
        return None
    m = re.search(r"boards-api\.greenhouse\.io/v1/boards/([^/?]+)", v)
    if m:
        return "greenhouse", m.group(1)
    m = re.search(r"ashbyhq\.com/posting-api/job-board/([^/?]+)", v)
    if m:
        return "ashby", m.group(1)
    m = re.search(r"api\.lever\.co/v0/postings/([^/?]+)", v)
    if m:
        return "lever", m.group(1)
    m = re.search(r"([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:wday/cxs/[^/]+/|en-US/)([^/?]+)", v)
    if m:
        return "workday", f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    kind, _, slug = v.partition(":")
    return (kind, slug) if slug and kind in ("greenhouse", "ashby", "lever", "workday") else None


def fetch(kind: str, slug: str) -> list[dict]:
    """统一成 [{id, title, loc, url}]。两家的字段名不一样, 在这里抹平。"""
    if kind == "greenhouse":
        d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
        return [{"id": str(j["id"]), "title": j["title"],
                 "loc": (j.get("location") or {}).get("name", ""),
                 "url": j.get("absolute_url", "")} for j in d.get("jobs", [])]
    if kind == "ashby":
        d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
        return [{"id": str(j.get("id")), "title": j.get("title", ""),
                 "loc": j.get("location", ""),
                 "url": j.get("jobUrl", "")} for j in d.get("jobs", [])]
    if kind == "workday":
        # tenant.wdN.site。它是 POST + 分页 + 只能搜, 拿不到全量, 所以只搜应届那几个词。
        tenant, wd, site = slug.split(".", 2)
        url = f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        base = f"https://{tenant}.{wd}.myworkdayjobs.com/en-US/{site}"
        out, seen_p = [], set()
        for term in ("new college graduate", "new grad", "university graduate", "early career"):
            body = json.dumps({"appliedFacets": {}, "limit": 20, "offset": 0,
                               "searchText": term}).encode()
            try:
                req = urllib.request.Request(
                    url, data=body, method="POST",
                    headers={**UA, "Content-Type": "application/json",
                             "accept": "application/json"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    d = json.loads(r.read().decode())
            except Exception:
                continue
            for j in d.get("jobPostings", []):
                path = j.get("externalPath", "")
                if path and path not in seen_p:
                    seen_p.add(path)
                    out.append({"id": path.rsplit("_", 1)[-1] or path,
                                "title": j.get("title", ""),
                                "loc": j.get("locationsText", ""),
                                "url": base + path})
            time.sleep(PAUSE)
        return out
    if kind == "lever":
        d = get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        return [{"id": str(j.get("id")), "title": j.get("text", ""),
                 "loc": (j.get("categories") or {}).get("location", ""),
                 "url": j.get("hostedUrl", "")} for j in d]
    raise ValueError(kind)


def slug_candidates(name: str):
    # 括号里往往才是法人名, 也往往才是 slug —— "Cursor (Anysphere)" 的板子在 anysphere
    paren = [re.sub(r"[^a-z0-9]", "", m.lower()) for m in re.findall(r"\((.*?)\)", name)]
    base = re.sub(r"\(.*?\)", "", name).strip().lower()
    base = re.sub(r"\b(inc|llc|ltd|labs?|ai|中国)\b", "", base).strip()
    compact = re.sub(r"[^a-z0-9]", "", base)
    dashed = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    first = compact[:len(re.sub(r"[^a-z0-9]", "", base.split()[0]))] if base.split() else compact
    out = []
    for s in (compact, dashed, first, *paren, re.sub(r"[^a-z0-9]", "", name.lower())):
        if s and s not in out:
            out.append(s)
    return out


def discover(name: str) -> str | None:
    """猜 board 地址。命中一个就停 —— 公司名到 slug 多数是直白映射。"""
    for slug in slug_candidates(name):
        for kind in ("greenhouse", "ashby", "lever"):
            try:
                jobs = fetch(kind, slug)
            except (urllib.error.HTTPError, urllib.error.URLError,
                    json.JSONDecodeError, TimeoutError):
                jobs = None
            time.sleep(PAUSE)
            if jobs:                       # 空板子不算命中, 可能是猜错了 slug
                return f"{kind}:{slug}"
    return None


# ── 读写 ────────────────────────────────────────────────────────────────
def load_apps() -> list:
    return json.loads(APPS.read_text(encoding="utf-8")).get("apps", [])


def save_apps(apps: list) -> None:
    d = json.loads(APPS.read_text(encoding="utf-8"))
    d["apps"] = apps
    APPS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save_state(st: dict) -> None:
    DATA.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


# ── 两个动作 ────────────────────────────────────────────────────────────
def cmd_discover(apps: list) -> None:
    todo = [a for a in apps if not a.get("board")]
    print(f"给 {len(todo)} 家找 board 地址(每家最多试几个 slug, 会慢)…\n")
    found = 0
    for a in todo:
        b = discover(a["n"])
        if b:
            a["board"] = b
            found += 1
            print(f"  ✓ {a['n']:24} {b}")
        else:
            a["board"] = "-"           # 标成试过了, 下次 --discover 不再重试
            print(f"  · {a['n']:24} 没找到(自建站或别的 ATS, 手填 board 字段)")
    save_apps(apps)
    print(f"\n找到 {found} / {len(todo)} 家。手填格式: greenhouse:<slug> 或 ashby:<slug>")


def cmd_scan(apps: list, write: bool, show_entry: bool = False) -> None:
    st = load_state()
    today = date.today().isoformat()
    watched = [a for a in apps if parse_board(a.get("board", ""))]
    print(f"扫 {len(watched)} 家…\n")

    new_rows, ng_now, errs = [], set(), []
    for a in watched:
        kind, slug = parse_board(a["board"])
        a["board"] = f"{kind}:{slug}"          # 顺手把手填的 URL 规范化回来
        try:
            jobs = fetch(kind, slug)
        except Exception as e:                      # 一家挂了不该让整轮停
            errs.append(f"{a['n']}: {type(e).__name__}")
            continue
        time.sleep(PAUSE)

        rec = st.setdefault(a["id"], {"kind": kind, "slug": slug, "jobs": {}})
        seen = rec["jobs"]
        live = set()
        for j in jobs:
            b = bucket(j["title"])
            if not b:
                continue
            live.add(j["id"])
            if j["id"] in seen:
                seen[j["id"]]["last_seen"] = today
            else:
                seen[j["id"]] = {"title": j["title"], "url": j["url"], "loc": j["loc"],
                                 "bucket": b, "first_seen": today, "last_seen": today}
                new_rows.append((a, seen[j["id"]]))
        # 公司的 ng 标记只看 ng 桶 —— entry 桶太松, 标了等于没标
        if any(seen[i]["bucket"] == "ng" for i in live):
            ng_now.add(a["id"])
        rec["total"] = len(jobs)
        rec["checked"] = today

    save_state(st)

    show = [r for r in new_rows if show_entry or r[1]["bucket"] == "ng"]
    hidden = len(new_rows) - len(show)
    if show:
        print(f"── 新增 {len(show)} 个 ──")
        for a, j in sorted(show, key=lambda x: (x[1]["bucket"] != "ng", x[0]["n"])):
            tag = "NG " if j["bucket"] == "ng" else "   "
            print(f"  {tag}[{a['tier']}] {a['n']}  ·  {j['loc']}")
            print(f"      {j['title']}")
            print(f"      {j['url']}")
    else:
        print("没有新增的 new grad 岗。")
    if hidden:
        print(f"\n(另有 {hidden} 个 entry 桶的没显示 —— 那个桶信号很弱, 要看加 --entry)")

    # 应届通道活着但工程岗还没放的 —— 这批最值得盯, 因为坑就快开了
    soon = []
    for a in watched:
        rec = st.get(a["id"], {})
        js = rec.get("jobs", {}).values()
        if any(j["bucket"] == "ng_other" for j in js) and not any(j["bucket"] == "ng" for j in js):
            soon.append(a)
    if soon:
        print(f"\n── 应届通道活着, 但工程岗还没放({len(soon)} 家)——盯这批 ──")
        for a in soon:
            titles = [j["title"] for j in st[a["id"]]["jobs"].values() if j["bucket"] == "ng_other"]
            print(f"  [{a['tier']}] {a['n']}  ·  在招的是: {titles[0][:44]}")

    if errs:
        print(f"\n拉不到 {len(errs)} 家: {', '.join(errs[:6])}")

    save_apps(apps)                            # board 字段可能被规范化过
    if write:
        changed = 0
        for a in apps:
            v = 1 if a["id"] in ng_now else 0
            if a.get("ng", 0) != v:
                a["ng"] = v
                changed += 1
        save_apps(apps)
        print(f"\n写回看板: {len(ng_now)} 家当前有 new grad 岗, 改了 {changed} 家的 ng 标记。")
        print("注意 server 缓存: 看板刷新即可, 不用重启。")


def main() -> None:
    if not APPS.exists():
        raise SystemExit("先跑一次 jobs/server.py 把 applications.json 建出来")
    apps = load_apps()
    if "--discover" in sys.argv:
        cmd_discover(apps)
    else:
        cmd_scan(apps, "--write" in sys.argv, "--entry" in sys.argv)


if __name__ == "__main__":
    main()
