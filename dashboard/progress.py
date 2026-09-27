#!/usr/bin/env python3
"""
进度 tracker —— 覆盖和掌握分开看。

为什么单独一个脚本, 不读 data.db:
data.db 是 /api/sync 重建出来的索引层, server 没跑、或者刚手改过 meta.json 还没 sync 的时候
它就是旧的。这个脚本直接扫各题文件夹的 meta.json(真相源), 所以随时能跑, 不用先开看板。

两条线, 只看一条就会误判:

    覆盖   摸过多少题       -> 第一层 90%, 看着该开新题了
    掌握   多少题到了 S2    -> 第一层 64%, 看着还早

两个数一起看才知道第一层卡在哪: 不是没题做, 是二十道 L3–L4 的欠账没还。

    欠账 = 摸过但没到 L2 的题数 (familiarity > 2, 即 L3 / L3.5 / L4)

欠账涨 = 在囤题, 欠账掉 = 在消化。**不设阈值** —— 开不开新题当场自己判断, 这个脚本只报数。

口径(跟 plan.json 的 stages 一致):

    没建   plan 里有这道题, 本地连文件夹都没有
    见过   建了文件夹(题面抓到本地了), familiarity 还是空的 —— 阶梯的地板
    摸过   有 familiarity, 不管是 L0 还是 L4
    S2     familiarity <= 2 (L0–L2, 含 L1.5) —— OA 门槛
    欠账   摸过 - S2

会员题(lists.json 的 premium)单独摘出来报, 不算进"该做还没做"。
它们做不掉, 混在缺口里每次看都像背着一笔还不了的债。

run:
    python dashboard/progress.py           三层汇总 + 按组明细 + 题单覆盖
    python dashboard/progress.py --debt    再列出每一道欠账题(按组, 带 L 几)
    python dashboard/progress.py --todo    再列出没建文件夹的题(按组)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PLAN = HERE / "plan.json"
LISTS = HERE / "lists.json"

S2_MAX = 2.0          # familiarity <= 2 算 S2 达标(L0–L2, 含 L1.5)
BAR = 22              # 进度条宽度


# ---------------------------------------------------------------- 读真相源

def load_meta():
    """扫 repo 下的题目文件夹, 返回 {题号: familiarity 或 None}。

    文件夹名形如 "56. Merge Intervals"。建了文件夹但 meta.json 缺失/坏了/没写
    familiarity 的, 一律记 None —— 也就是"见过"这一档, 地板。
    """
    out = {}
    for d in REPO.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"^(\d+)\.\s", d.name)
        if not m:
            continue
        fam = None
        f = d / "meta.json"
        if f.exists():
            try:
                fam = json.loads(f.read_text()).get("familiarity")
            except (json.JSONDecodeError, OSError):
                pass
        out[int(m.group(1))] = None if fam in (None, "") else float(fam)
    return out


def state(pid, meta):
    """一道题落在哪一档。四档互斥, 加起来就是题数。"""
    if pid not in meta:
        return "absent"
    fam = meta[pid]
    if fam is None:
        return "seen"
    return "s2" if fam <= S2_MAX else "debt"


def tally(ids, meta, premium):
    """一组题的五个数。absent 里的会员题拆出来单独算。"""
    c = Counter(state(i, meta) for i in ids)
    gone = [i for i in ids if state(i, meta) == "absent" and i in premium]
    return {
        "n": len(ids),
        "seen": len(ids) - c["absent"],      # 见过 = 建了文件夹的, 含已摸过的
        "touched": c["s2"] + c["debt"],
        "s2": c["s2"],
        "debt": c["debt"],
        "absent": c["absent"] - len(gone),   # 没建, 且做得了
        "premium": len(gone),
    }


# ---------------------------------------------------------------- 排版

def w(s):
    """显示宽度, 中日韩字符按两格算 —— 不然中文表头对不齐。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def pad(s, n, right=False):
    s = str(s)
    fill = " " * max(0, n - w(s))
    return fill + s if right else s + fill


def pct(a, b):
    return f"{round(100 * a / b):>3d}%" if b else "  -"


def bar(a, b, width=BAR):
    filled = round(width * a / b) if b else 0
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------- 各块输出

HEAD = (pad("", 10) + pad("共", 5, True) + pad("见过", 7, True) + pad("摸过", 7, True)
        + pad("S2", 6, True) + pad("", 7) + pad("欠账", 7, True) + pad("没建", 7, True))


