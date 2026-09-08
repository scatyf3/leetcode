#!/usr/bin/env python3
"""
LeetCode dashboard — 数据结构 x 算法范式 看板.

纯标准库(http.server + sqlite3),零 pip 安装.

真相源 : 每个题目文件夹里的 meta.json (git 可追踪)
索引层 : data.db  (SQLite, 由 /api/sync 从 meta.json 重建, gitignore)
笔记   : 题目文件夹里的 note.md / explain.md ... 直接读写磁盘

第二个视图「坐标系」(覆盖 x 深度) 的分层和时间线在 dashboard/plan.json (手改, git 追踪).
掌握度不另存: S1/S2/S3 全部由 meta.json 的 familiarity (L0..L4, 含半档 L1.5) 算出来.
一个字段一条阶梯, 不会出现 "L2 但标了 S1" 这种自相矛盾的状态.

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
import syntax            # 第二个牌组: 语法卡(见 dashboard/syntax.py)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DB = HERE / "data.db"
STRUCT_DIR = REPO / "structures"   # per-data-structure trick docs (markdown)
PLAN = HERE / "plan.json"          # coverage x depth curriculum (hand-edited)
PARADIGM_DIR = REPO / "paradigms"  # per-paradigm trick docs (双指针 / 贪心 / dp ...)
NOTES_DIR = REPO / "notes"         # cross-cutting notes, not tied to one problem
SCRATCH = "scratch.md"             # 随想收件箱: 速记先落这里, 想清楚了再挪走
PORT = 8765
REVIEW_LOG = HERE / "reviews.jsonl"   # 每次评分追加一行, git 追踪, 留给以后跑 FSRS 优化器
EDIT_LOG = HERE / "edits.jsonl"       # 每次改标签/难度/状态追加一行, git 追踪, 留给以后画"标签什么时候长出来的"
ATTEMPT_LOG = HERE / "attempts.jsonl"  # 每次「做了一遍」打卡追加一行, git 追踪, 日课/配速的复习那半边靠它
SESSION_FILE = HERE / "session.json"  # 当前这轮复习的队列快照, **易失状态**, 不进 git
_REVIEW_LOCK = threading.Lock()       # ThreadingHTTPServer + meta.json 读改写 + 日志追加, 必须串行
VENDOR_FILES = ("/vendor/vue.global.prod.js", "/vendor/marked.min.js")

FOLDER_RE = re.compile(r"^(\d+)\.\s*(.+)$")
# .md files that count as "the note" (first match wins), in priority order
NOTE_NAMES = ["note.md", "explain.md", "motivation.md", "obs1.md", "notes.md"]
ANSWER_FILE = "answer.md"   # 复习用的答案卡: 一句话思路, 和 note.md 的流水账分开


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


def fam_level(meta: dict):
    """熟练度 0..4 (0 = L0 英语讲得清, 4 = 完全不会), 缺键 = 还没评 -> None.

    别写成 `int(meta.get("familiarity", 0) or 0)` —— 0 现在是阶梯**顶端**,
    那样会把所有没评过的题静默算成最熟的一档。

    也别用 int() 转: 阶梯允许半档(L1.5), int(1.5) == 1 会把它悄悄升成 L1。
    """
    v = meta.get("familiarity")
    if v is None or v == "":
        return None
    try:
        return fam_num(v)
    except (TypeError, ValueError):
        return None


def fam_num(v):
    """档位数值化: 整数档回 int, 半档(L1.5)回 float —— 写回 meta.json 时
    1 就还是 1 而不是 1.0, 那个文件是手写手读的, 别给它塞小数点。"""
    f = float(v)
    return int(f) if f.is_integer() else f


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
    familiarity REAL, complexity TEXT,   -- REAL: 阶梯有半档(L1.5)
    due TEXT, stability REAL, reps INTEGER, last_review TEXT, fsrs_state TEXT
)"""

