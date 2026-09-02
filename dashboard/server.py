#!/usr/bin/env python3
"""
LeetCode dashboard — 数据结构 x 算法范式 看板.

纯标准库(http.server + sqlite3),零 pip 安装.

真相源 : 每个题目文件夹里的 meta.json (git 可追踪)
索引层 : data.db  (SQLite, 由 /api/sync 从 meta.json 重建, gitignore)
笔记   : 题目文件夹里的 note.md / explain.md ... 直接读写磁盘

run:
    python dashboard/server.py
then open http://localhost:8765
"""
import json
import os
import re
import sqlite3
import sys
import threading
import time
from datetime import date
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

import fsrs              # FSRS-6 调度算法(见 dashboard/fsrs.py)
import scaffold          # 题号/题名 -> 建题目文件夹(见 dashboard/scaffold.py)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DB = HERE / "data.db"
STRUCT_DIR = REPO / "structures"   # per-data-structure trick docs (markdown)
PARADIGM_DIR = REPO / "paradigms"  # per-paradigm trick docs (双指针 / 贪心 / dp ...)
NOTES_DIR = REPO / "notes"         # cross-cutting notes, not tied to one problem
SCRATCH = "scratch.md"             # 随想收件箱: 速记先落这里, 想清楚了再挪走
PORT = 8765
REVIEW_LOG = HERE / "reviews.jsonl"   # 每次评分追加一行, git 追踪, 留给以后跑 FSRS 优化器
_REVIEW_LOCK = threading.Lock()       # ThreadingHTTPServer + meta.json 读改写 + 日志追加, 必须串行

FOLDER_RE = re.compile(r"^(\d+)\.\s*(.+)$")
# .md files that count as "the note" (first match wins), in priority order
NOTE_NAMES = ["note.md", "explain.md", "motivation.md", "obs1.md", "notes.md"]


# ---------------------------------------------------------------- scan / db ---
def scan_folders():
    """Yield (id, title, folder) for every '<num>. <title>' folder in the repo."""
    for p in sorted(REPO.iterdir()):
        if not p.is_dir():
            continue
        m = FOLDER_RE.match(p.name)
        if not m:
            continue
        yield int(m.group(1)), m.group(2).strip(), p.name


def read_meta(folder: str) -> dict:
    """Load meta.json for a folder, tolerating missing/broken files."""
    f = REPO / folder / "meta.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def write_meta(folder: str, meta: dict):
    """原子写: 复习模式下这个函数一天要跑几十次, 中途被打断不能留下半个 meta.json。"""
    f = REPO / folder / "meta.json"
    tmp = f.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, f)


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


# 列名在这里、在 sync() 的 COLUMNS 里各写一次, INSERT 用显式列名 ——
# 早先是 "INSERT INTO problems VALUES (?,?,...)" 的位置式写法, 加一列只要漏改一处,
# familiarity 就会悄悄挪进 status。别改回去。
SCHEMA = """CREATE TABLE problems(
    id INTEGER PRIMARY KEY,
    title TEXT, folder TEXT,
    structures TEXT, paradigms TEXT, techniques TEXT,
    difficulty TEXT, status TEXT,
    familiarity INTEGER,
    due TEXT, stability REAL, reps INTEGER, last_review TEXT, fsrs_state TEXT
)"""

COLUMNS = ("id", "title", "folder", "structures", "paradigms", "techniques",
           "difficulty", "status", "familiarity",
           "due", "stability", "reps", "last_review", "fsrs_state")


def init_db():
    """(Re)create the index table. Dropping first means schema changes need no migration."""
    with db() as con:
        con.execute("DROP TABLE IF EXISTS problems")
        con.execute(SCHEMA)


