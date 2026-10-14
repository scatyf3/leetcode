#!/usr/bin/env python3
"""从 git 历史回填 edits.jsonl —— 时间轴的左半截。

edits.jsonl 是 2026-09-06 才开始记的, 在那之前"哪天把哪道题从 L4 提到 L2"只散落在
commit 里, 而且粒度是"一个 commit 一堆题"。这个脚本把每个碰过 meta.json 的 commit
当成一个时间点, diff 出相邻两个 commit 之间每道题的字段变化, 补成日志行。

    python dashboard/backfill_edits.py          # 看看会写什么(不落盘)
    python dashboard/backfill_edits.py --write  # 真写

回填出来的行带 "src": "git" + commit 短 sha。**可以反复跑**: 每次都把已有的
src=git 行整段丢掉重算, 只保留服务器实时写的那些, 所以不会越跑越多。

两处口径要留神:
- 时间戳用的是 **commit 时间**, 不是"你其实是那天下午改的"。粒度到天就够画图了。
- `explained` 是 2026-09-05 那天短命的一个布尔位(见 commit 999ff44), 后来被收成
  熟练度阶梯顶端的 L0。回填时按 L0 折算, 否则那两天的曲线会凭空少一档。
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
EDIT_LOG = HERE / "edits.jsonl"

FOLDER_RE = re.compile(r"^(\d+)\. .+/meta\.json$")
LIST_FIELDS = ("structures", "paradigms", "techniques")
SCALAR_FIELDS = ("difficulty", "status", "familiarity")


def git(*args: str) -> str:
    # stderr 也收进来: 老 commit 里没有 plan.json 是**预期内**的(has_l0 拿它当"那会儿
    # 还没有 L0 这一档"的信号), 别让 git 的 fatal: 刷屏, 看着像出事了
    return subprocess.run(("git", *args), cwd=REPO, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding="utf-8", errors="replace").stdout


def commits() -> list:
    """碰过任何 meta.json 的 commit, 从老到新。"""
    out = git("log", "--reverse", "--format=%H\t%ct", "--", "*/meta.json")
    rows = []
    for line in out.splitlines():
        if line.strip():
            sha, ts = line.split("\t")
            rows.append((sha, int(ts)))
    return rows


def snapshot(sha: str) -> dict:
    """这个 commit 的树里, 每道题的 meta.json 长什么样 -> {id: meta}。

    一个 commit 几十个 blob, 逐个 `git show` 在 Windows 上慢得离谱, 所以先 ls-tree
    拿到 (sha, path), 再用一次 cat-file --batch 把内容整批读回来。
    """
    files = []
    for line in git("ls-tree", "-r", sha).splitlines():
        info, _, path = line.partition("\t")
        m = FOLDER_RE.match(path)
        if m:
            files.append((info.split()[2], int(m.group(1))))
    if not files:
        return {}

    # 必须走 bytes: header 里的 size 是**字节数**, meta.json 里全是中文,
    # 按字符切会一路错位。
    proc = subprocess.run(("git", "cat-file", "--batch"), cwd=REPO, check=True,
                          input=("\n".join(b for b, _ in files) + "\n").encode(),
                          stdout=subprocess.PIPE)
    out, pos, snap = proc.stdout, 0, {}
    for _, pid in files:
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].split()[2])
        body = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1               # 跳过内容后面那个换行
        try:
            snap[pid] = json.loads(body.decode("utf-8", "replace"))
        except json.JSONDecodeError:
            snap[pid] = {}
    return snap


def has_l0(sha: str) -> bool:
    """这个 commit 的阶梯上有没有 L0 这一档(看它自己的 plan.json, 不硬编码 sha)。

    要紧的是 `familiarity: 0` 在不同年代意思不一样: L0「英语讲得清」是 2026-09-05
    (commit 999ff44) 才加的档, 在那之前落在 meta.json 里的 0 是个没含义的空值 ——
    999ff44 顺手把它们清成了缺键。照字面读成"讲得清"的话, 时间轴上会凭空冒出几道
    S3 然后又消失, 看着像退步, 其实什么都没发生。
    """
    try:
        plan = json.loads(git("show", f"{sha}:dashboard/plan.json"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return False
    return any(r.get("l") == 0 for r in plan.get("familiarity") or [])


def fam_of(meta: dict, l0: bool):
    """熟练度, 缺键 = 未评 -> None。

    `explained: true` 是老口径的 S3(见 999ff44), 在现在的阶梯里就是 L0。
    """
    if meta.get("explained"):
        return 0
    v = meta.get("familiarity")
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f == 0 and not l0:
        return None                # 那会儿还没有 L0 这一档, 0 就是没评
    return int(f) if f.is_integer() else f


def diff_rows(pid: int, old: dict, new: dict, ts: int, date: str, sha: str,
              l0: tuple) -> list:
    rows = []

    def row(**kw):
        rows.append({"ts": ts, "date": date, "id": pid, **kw,
                     "src": "git", "commit": sha[:7]})

    if old is None:            # 这个 commit 里新出现的题
        row(field="exists", **{"from": None, "to": True})
    elif new is None:          # 文件夹被删了/改名了
        row(field="exists", **{"from": True, "to": None})
        return rows

    o, n = old or {}, new or {}
    for k in LIST_FIELDS:
        a, b = list(o.get(k) or []), list(n.get(k) or [])
        if a != b:
            row(field=k, added=[x for x in b if x not in a],
                removed=[x for x in a if x not in b])
    for k in SCALAR_FIELDS:
        a = fam_of(o, l0[0]) if k == "familiarity" else o.get(k)
        b = fam_of(n, l0[1]) if k == "familiarity" else n.get(k)
        if a != b:
            row(field=k, **{"from": a, "to": b})
    return rows


def backfill() -> list:
    rows, prev, prev_l0 = [], {}, False
    for sha, ts in commits():
        cur, cur_l0 = snapshot(sha), has_l0(sha)
        date = time.strftime("%Y-%m-%d", time.localtime(ts))
        for pid in sorted(set(prev) | set(cur)):
            rows += diff_rows(pid, prev.get(pid), cur.get(pid), ts, date, sha,
                              (prev_l0, cur_l0))
        prev, prev_l0 = cur, cur_l0
    return rows


def merge(rows: list) -> list:
    """git 行整段重算, 服务器实时写的那些原样留着, 一起按时间排。"""
    live = []
    if EDIT_LOG.exists():
        for line in EDIT_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(e, dict) and e.get("src") != "git":
                live.append(e)
    return sorted(rows + live, key=lambda e: (e.get("ts") or 0))


def main():
    rows = backfill()
    merged = merge(rows)
    write = "--write" in sys.argv
    print(f"从 git 回填 {len(rows)} 行 (共 {len(commits())} 个 commit), "
          f"合并实时日志后 {len(merged)} 行")
    by_day = {}
    for e in rows:
        by_day[e["date"]] = by_day.get(e["date"], 0) + 1
    for d in sorted(by_day):
        print(f"  {d}  {by_day[d]:>4} 行")
    if not write:
        print("\n(没有 --write, 什么都没落盘。上面几行是预览)")
        for e in rows[:5]:
            print("  " + json.dumps(e, ensure_ascii=False))
        return
    with EDIT_LOG.open("w", encoding="utf-8") as f:
        for e in merged:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"已写 {EDIT_LOG}")


if __name__ == "__main__":
    main()
