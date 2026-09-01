#!/usr/bin/env python3
"""
给一个题号或题名, 把一道新题落到磁盘上:

    <编号>. <标题>/
      problem.html   ← LeetCode 题面(抓不到就不写, 例如会员题)
      sol.py         ← 空文件, 等着写
      note.md        ← 只有一行标题
      meta.json      ← status: todo, difficulty 来自 LeetCode, 标签留空

看板的 📋 TODO 加一条时会调这里(POST /api/problems), 建完 server 再 sync() 一次,
题目就出现在「未完全打标签」区。命令行也能直接用:

    python dashboard/scaffold.py 105
    python dashboard/scaffold.py "word break"

题号 -> slug 没法硬推, 所以拿 leetcode.com/api/problems/all/ 那份全量清单来查,
存成 .lc_index.json 缓存一周; 题名则先按 slug 直接查 GraphQL, 查不到再回清单里模糊找。
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from fetch_desc import FOLDER_RE, fetch, problem_html, slugify

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INDEX_CACHE = HERE / ".lc_index.json"
INDEX_URL = "https://leetcode.com/api/problems/all/"
INDEX_TTL = 7 * 24 * 3600
LEVELS = {1: "easy", 2: "medium", 3: "hard"}
BAD_TITLE_CHARS = re.compile(r"[/\\:*?\"<>|]")


class ScaffoldError(Exception):
    """能直接甩给用户看的失败原因(网络挂了、题号不存在、题名有歧义……)。"""


# ------------------------------------------------------------------ 清单 ----
def load_index(force: bool = False) -> list[dict]:
    """[{id, title, slug, difficulty, paid}], 全量题目清单, 缓存一周。"""
    if not force and INDEX_CACHE.exists() and time.time() - INDEX_CACHE.stat().st_mtime < INDEX_TTL:
        try:
            return json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass                                  # 缓存坏了就当没有, 重抓
    req = urllib.request.Request(
        INDEX_URL, headers={"User-Agent": "Mozilla/5.0 (leetcode-dashboard local script)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = json.loads(r.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        if INDEX_CACHE.exists():                  # 拿过期缓存兜底, 总比直接失败强
            try:
                return json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        raise ScaffoldError(f"拿不到 LeetCode 题目清单: {e}") from e

    out = []
    for pair in raw.get("stat_status_pairs", []):
        st = pair.get("stat", {})
        try:
            pid = int(st.get("frontend_question_id"))
        except (TypeError, ValueError):
            continue
        out.append({
            "id": pid,
            "title": st.get("question__title") or "",
            "slug": st.get("question__title_slug") or "",
            "difficulty": LEVELS.get(pair.get("difficulty", {}).get("level"), ""),
            "paid": bool(pair.get("paid_only")),
        })
    out.sort(key=lambda q: q["id"])
    INDEX_CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


# ------------------------------------------------------------------ 解析 ----
def find_folder(pid: int) -> str | None:
    """仓库里已经有这个编号的文件夹了吗(标题写法可能和 LeetCode 不一样)。"""
    for p in sorted(REPO.iterdir()):
        m = FOLDER_RE.match(p.name) if p.is_dir() else None
        if m and int(m.group(1)) == pid:
            return p.name
    return None


def resolve(query: str) -> dict:
    """'105' / 'word break' / 'Word Break' -> 清单里的那一条 {id,title,slug,...}。"""
    q = (query or "").strip()
    if not q:
        raise ScaffoldError("给个题号或题名")

    if q.isdigit():
        pid = int(q)
        hit = next((r for r in load_index() if r["id"] == pid), None)
        if not hit:
            raise ScaffoldError(f"清单里没有第 {pid} 题")
        return hit

    # 题名: 先赌 slug 推得对, 一次 GraphQL 就够, 不用下载整份清单
    slug = slugify(q)
    try:
        got = fetch(slug)
    except (urllib.error.URLError, TimeoutError) as e:
        raise ScaffoldError(f"网络失败: {e}") from e
    if got:
        return {"id": int(got["questionFrontendId"]), "title": got["title"], "slug": slug,
                "difficulty": (got.get("difficulty") or "").lower(), "paid": False, "q": got}

    low = q.lower()
    rows = load_index()
    exact = [r for r in rows if r["title"].lower() == low]
    hits = exact or [r for r in rows if low in r["title"].lower()]
    if not hits:
        raise ScaffoldError(f"找不到题目: {q}")
    if len(hits) > 1:
        names = ", ".join(f"{r['id']} {r['title']}" for r in hits[:5])
        raise ScaffoldError(f"「{q}」对上了 {len(hits)} 道题, 说具体点或直接给题号: {names}")
    return hits[0]


# ------------------------------------------------------------------ 建盘 ----
def create_problem(query: str) -> dict:
    """解析 -> 抓题面 -> 建文件夹。已经有的题原样返回, 一个字节都不改。"""
    row = resolve(query)
    pid, slug = row["id"], row["slug"]

    exist = find_folder(pid)
    if exist:
        return {"ok": True, "created": False, "id": pid,
                "title": FOLDER_RE.match(exist).group(2).strip(), "folder": exist}

    q = row.get("q")
    if q is None and slug:
        try:
            q = fetch(slug)
        except (urllib.error.URLError, TimeoutError):
            q = None                              # 题面抓不到不算致命, 文件夹照建
    title = (q or row).get("title") or row["title"]
    difficulty = ((q or {}).get("difficulty") or row.get("difficulty") or "").lower()
    if q and int(q["questionFrontendId"]) != pid:  # slug 推错了, 宁可不建也别建错
        raise ScaffoldError(f"slug {slug} 抓回来的是 #{q['questionFrontendId']}, 不是 #{pid}")

    safe = BAD_TITLE_CHARS.sub("-", title).strip()
    folder = REPO / f"{pid}. {safe}"
    folder.mkdir()
    if q and q.get("content"):
        (folder / "problem.html").write_text(problem_html(slug, q), encoding="utf-8")
    (folder / "sol.py").write_text("", encoding="utf-8")
    (folder / "note.md").write_text(f"# {pid}. {title}\n", encoding="utf-8")
    (folder / "meta.json").write_text(json.dumps({
        "structures": [], "paradigms": [], "techniques": [],
        "difficulty": difficulty, "status": "todo", "familiarity": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {"ok": True, "created": True, "id": pid, "title": title, "folder": folder.name,
            "difficulty": difficulty,
            "description": bool(q and q.get("content")),
            "note": "" if (q and q.get("content")) else "题面没抓到(会员题或网络问题), 文件夹已建好"}


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[0])
        print("用法: python dashboard/scaffold.py <题号或题名> [...]")
        return 2
    bad = 0
    for arg in argv:
        try:
            r = create_problem(arg)
        except ScaffoldError as e:
            print(f"  !! {arg}: {e}")
            bad += 1
            continue
        print(f"  {'建好' if r['created'] else '已有'}  {r['folder']}"
              + (f"   ({r['note']})" if r.get("note") else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
