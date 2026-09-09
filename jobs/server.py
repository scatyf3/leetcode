#!/usr/bin/env python3
"""
求职看板 —— 本地服务端。纯标准库, 零依赖。

    python jobs/server.py            # http://localhost:8766

真相分两半, 因为**这个仓库是 public 的**:

    jobs/plan.json               ← 方法论 + 候选池。git 追踪, 会上 Pages, 手改即改计划
    jobs/data/applications.json  ← 你的投递状态。**已 gitignore, 永不出仓库**
    jobs/data/events.jsonl       ← 每次状态流转追加一行, 同样 gitignore

第一次跑会把 plan.json 的 pool 铺成 applications.json(全部 status=pool)。
之后往 plan.json 的 pool 里加公司, 下次启动会自动补进来, 不会覆盖你已有的状态。

注意 (和 dashboard/server.py 同一个坑): **后端不热重载**。改了这个文件要 Ctrl+C 重启,
只改前端 app.js / styles.css 的话刷新浏览器就够了。
"""
import json
import re
import time
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
PLAN = HERE / "plan.json"
APPS = DATA / "applications.json"
EVENTS = DATA / "events.jsonl"
PORT = 8766                       # 不是 8765 —— 那个是 LeetCode 看板, 两个要能同时开

STATUSES = ["pool", "todo", "applied", "oa", "screen", "onsite"]  # 单调推进的「到达过的最高阶段」
# pool = 还没决定投不投; todo = 看过 JD 决定要投、排队中; applied 起才算真的投出去了
OUTCOMES = ["", "rejected", "withdrawn", "closed", "offer"]   # 结局和阶段正交: 可以「OA 阶段被拒」
# closed = 「没招」: 本轮没坑。招满了 / 还没开 / 压根不招 entry level 统统算这个 ——
#   一次 board 快照分不出这三种(下架的岗不在 API 里), 而且对本轮决策是同一个动作。
#   要分清只能靠时间: 每天存一份 board, 几周后自己的历史数据会说话。
#   和 rejected 分开是因为诊断不同:
#     rejected 多 -> 简历有问题;  没招 多 -> 动作太慢, 窗口没接住
REFERRALS = ["none", "asked", "got"]

# 前端可以改的字段。白名单而不是黑名单 —— 免得哪天前端多塞个键就写进磁盘
EDITABLE = {"n", "tier", "cat", "size", "bridge", "d", "role", "url",
            "referral", "status", "outcome", "applied", "due", "note",
            "resume", "essay",      # 投递数据: 这次用的哪版魔改简历 / 小作文原文
            # board 扫描的观测。一次快照分不出「招完了」和「没开过」(下架的岗不在
            # API 里), 但同一家扫很多次之后这几个数字自己会说话。由 scan_board.py 写。
            "board", "scan_at", "scan_n", "scan_ng", "scan_mid", "scan_sr"}

MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8"}


def read_plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))



def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "x"


def blank(entry: dict, plan_seed: bool) -> dict:
    """把 plan.json 的 pool 条目铺成一条完整记录。"""
    return {
        "id": slug(entry["n"]),
        "n": entry["n"],
        "tier": entry.get("tier", "C"),
        "cat": entry.get("cat", ""),
        "size": entry.get("size", "mid"),
        "bridge": entry.get("bridge", 0),
        "d": entry.get("d", ""),
        "role": entry.get("role", ""),
        "url": entry.get("url", ""),
        "referral": "none",
        "status": "pool",
        "outcome": "",
        "applied": "",
        "due": "",
        "note": "",
        "resume": "",
        "essay": "",
        # 这家公司下面挂的岗位。公司一行 = 一条投递流程(漏斗的分母), 岗位是它的
        # 明细 —— 同一个 ATS 下的几个 req 拆成几条 jd, 但仍然只算一家。
        "jds": [],
        "board": "",        # 板子的 JSON API 地址(Greenhouse / Ashby), 复扫用
        "scan_at": "",      # 上次扫的日期
        "scan_n": None,     # 在招总数
        "scan_ng": None,    # entry level / new grad 的工程岗 <- 关键那个数
        "scan_mid": None,   # 中级工程岗
        "scan_sr": None,    # 资深工程岗
        "seed": 1 if plan_seed else 0,
    }