def sync():
    """Rebuild the SQLite index from folders + their meta.json."""
    init_db()
    rows = []
    for pid, title, folder in scan_folders():
        m = read_meta(folder)
        f = m.get("fsrs") or {}              # 没有这个 key = 还不是复习卡片
        rows.append(
            (
                pid,
                title,
                folder,
                json.dumps(m.get("structures", []), ensure_ascii=False),
                json.dumps(m.get("paradigms", []), ensure_ascii=False),
                json.dumps(m.get("techniques", []), ensure_ascii=False),
                m.get("difficulty", ""),
                m.get("status", "solved"),
                int(m.get("familiarity", 0) or 0),   # 0 = 未评级
                f.get("due", ""),                    # "" = 不是卡片, 前端靠这个判断
                float(f.get("stability") or 0),
                int(f.get("reps") or 0),
                f.get("last_review", ""),
                f.get("state", ""),
            )
        )
    cols = ",".join(COLUMNS)
    marks = ",".join("?" * len(COLUMNS))
    with db() as con:
        con.executemany(f"INSERT INTO problems ({cols}) VALUES ({marks})", rows)
    return len(rows)


def list_problems():
    with db() as con:
        out = []
        for r in con.execute("SELECT * FROM problems ORDER BY id"):
            d = dict(r)
            for k in ("structures", "paradigms", "techniques"):
                d[k] = json.loads(d[k] or "[]")
            out.append(d)
        return out