def row(label, t, width=10):
    line = (pad(label, width) + pad(t["n"], 5, True) + pad(t["seen"], 7, True)
            + pad(t["touched"], 7, True) + pad(t["s2"], 6, True)
            + pad(f" ({pct(t['s2'], t['n'])})", 7)
            + pad(t["debt"], 7, True) + pad(t["absent"], 7, True))
    if t["premium"]:
        line += f"  +{t['premium']} 会员"
    return line


def tiers(groups, meta, premium):
    print("NeetCode 150 · 覆盖 x 掌握")
    print()
    print(HEAD)
    names = {1: "第一层", 2: "第二层", 3: "第三层"}
    every = []
    for t in (1, 2, 3):
        ids = [p[0] for g in groups if g["tier"] == t for p in g["problems"]]
        every += ids
        print(row(names[t], tally(ids, meta, premium)))
    print("─" * w(HEAD))
    print(row("合计", tally(every, meta, premium)))


def by_group(groups, meta, premium):
    print()
    print("按组 (条形 = S2 占比)")
    names = {1: "第一层", 2: "第二层", 3: "第三层"}
    for t in (1, 2, 3):
        print()
        print(f"  {names[t]}")
        for g in sorted((g for g in groups if g["tier"] == t),
                        key=lambda g: -tally([p[0] for p in g["problems"]], meta, premium)["s2"]):
            ids = [p[0] for p in g["problems"]]
            s = tally(ids, meta, premium)
            tail = []
            if s["debt"]:
                tail.append(f"欠 {s['debt']}")
            if s["absent"]:
                tail.append(f"没建 {s['absent']}")
            if s["premium"]:
                tail.append(f"会员 {s['premium']}")
            frac = "{}/{}".format(s["s2"], s["n"])
            print(f"    {pad(g['name'], 26)}{bar(s['s2'], s['n'])} "
                  f"{pad(frac, 7, True)}   {' · '.join(tail)}")


def by_list(lists, meta, premium):
    print()
    print("题单覆盖")
    print()
    for name, spec in lists.items():
        ids = [it[0] for items in spec["categories"].values() for it in items]
        s = tally(ids, meta, premium)
        extra = f"   会员 {s['premium']}" if s["premium"] else ""
        frac = "{}/{}".format(s["s2"], s["n"])
        print(f"  {pad(name, 20)}{bar(s['s2'], s['n'])} "
              f"{pad(frac, 8, True)} ({pct(s['s2'], s['n'])})"
              f"   欠 {s['debt']}   没建 {s['absent']}{extra}")


LABEL = {3.0: "L3", 3.5: "L3.5", 4.0: "L4"}


def debts(groups, meta):
    """欠账清单。按组出, 因为同组连着还账比打散快。"""
    print()
    print("欠账明细 (摸过但没到 L2)")
    for g in groups:
        rows = [(p[0], p[1], meta[p[0]]) for p in g["problems"]
                if state(p[0], meta) == "debt"]
        if not rows:
            continue
        print()
        print(f"  {g['name']}  (第{g['tier']}层)")
        for pid, title, fam in sorted(rows, key=lambda r: -r[2]):
            print(f"    {pad(LABEL.get(fam, fam), 5)}{pad(pid, 5, True)}  {title}")


def todos(groups, meta, premium):
    print()
    print("没建文件夹的题")
    for g in groups:
        rows = [(p[0], p[1], p[2]) for p in g["problems"]
                if state(p[0], meta) == "absent"]
        if not rows:
            continue
        print()
        print(f"  {g['name']}  (第{g['tier']}层)")
        for pid, title, diff in rows:
            mark = "  · 会员" if pid in premium else ""
            print(f"    {pad(pid, 5, True)}  {pad(title, 46)}{pad(diff, 7)}{mark}")


# ---------------------------------------------------------------- main

def main():
    plan = json.loads(PLAN.read_text())
    lists = json.loads(LISTS.read_text())
    premium = set(lists["premium"])
    meta = load_meta()
    groups = plan["groups"]

    print()
    tiers(groups, meta, premium)
    by_group(groups, meta, premium)
    by_list(lists["lists"], meta, premium)
    if "--debt" in sys.argv:
        debts(groups, meta)
    if "--todo" in sys.argv:
        todos(groups, meta, premium)
    print()


if __name__ == "__main__":
    main()