def sync_main(a: dict) -> None:
    """把 role / url 同步成「主岗」那条 jd —— 导出和只读静态站还在读这两个字段。"""
    js = a.get("jds") or []
    if not js:
        return
    m = next((j for j in js if j.get("pick")), js[0])
    a["role"], a["url"] = m.get("role", ""), m.get("url", "")


def migrate_jds(a: dict) -> bool:
    """老记录只有 role / url 两个平字段, 铺成第一条 jd。返回是否动过。"""
    if isinstance(a.get("jds"), list):
        return False
    role, url = a.get("role", ""), a.get("url", "")
    a["jds"] = [{"id": "j1", "role": role, "url": url, "loc": "", "lv": "",
                 "note": "", "pick": 1}] if (role or url) else []
    return True


def _read_file() -> dict:
    if not APPS.exists():
        return {"apps": [], "dropped": []}
    d = json.loads(APPS.read_text(encoding="utf-8"))
    d.setdefault("apps", [])
    d.setdefault("dropped", [])
    return d


def load_apps() -> list:
    """读盘 + 用 plan.json 的 pool 补齐新公司(不覆盖已有状态、不复活删过的)。"""
    DATA.mkdir(exist_ok=True)
    d = _read_file()
    apps, dropped = d["apps"], set(d["dropped"])
    have = {a["id"] for a in apps}
    added = 0
    moved = sum(migrate_jds(a) for a in apps)
    # 播种的去重键是**公司名**, 不是 id ——「NVIDIA 中国」slug 出来是 nvidia, 和
    # 母公司撞。按 id 去重的话它要么永远进不来, 要么每次 load 都再加一条。
    have_names = {a["n"] for a in apps}
    for e in read_plan().get("pool", []):
        if e["n"] in have_names:
            continue
        sid = slug(e["n"])
        if sid in dropped:      # 手动删过的不该被 pool 种回来
            continue
        base, i = sid, 2
        while sid in have:      # id 撞了就换一个, 条目照加
            sid, i = f"{base}-{i}", i + 1
        a = blank(e, True)
        a["id"] = sid
        apps.append(a)
        have.add(sid)
        have_names.add(e["n"])
        added += 1
    if added or moved or not APPS.exists():
        save_apps(apps, d["dropped"])
    return apps


def save_apps(apps: list, dropped=None) -> None:
    DATA.mkdir(exist_ok=True)
    if dropped is None:
        dropped = _read_file()["dropped"]
    APPS.write_text(json.dumps({"apps": apps, "dropped": dropped}, ensure_ascii=False, indent=1),
                    encoding="utf-8")


def drop_app(app_id: str) -> bool:
    d = _read_file()
    apps = [a for a in d["apps"] if a["id"] != app_id]
    if len(apps) == len(d["apps"]):
        return False
    dropped = d["dropped"] + ([app_id] if app_id not in d["dropped"] else [])
    save_apps(apps, dropped)
    log_event(app_id, "dropped", "", "")
    return True


def log_event(app_id: str, field: str, old, new) -> None:
    DATA.mkdir(exist_ok=True)
    row = {"ts": datetime.now().isoformat(timespec="seconds"),
           "id": app_id, "f": field, "from": old, "to": new}
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_events() -> list:
    if not EVENTS.exists():
        return []
    out = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass                      # 手改坏了一行不该让整个看板打不开
    return out


def patch(app_id: str, body: dict) -> dict | None:
    apps = load_apps()
    for a in apps:
        if a["id"] != app_id:
            continue
        for k, v in body.items():
            if k not in EDITABLE or a.get(k) == v:
                continue
            # 状态推进到 applied 而没填日期 -> 补今天, 省得每次手点日历
            log_event(app_id, k, a.get(k), v)
            a[k] = v
            if k == "status" and v not in ("pool", "todo") and not a.get("applied"):
                a["applied"] = date.today().isoformat()
                log_event(app_id, "applied", "", a["applied"])
        save_apps(apps)
        return a
    return None


