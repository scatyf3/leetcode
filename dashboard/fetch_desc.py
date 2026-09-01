#!/usr/bin/env python3
"""
把 LeetCode 的题面抓下来存到每题文件夹里的 problem.html。

只用标准库。抓一次就存盘, 之后面板离线可读; 默认跳过已存在的文件。

    python dashboard/fetch_desc.py            # 只抓缺的
    python dashboard/fetch_desc.py --force    # 全部重抓
    python dashboard/fetch_desc.py 417 33     # 只抓这几题

slug 由文件夹名推出来 ("417. Pacific Atlantic Water Flow" -> pacific-atlantic-water-flow),
抓回来后拿 questionFrontendId 和文件夹编号对一遍, 对不上就报错而不是写坏文件。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
API = "https://leetcode.com/graphql"
QUERY = """query q($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionFrontendId title difficulty content
    topicTags { name }
  }
}"""
FOLDER_RE = re.compile(r"^(\d+)\.\s*(.+)$")


def slugify(title: str) -> str:
    """'Best Time to Buy and Sell Stock II' -> 'best-time-to-buy-and-sell-stock-ii'"""
    s = title.lower().replace("'", "").replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def problem_html(slug: str, q: dict) -> str:
    """题面存盘的格式: 一行来源注释 + LeetCode 原始 HTML。"""
    tags = ", ".join(t["name"] for t in (q.get("topicTags") or []))
    return (f"<!-- leetcode.com/problems/{slug}/  ·  {q['difficulty']}"
            f"{'  ·  ' + tags if tags else ''} -->\n{q['content']}")


def fetch(slug: str) -> dict | None:
    body = json.dumps({"query": QUERY, "variables": {"titleSlug": slug}}).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (leetcode-dashboard local script)"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read()).get("data", {}).get("question")


def main(argv):
    force = "--force" in argv
    only = {int(a) for a in argv if a.isdigit()}

    todo = []
    for p in sorted(REPO.iterdir()):
        m = FOLDER_RE.match(p.name) if p.is_dir() else None
        if not m:
            continue
        pid, title = int(m.group(1)), m.group(2).strip()
        if only and pid not in only:
            continue
        if (p / "problem.html").exists() and not force:
            continue
        todo.append((pid, title, p))

    if not todo:
        print("没有要抓的 (加 --force 可以全部重抓)")
        return 0

    ok = bad = 0
    for pid, title, folder in todo:
        slug = slugify(title)
        try:
            q = fetch(slug)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  !! {pid:>4} 网络失败 {slug}: {e}")
            bad += 1
            continue
        if not q:
            print(f"  !! {pid:>4} 查无此题, slug 可能推错了: {slug}")
            bad += 1
            continue
        if int(q["questionFrontendId"]) != pid:
            print(f"  !! {pid:>4} 抓回来的是 #{q['questionFrontendId']} ({slug}), 跳过不写")
            bad += 1
            continue
        (folder / "problem.html").write_text(problem_html(slug, q), encoding="utf-8")
        print(f"  {pid:>4}  {q['difficulty']:<6} {len(q['content']):>6}B  {slug}")
        ok += 1
        time.sleep(0.4)          # 别把人家的接口打疼

    print(f"\n抓到 {ok} 题" + (f", 失败 {bad} 题(见上面的 !!)" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