COLUMNS = ("id", "title", "folder", "structures", "paradigms", "techniques",
           "difficulty", "status", "familiarity", "complexity",
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
                fam_level(m),                        # 0..4, None = 还没评(缺键)
                json.dumps(m.get("complexity") or {}, ensure_ascii=False),
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


def _unpack(row):
    d = dict(row)
    for k in ("structures", "paradigms", "techniques"):
        d[k] = json.loads(d[k] or "[]")
    d["complexity"] = json.loads(d["complexity"] or "{}")
    # familiarity 列是 REAL(阶梯有半档), 于是整数档读回来是 2.0 —— 收敛回 2,
    # 否则 API 和静态站导出的 JSON 里整数档全带个小数点。
    if d.get("familiarity") is not None:
        d["familiarity"] = fam_num(d["familiarity"])
    return d


def list_problems():
    with db() as con:
        return [_unpack(r) for r in con.execute("SELECT * FROM problems ORDER BY id")]


def get_detail(pid: int):
    with db() as con:
        r = con.execute("SELECT * FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    d = _unpack(r)
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
    m = read_meta(d["folder"])
    # 答案卡: 自然语言思路。和 note.md 分开 —— note 是随手记的过程, 这个是压缩过的结论
    af = folder / ANSWER_FILE
    d["answer"] = af.read_text(encoding="utf-8", errors="replace") if af.exists() else ""
    # 选择题: 正确的一句话思路 + 3 个"这道题上似是而非"的干扰项(手写在 meta.json 里)
    d["quiz"] = m.get("quiz") or {}
    card = m.get("fsrs") or fsrs.new_card()
    d["fsrs"] = card
    d["fsrs_preview"] = fsrs.preview(card, today_str())   # {"1":1,"2":1,"3":2,"4":8} 天
    # 现在打卡会记进哪一半。**判据只写在服务端一处**(attempt_state), 前端照抄这个字段就行 ——
    # 在 JS 里重算一遍迟早会和这边分叉, 而按钮上的预告和真正落盘的那一笔必须是同一个答案。
    d["attempt_next"] = attempt_state(d["id"], d.get("familiarity"))
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


def save_answer(pid: int, content: str) -> bool:
    """写复习答案卡(answer.md)。空内容 = 删掉这个文件, 别留个空壳。"""
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return False
    f = REPO / r["folder"] / ANSWER_FILE
    if content.strip():
        f.write_text(content, encoding="utf-8")
    elif f.exists():
        f.unlink()
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


LOGGED_FIELDS = ("structures", "paradigms", "techniques", "difficulty", "status", "familiarity")
LIST_FIELDS = ("structures", "paradigms", "techniques")


def append_edit_log(pid: int, before: dict, after: dict):
    """把这次保存**真正改动**的字段追加成日志行, 一个字段一行。

    meta.json 是覆盖写的, 改完就没了"上一版长什么样" —— git 里那点粒度是
    "一个 commit 一堆题", 重建不出"哪天给哪道题加了 two-pointer"。这里补的就是那条时间轴。

    只记变化: 前端每次都 PATCH 全量字段, 不 diff 的话每保存一次就多几行噪音。
    """
    ts, date = int(time.time()), today_str()
    rows = []
    for k in LOGGED_FIELDS:
        old, cur = before.get(k), after.get(k)
        if old == cur:
            continue
        if k in LIST_FIELDS:
            o, c = list(old or []), list(cur or [])
            rows.append({"ts": ts, "date": date, "id": pid, "field": k,
                         "added": [x for x in c if x not in o],
                         "removed": [x for x in o if x not in c]})
        else:
            rows.append({"ts": ts, "date": date, "id": pid, "field": k,
                         "from": old, "to": cur})
    write_edit_rows(rows)


def write_edit_rows(rows: list):
    if not rows:
        return
    with EDIT_LOG.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def log_problem_created(pid: int):
    """新建题目文件夹也记一行。

    时间轴上"未做 → 进了库"那一步全靠它 —— 没有这行的话, 一道题要等到第一次被打标签
    才会从"未做"里消失, 中间那段"建了但还没碰"就看不见了。
    """
    write_edit_rows([{"ts": int(time.time()), "date": today_str(), "id": pid,
                      "field": "exists", "from": None, "to": True}])


# ---------------------------------------------------- 做题打卡 (attempts) ---
# 为什么要单开一份日志: edits.jsonl 只记**升降档**, 于是"重做一遍 L4 但没升上去"在全库
# 没有任何痕迹。日课要是继续从它算, 唯一的得分方式就是让 familiarity 变好看 —— 挑软柿子、
# 把自己评高, 而真正该做的重做因为"不出成绩"反而被系统惩罚。这份日志记的是**动作**:
# 哪天动手做了哪道题、当时是什么档。效果一概不参与。

def folder_born(pid: int):
    """这道题的文件夹是哪天建的 —— edits.jsonl 里那条 exists: null -> true 的日期。

    按写入顺序取**第一条**(backfill_edits.py 从 git 回填的那截也在里面)。
    找不到就是 None: 日志开写之前就存在的老题, 一律当"很久以前就有了"。
    """
    for e in read_edits():
        if e.get("id") == pid and e.get("field") == "exists" and e.get("to"):
            return e.get("date")
    return None


def attempt_state(pid: int, fam) -> dict:
    """这一笔算哪半边。**先问"以前碰过没有", 再看档位** —— 顺序不能反。

    只看档位会漏一个大洞: 今天点 + 建文件夹、做了一遍、发现完全不会评成 L4, 再打卡 ——
    档位是 4, 于是被算成"复习重做"。新题就这么洗成了复习, reward hack 只是换了个地方。

    反过来"有没有文件夹"也不能单独当判据: 📋 TODO 会**提前**把空文件夹建出来(把题加进
    todo.md 那一刻就建了), 那些题有文件夹、没评档、也确实还没做过, 它们才是真正的新题。

    所以判据是**以前碰过没有**, 文件夹的生日只是它的一个信号:
      new  = 之前没打过卡, 且(从没评过档 或 文件夹是今天才建的)
      redo = 碰过 + 打卡时 L3 / L3.5 / L4
      warm = 其余(打卡时 L0–L2), 记一行但不占额度
    """
    today = today_str()
    seen = any(a.get("id") == pid and a.get("date", "") < today for a in read_attempts())
    born = folder_born(pid)
    first = (not seen) and (fam is None or born == today)
    if first:
        kind = "new"
    elif fam is not None and fam >= 3:
        kind = "redo"
    else:
        kind = "warm"
    return {"kind": kind, "first": first, "born": born, "seen": seen, "fam": fam}


def read_attempts() -> list:
    """attempts.jsonl 全部行: 哪天做了哪道题。"""
    return read_jsonl(ATTEMPT_LOG)


def log_attempt(pid: int, undo: bool = False) -> dict:
    """打一次卡, 或撤销今天这道题的那次。

    **一天一题最多一条** —— 同一道题反复点不该刷出额度, 重复打卡直接返回已有的那条。
    撤销会真的把今天那行删掉(整份重写): 这是留给手滑的, 只能删当天当题这一条,
    历史日期的记录碰不到。
    """
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return {"ok": False, "error": "没这道题"}
    today = today_str()
    with _REVIEW_LOCK:   # 和评分/存 meta 同一把锁: 都是"读整个文件 -> 改 -> 写回"
        rows = read_attempts()
        mine = [a for a in rows if a.get("id") == pid and a.get("date") == today]
        if undo:
            if mine:
                keep = [a for a in rows
                        if not (a.get("id") == pid and a.get("date") == today)]
                tmp = ATTEMPT_LOG.with_suffix(".jsonl.tmp")
                tmp.write_text("".join(json.dumps(a, ensure_ascii=False) + "\n" for a in keep),
                               encoding="utf-8")
                os.replace(tmp, ATTEMPT_LOG)
            return {"ok": True, "logged": False, "kind": None}
        if mine:
            return {"ok": True, "logged": True, "dup": True,
                    "kind": mine[0].get("kind"), "fam": mine[0].get("fam")}
        fam = fam_level(read_meta(r["folder"]))
        st = attempt_state(pid, fam)
        # born/seen 一起写进去: 日后想复盘"这一笔当初凭什么算成新题"不用再猜
        row = {"ts": int(time.time()), "date": today, "id": pid,
               "kind": st["kind"], "fam": fam, "born": st["born"], "seen": st["seen"]}
        with ATTEMPT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "logged": True, "kind": row["kind"], "fam": fam}


def save_meta(pid: int, payload: dict):
    with db() as con:
        r = con.execute("SELECT folder FROM problems WHERE id=?", (pid,)).fetchone()
    if not r:
        return False
    folder = r["folder"]
    with _REVIEW_LOCK:   # meta.json 读改写 + 日志追加, 和评分那条路一样必须串行
        meta = read_meta(folder)
        before = {k: meta.get(k) for k in LOGGED_FIELDS}
        for k in ("structures", "paradigms", "techniques", "difficulty", "status", "complexity", "quiz"):
            if k in payload:
                meta[k] = payload[k]
        if "familiarity" in payload:
            # 0 是 L0(英语讲得清), 不是"未评" —— 未评就是没有这个键
            v = payload["familiarity"]
            if v is None or v == "":
                meta.pop("familiarity", None)
            else:
                meta["familiarity"] = fam_num(v)
        write_meta(folder, meta)
        append_edit_log(pid, before, meta)
        sync()  # cheap for small repos; keeps index consistent
    return True


# -------------------------------------------------- plan / progress (grid) ---
def read_plan() -> dict:
    """The coverage x depth curriculum. Hand-edited, so tolerate a broken save."""
    try:
        return json.loads(PLAN.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"error": f"plan.json 读不出来: {e}", "groups": [], "tiers": [],
                "stages": [], "phases": [], "targets": []}


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


def _label(pid, titles: dict) -> dict:
    # 语法卡的 id 本身就是 "主题/标题", 已经自带人话了, 查不到就用它自己
    return {"id": pid, "title": titles.get(pid) or (pid if isinstance(pid, str) else "?")}


def write_session(body: dict) -> dict:
    """把前端这一轮复习的队列快照落盘(覆盖写)。

    这是**易失状态, 不是数据源** —— 关掉面板它就没意义了, 所以不进 git、不参与调度、
    也没有任何东西会去读它做决定。存它只有一个目的: 让浏览器外面(比如我)能看见
    "现在队列长什么样、哪几道被押到队尾了"。前端每次动队列就覆盖一次。
    """
    with db() as con:
        titles = {r["id"]: r["title"] for r in con.execute("SELECT id, title FROM problems")}

    # 题目牌组的 id 是整数, 语法卡的是 "主题/标题" 字符串。别无脑 int() ——
    # 那样整个语法队列会被静默丢光, 快照看着像"队列是空的"。
    deck = body.get("deck") if body.get("deck") in ("problems", "syntax") else "problems"

    def one_id(x):
        if deck == "syntax":
            return x if isinstance(x, str) and x else None
        try:
            return int(x)
        except (TypeError, ValueError):
            return None

    def ids(key, cap=500):
        return [i for i in (one_id(x) for x in (body.get(key) or [])[:cap]) if i is not None]

    cur = one_id(body.get("current"))

    snap = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "open": bool(body.get("open")),
        "deck": deck,
        "mode": body.get("mode") if body.get("mode") in ("fsrs", "order", "random") else "?",
        "done": int(body.get("done") or 0),
        "total": int(body.get("total") or 0),
        "current": _label(cur, titles) if cur is not None else None,
        "queue": [_label(i, titles) for i in ids("queue")],
        # 押到队尾的记录, 按发生顺序, 同一道押两次就出现两次
        "deferred": [_label(i, titles) for i in ids("deferred")],
    }
    SESSION_FILE.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True}


