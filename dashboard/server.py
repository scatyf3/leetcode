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
import re
import sqlite3
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DB = HERE / "data.db"
STRUCT_DIR = REPO / "structures"   # per-data-structure trick docs (markdown)
PORT = 8765

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
    (REPO / folder / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS problems(
                id INTEGER PRIMARY KEY,
                title TEXT, folder TEXT,
                structures TEXT, paradigms TEXT, techniques TEXT,
                difficulty TEXT, status TEXT
            )"""
        )


def sync():
    """Rebuild the SQLite index from folders + their meta.json."""
    init_db()
    rows = []
    for pid, title, folder in scan_folders():
        m = read_meta(folder)
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
            )
        )
    with db() as con:
        con.execute("DELETE FROM problems")
        con.executemany(
            "INSERT INTO problems VALUES (?,?,?,?,?,?,?,?)", rows
        )
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


def struct_slug(name: str) -> str:
    """Filesystem-safe slug for a data-structure name (keeps unicode letters)."""
    s = re.sub(r"[^\w\-]+", "-", name.strip()).strip("-")
    return s or "unnamed"


def get_struct(name: str) -> dict:
    slug = struct_slug(name)
    f = STRUCT_DIR / (slug + ".md")
    content = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
    return {"name": name, "file": slug + ".md", "content": content}


def save_struct(name: str, content: str) -> bool:
    STRUCT_DIR.mkdir(exist_ok=True)
    (STRUCT_DIR / (struct_slug(name) + ".md")).write_text(content, encoding="utf-8")
    return True


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
    write_meta(folder, meta)
    sync()  # cheap for small repos; keeps index consistent
    return True


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
        m = re.match(r"^/api/problems/(\d+)$", path)
        if m:
            d = get_detail(int(m.group(1)))
            return self._send(200, d) if d else self._send(404, {"error": "not found"})
        m = re.match(r"^/api/structures/(.+)$", path)
        if m:
            return self._send(200, get_struct(unquote(m.group(1))))
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path == "/api/sync":
            return self._send(200, {"synced": sync()})
        self._send(404, {"error": "not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        m = re.match(r"^/api/problems/(\d+)/note$", path)
        if m:
            ok = save_note(int(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/meta$", path)
        if m:
            ok = save_meta(int(m.group(1)), self._body_json())
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/structures/(.+)$", path)
        if m:
            ok = save_struct(unquote(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
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