def add_many(names: list, tier: str) -> list:
    """一行一个公司名地粘进来 —— 整理名单时基本都是成批来的, 不是一家一家点。

    重名**跳过**而不是建第二条: 粘过来的清单十有八九和现有名单有重叠,
    默默建一堆 xxx-2 会把你已有的状态藏起来。单个添加仍然允许重名(见 add_app)。
    """
    have = {a["id"] for a in load_apps()}
    dropped = set(_read_file()["dropped"])
    out = []
    for n in names:
        n = n.strip()
        sid = slug(n)
        if not n or sid in have:
            continue
        if sid in dropped:                       # 之前手动删过的, 重新粘进来就当恢复
            d = _read_file()
            save_apps(d["apps"], [x for x in d["dropped"] if x != sid])
        try:
            out.append(add_app({"n": n, "tier": tier}))
            have.add(sid)
        except ValueError:
            pass
    return out


def add_app(body: dict) -> dict:
    apps = load_apps()
    name = (body.get("n") or "").strip()
    if not name:
        raise ValueError("公司名不能为空")
    a = blank({**body, "n": name}, False)
    base, i = a["id"], 2
    while any(x["id"] == a["id"] for x in apps):     # 同名公司(不同组)也能各记一条
        a["id"] = f"{base}-{i}"
        i += 1
    apps.append(a)
    save_apps(apps)
    log_event(a["id"], "created", "", name)
    return a


JD_FIELDS = {"role", "url", "loc", "lv", "note"}


def _find(apps: list, app_id: str) -> dict | None:
    return next((a for a in apps if a["id"] == app_id), None)


def add_jd(app_id: str, body: dict) -> dict | None:
    apps = load_apps()
    a = _find(apps, app_id)
    if a is None:
        return None
    js = a.setdefault("jds", [])
    n = max((int(j["id"][1:]) for j in js if re.fullmatch(r"j\d+", j["id"])), default=0) + 1
    j = {"id": f"j{n}", "role": (body.get("role") or "").strip(),
         "url": (body.get("url") or "").strip(), "loc": (body.get("loc") or "").strip(),
         "lv": body.get("lv") or "", "note": (body.get("note") or "").strip(),
         "pick": 1 if not js else 0}      # 第一条自动成为主岗
    js.append(j)
    sync_main(a)
    save_apps(apps)
    log_event(app_id, "jd+", "", j["role"] or j["url"])
    return a


def patch_jd(app_id: str, jid: str, body: dict) -> dict | None:
    apps = load_apps()
    a = _find(apps, app_id)
    if a is None:
        return None
    j = next((x for x in (a.get("jds") or []) if x["id"] == jid), None)
    if j is None:
        return None
    for k, v in body.items():
        if k in JD_FIELDS and j.get(k) != v:
            log_event(app_id, f"jd.{jid}.{k}", j.get(k), v)
            j[k] = v
    if body.get("pick"):                  # 主岗唯一 —— 设一条就清掉其余
        for x in a["jds"]:
            x["pick"] = 1 if x["id"] == jid else 0
    sync_main(a)
    save_apps(apps)
    return a


def drop_jd(app_id: str, jid: str) -> dict | None:
    apps = load_apps()
    a = _find(apps, app_id)
    if a is None:
        return None
    js = a.get("jds") or []
    keep = [x for x in js if x["id"] != jid]
    if len(keep) == len(js):
        return None
    a["jds"] = keep
    if keep and not any(x.get("pick") for x in keep):   # 删掉的是主岗 -> 顺位补上
        keep[0]["pick"] = 1
    if not keep:
        a["role"], a["url"] = "", ""
    sync_main(a)
    save_apps(apps)
    log_event(app_id, "jd-", jid, "")
    return a