def read_session() -> dict:
    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"open": False, "queue": [], "deferred": [], "note": "还没有过复习会话"}


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


# ------------------------------------------------------- 语法卡组(第二牌组) ---
# 内容和调度都在 syntax.py, 这里只负责"加锁"和"翻译成 HTTP" —— 和题目牌组共用
# 同一把 _REVIEW_LOCK, 因为两边都会往 reviews.jsonl 追行。

def syntax_list() -> dict:
    return syntax.list_cards(today_str())


def syntax_review(cid: str, rating: int):
    with _REVIEW_LOCK:
        return syntax.review_card(cid, rating, today_str())


def syntax_reset(cid: str) -> bool:
    with _REVIEW_LOCK:
        return syntax.reset_card(cid)


def syntax_save_back(cid: str, content: str) -> bool:
    with _REVIEW_LOCK:
        return syntax.save_back(cid, content)


def read_jsonl(path: Path) -> list:
    """把一个只追加的日志整个读出来。

    坏行(写了一半/手改坏了)直接跳过而不是报错 —— 一行读不动不该让整页图表打不开。
    返回的每条都是当初写进去的那个 dict 原样。
    """
    if not path.exists():
        return []
    out = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(e, dict) and e.get("date"):
                    out.append(e)
    except OSError:
        return []
    return out