def get_detail(pid: int):
    with db() as con:
        r = con.execute("SELECT * FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    for k in ("structures", "paradigms", "techniques"):
        d[k] = json.loads(d[k] or "[]")
    folder = REPO / d["folder"]
    # all python solutions, sorted for stable tab order
    sols = []
    for f in sorted(folder.glob("*.py")):
        sols.append({"name": f.name, "content": f.read_text(encoding="utf-8", errors="replace")})
    d["solutions"] = sols
    # LeetCode 题面(dashboard/fetch_desc.py 抓的), 没抓过就是空串
    desc = folder / "problem.html"
    d["description"] = desc.read_text(encoding="utf-8", errors="replace") if desc.exists() else ""
    # the note file (existing preferred name, else default note.md)
    note_file = None
    for name in NOTE_NAMES:
        if (folder / name).exists():
            note_file = name
            break
    if note_file is None:
        note_file = "note.md"
    nf = folder / note_file
    d["note_file"] = note_file
    d["note"] = nf.read_text(encoding="utf-8", errors="replace") if nf.exists() else ""
    # 复习界面要的东西随详情一起给, 省一次请求; 静态导出也就自动带上了
    card = read_meta(d["folder"]).get("fsrs") or fsrs.new_card()
    d["fsrs"] = card
    d["fsrs_preview"] = fsrs.preview(card, today_str())   # {"1":1,"2":1,"3":2,"4":8} 天
    return d


def save_note(pid: int, content: str):
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return False
    folder = REPO / r["folder"]
    note_file = next((n for n in NOTE_NAMES if (folder / n).exists()), "note.md")
    (folder / note_file).write_text(content, encoding="utf-8")
    return True


SOL_NAME_RE = re.compile(r"^[\w\u4e00-\u9fff\-. ]+\.py$")


def sol_path(folder: Path, name: str) -> Path | None:
    """解析一个解法文件名。带路径成分的、非 .py 的一律拒绝(不悄悄改名)，同 note_path。"""
    if name != Path(name).name or not SOL_NAME_RE.match(name):
        return None
    return folder / name


def save_solution(pid: int, name: str, content: str) -> bool:
    """新建或覆盖题目文件夹里的一个 .py 解法。"""
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return False
    f = sol_path(REPO / r["folder"], name)
    if f is None:
        return False
    f.write_text(content, encoding="utf-8")
    return True


def struct_slug(name: str) -> str:
    """Filesystem-safe slug for a data-structure name (keeps unicode letters)."""
    s = re.sub(r"[^\w\-]+", "-", name.strip()).strip("-")
    return s or "unnamed"


DOC_DIRS = {"structures": STRUCT_DIR, "paradigms": PARADIGM_DIR}


def get_doc(kind: str, name: str) -> dict | None:
    """通用 trick 文档: kind = structures | paradigms"""
    d = DOC_DIRS.get(kind)
    if d is None:
        return None
    slug = struct_slug(name)
    f = d / (slug + ".md")
    content = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
    return {"kind": kind, "name": name, "file": f"{kind}/{slug}.md", "content": content}


def save_doc(kind: str, name: str, content: str) -> bool:
    d = DOC_DIRS.get(kind)
    if d is None:
        return False
    d.mkdir(exist_ok=True)
    (d / (struct_slug(name) + ".md")).write_text(content, encoding="utf-8")
    return True


# --------------------------------------------------------------- notes ----
NOTE_NAME_RE = re.compile(r"^[\w\u4e00-\u9fff\-. ]+\.md$")


def note_path(name: str) -> Path | None:
    """Resolve a notes/ filename. 带路径成分的一律拒绝, 而不是悄悄改名成 basename。"""
    if name != Path(name).name or not NOTE_NAME_RE.match(name):
        return None
    return NOTES_DIR / name


def list_notes() -> list:
    if not NOTES_DIR.exists():
        return []
    out = []
    for f in sorted(NOTES_DIR.glob("*.md")):
        head = ""
        try:                                    # 拿第一行标题当摘要, 读一点就够
            with f.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.strip():
                        head = line.strip().lstrip("# ").strip()
                        break
        except OSError:
            pass
        out.append({"file": f.name, "head": head[:80], "size": f.stat().st_size,
                    "mtime": int(f.stat().st_mtime)})
    out.sort(key=lambda n: -n["mtime"])          # 最近改过的排前面
    return out


def get_note(name: str) -> dict | None:
    f = note_path(name)
    if f is None:
        return None
    return {"file": f.name,
            "content": f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""}


def save_note_file(name: str, content: str) -> bool:
    f = note_path(name)
    if f is None:
        return False
    NOTES_DIR.mkdir(exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return True


def append_scratch(text: str) -> dict:
    """随想速记: 追加一条带日期的条目到 notes/scratch.md。"""
    text = text.strip()
    if not text:
        return {"ok": False}
    NOTES_DIR.mkdir(exist_ok=True)
    f = NOTES_DIR / SCRATCH
    stamp = time.strftime("%Y-%m-%d %H:%M")
    body = f.read_text(encoding="utf-8", errors="replace") if f.exists() else "# 随想\n"
    if not body.endswith("\n"):
        body += "\n"
    f.write_text(f"{body}\n## {stamp}\n\n{text}\n", encoding="utf-8")
    return {"ok": True, "file": SCRATCH}


def save_meta(pid: int, payload: dict):
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return False
    folder = r["folder"]
    meta = read_meta(folder)
    for k in ("structures", "paradigms", "techniques", "difficulty", "status"):
        if k in payload:
            meta[k] = payload[k]
    if "familiarity" in payload:
        meta["familiarity"] = int(payload["familiarity"] or 0)
    write_meta(folder, meta)
    sync()  # cheap for small repos; keeps index consistent
    return True


# ------------------------------------------------------------------ 复习 ------
def today_str() -> str:
    """本地日期。前端用 toLocaleDateString('sv') 得到同样的格式, 两边都是本地时区。"""
    return time.strftime("%Y-%m-%d")


def append_review_log(entry: dict):
    """追加一行评分记录。

    ⚠️ entry 里的 state/stability/difficulty 是**评分前**的值 —— FSRS 优化器要的就是
    "当时是什么状态、给了什么评分", 记成评分后的值会让以后跑出来的参数悄悄失真。
    """
    with REVIEW_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def review_card(pid: int, rating: int):
    """评一次分: 更新 meta.json 的 fsrs 字段 + 追加日志 + 重建索引。整段串行。"""
    with _REVIEW_LOCK:
        with db() as con:
            r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
        if not r:
            return None
        folder = r["folder"]
        meta = read_meta(folder)
        before = meta.get("fsrs") or fsrs.new_card()
        today = today_str()
        card, interval = fsrs.review(before, rating, today)

        meta["fsrs"] = card
        write_meta(folder, meta)

        last = before.get("last_review") or ""
        append_review_log({
            "ts": int(time.time()),
            "date": today,
            "id": pid,
            "rating": rating,
            # --- 评分前的状态 ---
            "state": before.get("state", "new"),
            "elapsed_days": (
                (date.fromisoformat(today) - date.fromisoformat(last)).days if last else None
            ),
            "stability": before.get("stability"),
            "difficulty": before.get("difficulty"),
            # --- 评分后 ---
            "new_stability": card["stability"],
            "new_difficulty": card["difficulty"],
            "interval": interval,
            "due": card["due"],
        })
        sync()
        return {"ok": True, "id": pid, "interval": interval, "due": card["due"],
                "card": card, "preview": fsrs.preview(card, today)}


def reset_card(pid: int) -> bool:
    """退回成非卡片(删掉 meta 里的 fsrs)。日志不动 —— 那是历史, 不该被抹。"""
    with _REVIEW_LOCK:
        with db() as con:
            r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
        if not r:
            return False
        meta = read_meta(r["folder"])
        if "fsrs" in meta:
            del meta["fsrs"]
            write_meta(r["folder"], meta)
            sync()
        return True


def read_lists() -> dict:
    """题单定义(Blind 75 等), 纯静态数据。进度由前端拿 /api/problems 现算, 这里不重复一份状态。"""
    f = HERE / "lists.json"
    if not f.exists():
        return {"lists": {}, "premium": []}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"lists": {}, "premium": []}


# ------------------------------------------------------------------- http ----
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body_json(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self._send(200, (HERE / "index.html").read_text(encoding="utf-8"), "text/html; charset=utf-8")
        if path == "/app.js":
            return self._send(200, (HERE / "app.js").read_text(encoding="utf-8"), "text/javascript; charset=utf-8")
        if path == "/styles.css":
            return self._send(200, (HERE / "styles.css").read_text(encoding="utf-8"), "text/css; charset=utf-8")
        if path == "/api/problems":
            return self._send(200, list_problems())
        if path == "/api/lists":
            return self._send(200, read_lists())
        if path == "/api/notes":
            return self._send(200, list_notes())
        m = re.match(r"^/api/notes/(.+)$", path)
        if m:
            n = get_note(unquote(m.group(1)))
            return self._send(200, n) if n else self._send(400, {"error": "bad name"})
        m = re.match(r"^/api/problems/(\d+)$", path)
        if m:
            d = get_detail(int(m.group(1)))
            return self._send(200, d) if d else self._send(404, {"error": "not found"})
        m = re.match(r"^/api/(structures|paradigms)/(.+)$", path)
        if m:
            d = get_doc(m.group(1), unquote(m.group(2)))
            return self._send(200, d) if d else self._send(404, {"error": "bad kind"})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/sync":
            return self._send(200, {"synced": sync()})
        if path == "/api/scratch":
            return self._send(200, append_scratch(self._body_json().get("text", "")))
        m = re.match(r"^/api/review/(\d+)$", path)
        if m:
            pid = int(m.group(1))
            body = self._body_json()
            if body.get("op") == "reset":
                return self._send(200, {"ok": reset_card(pid)})
            try:
                rating = int(body.get("rating", 0))
            except (TypeError, ValueError):
                rating = 0
            if rating not in (1, 2, 3, 4):
                return self._send(400, {"ok": False, "error": "rating 必须是 1..4"})
            res = review_card(pid, rating)
            return self._send(200, res) if res else self._send(404, {"ok": False, "error": "not found"})
        if path == "/api/problems":
            # 给题号或题名, 拉题面 + 建空 sol.py/note.md, 然后立刻进索引表
            try:
                r = scaffold.create_problem(self._body_json().get("query", ""))
            except scaffold.ScaffoldError as e:
                return self._send(400, {"ok": False, "error": str(e)})
            if r.get("created"):
                sync()
            return self._send(200, r)
        self._send(404, {"error": "not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        m = re.match(r"^/api/problems/(\d+)/note$", path)
        if m:
            ok = save_note(int(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/solutions/(.+)$", path)
        if m:
            ok = save_solution(int(m.group(1)), unquote(m.group(2)),
                               self._body_json().get("content", ""))
            return self._send(200 if ok else 400, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/meta$", path)
        if m:
            ok = save_meta(int(m.group(1)), self._body_json())
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/(structures|paradigms)/(.+)$", path)
        if m:
            ok = save_doc(m.group(1), unquote(m.group(2)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/notes/(.+)$", path)
        if m:
            ok = save_note_file(unquote(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 400, {"ok": ok})
        self._send(404, {"error": "not found"})

    def log_message(self, *a):  # quieter console
        pass


def main():
    n = sync()
    print(f"indexed {n} problems -> {DB.name}")
    print(f"serving  http://localhost:{PORT}   (Ctrl+C to stop)")
    try:
        ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
        sys.exit(0)


if __name__ == "__main__":
    main()