def week_of(iso: str, anchor: str) -> int | None:
    """把一个日期换算成计划里的第几周。anchor 之前的一律算 W0。"""
    if not iso:
        return None
    try:
        d = date.fromisoformat(iso)
        a = date.fromisoformat(anchor)
    except ValueError:
        return None
    return max(0, (d - a).days // 7)


def stats() -> dict:
    """漏斗现算 —— 没有第二份状态。前端也能自己算, 放这儿是为了导出时能烤成静态。"""
    plan = read_plan()
    apps = load_apps()
    anchor = plan.get("anchor", date.today().isoformat())

    def bucket(rows):
        applied = [a for a in rows if a["status"] not in ("pool", "todo")]
        contact = [a for a in applied if a["status"] in ("oa", "screen", "onsite")]
        onsite = [a for a in applied if a["status"] == "onsite"]
        offer = [a for a in applied if a["outcome"] == "offer"]
        return {"pool": len(rows), "applied": len(applied), "contact": len(contact),
                "onsite": len(onsite), "offer": len(offer),
                "rejected": len([a for a in applied if a["outcome"] == "rejected"])}

    by_tier = {t["k"]: bucket([a for a in apps if a["tier"] == t["k"]]) for t in plan["tiers"]}
    by_week = {}
    for a in apps:
        w = week_of(a.get("applied", ""), anchor)
        if w is None:
            continue
        by_week.setdefault(str(w), {}).setdefault(a["tier"], 0)
        by_week[str(w)][a["tier"]] += 1
    return {"all": bucket(apps), "by_tier": by_tier, "by_week": by_week,
            "today": date.today().isoformat(),
            "week_now": week_of(date.today().isoformat(), anchor)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):                      # 别把终端刷满
        pass

    def _send(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/plan":
            return self._send(read_plan())
        if path == "/api/apps":
            return self._send({"apps": load_apps()})
        if path == "/api/stats":
            return self._send(stats())
        if path == "/api/events":
            return self._send({"events": read_events()})

        rel = "index.html" if path == "/" else path.lstrip("/")
        f = (HERE / rel).resolve()
        if not str(f).startswith(str(HERE)) or not f.is_file():
            return self._send({"error": "not found"}, 404)
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")     # 改了 app.js 刷新就生效
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/apps/bulk":
            b = self._body()
            return self._send({"added": add_many(b.get("names") or [], b.get("tier") or "C")})
        m = re.fullmatch(r"/api/apps/([^/]+)/jds", path)
        if m:
            a = add_jd(m.group(1), self._body())
            return self._send(a) if a else self._send({"error": "no such app"}, 404)
        if path != "/api/apps":
            return self._send({"error": "not found"}, 404)
        try:
            return self._send(add_app(self._body()))
        except ValueError as e:
            return self._send({"error": str(e)}, 400)

    def do_DELETE(self):
        path = unquote(urlparse(self.path).path)
        m = re.fullmatch(r"/api/apps/([^/]+)/jds/([^/]+)", path)
        if m:
            a = drop_jd(m.group(1), m.group(2))
            return self._send(a) if a else self._send({"error": "no such jd"}, 404)
        m = re.fullmatch(r"/api/apps/([^/]+)", path)
        if not m:
            return self._send({"error": "not found"}, 404)
        return self._send({"ok": True}) if drop_app(m.group(1)) \
            else self._send({"error": "no such app"}, 404)

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        m = re.fullmatch(r"/api/apps/([^/]+)/jds/([^/]+)", path)
        if m:
            a = patch_jd(m.group(1), m.group(2), self._body())
            return self._send(a) if a else self._send({"error": "no such jd"}, 404)
        m = re.fullmatch(r"/api/apps/([^/]+)", path)
        if not m:
            return self._send({"error": "not found"}, 404)
        a = patch(m.group(1), self._body())
        return self._send(a) if a else self._send({"error": "no such app"}, 404)


def main():
    n = len(load_apps())
    print(f"求职看板 · {n} 家在库 · http://localhost:{PORT}  (Ctrl+C 停)")
    print(f"  计划(可公开)  {PLAN.relative_to(HERE.parent)}")
    print(f"  投递(私密)    {APPS.relative_to(HERE.parent)}   ← 已 gitignore")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