def read_reviews() -> list:
    """reviews.jsonl 全部行, 给 📈 进度用。"""
    return read_jsonl(REVIEW_LOG)


def read_edits() -> list:
    """edits.jsonl 全部行: 标签/难度/状态的改动时间轴。"""
    return read_jsonl(EDIT_LOG)


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
        # 本地开发站, 一切都现读磁盘。不给缓存留余地 —— 否则浏览器可能拿旧的
        # index.html 配新的 app.js, 前端引用一个还不存在的元素就整页起不来。
        self.send_header("Cache-Control", "no-store")
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
        # 复习面板用的 Vue + 文档渲染用的 marked, 都存在仓库里不走 CDN(见 README「为什么不用构建」)。
        # 白名单, 不做目录遍历 —— 这个 server 只在本地跑, 但也没必要开个读文件的口子。
        # 往 vendor/ 里加文件时**这里也要加一行**, 否则浏览器拿到 404:
        # app.js 的 md() 会退化成纯文本(整篇 markdown 原样显示), 看起来像"渲染坏了"。
        if path in VENDOR_FILES:
            return self._send(200, (HERE / "vendor" / path.split("/")[-1]).read_text(encoding="utf-8"),
                              "text/javascript; charset=utf-8")
        if path == "/api/problems":
            return self._send(200, list_problems())
        if path == "/api/plan":
            return self._send(200, read_plan())
        if path == "/api/lists":
            return self._send(200, read_lists())
        if path == "/api/review/session":
            return self._send(200, read_session())
        if path == "/api/syntax":
            return self._send(200, syntax_list())
        if path == "/api/reviews":
            return self._send(200, {"reviews": read_reviews()})
        if path == "/api/edits":
            return self._send(200, {"edits": read_edits()})
        if path == "/api/attempts":
            return self._send(200, {"attempts": read_attempts()})
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
        if path == "/api/attempts":
            # 「做了一遍」打卡。op=undo 撤销今天这道题的那一次(手滑用)。
            body = self._body_json()
            try:
                pid = int(body.get("id"))
            except (TypeError, ValueError):
                return self._send(400, {"ok": False, "error": "缺 id"})
            return self._send(200, log_attempt(pid, body.get("op") == "undo"))
        if path == "/api/scratch":
            return self._send(200, append_scratch(self._body_json().get("text", "")))
        if path == "/api/review/session":
            return self._send(200, write_session(self._body_json()))
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
        if path == "/api/syntax/review":
            # 语法卡的 id 是 "主题/标题"(带中文和空格), 塞不进 URL 路径, 所以走 body
            body = self._body_json()
            cid = str(body.get("id") or "")
            if not cid:
                return self._send(400, {"ok": False, "error": "缺 id"})
            if body.get("op") == "reset":
                return self._send(200, {"ok": syntax_reset(cid)})
            try:
                rating = int(body.get("rating", 0))
            except (TypeError, ValueError):
                rating = 0
            if rating not in (1, 2, 3, 4):
                return self._send(400, {"ok": False, "error": "rating 必须是 1..4"})
            res = syntax_review(cid, rating)
            return self._send(200, res) if res else self._send(404, {"ok": False, "error": "没这张卡"})
        if path == "/api/problems":
            # 给题号或题名, 拉题面 + 建空 sol.py/note.md, 然后立刻进索引表
            try:
                r = scaffold.create_problem(self._body_json().get("query", ""))
            except scaffold.ScaffoldError as e:
                return self._send(400, {"ok": False, "error": str(e)})
            if r.get("created"):
                with _REVIEW_LOCK:
                    log_problem_created(int(r["id"]))
                sync()
            return self._send(200, r)
        self._send(404, {"error": "not found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        if path == "/api/syntax/card":
            body = self._body_json()
            ok = syntax_save_back(str(body.get("id") or ""), body.get("content", ""))
            return self._send(200 if ok else 400, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/note$", path)
        if m:
            ok = save_note(int(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/solutions/(.+)$", path)
        if m:
            ok = save_solution(int(m.group(1)), unquote(m.group(2)),
                               self._body_json().get("content", ""))
            return self._send(200 if ok else 400, {"ok": ok})
        m = re.match(r"^/api/problems/(\d+)/answer$", path)
        if m:
            ok = save_answer(int(m.group(1)), self._body_json().get("content", ""))
            return self._send(200 if ok else 404, {"ok": ok})
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
