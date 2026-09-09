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
METHOD = HERE / "method.md"        # 方法论散文, 手写 markdown —— 结构化的东西才进 plan.json
APPS = DATA / "applications.json"
EVENTS = DATA / "events.jsonl"
PORT = 8766                       # 不是 8765 —— 那个是 LeetCode 看板, 两个要能同时开

STATUSES = ["pool", "applied", "oa", "screen", "onsite"]   # 单调推进的「到达过的最高阶段」
OUTCOMES = ["", "rejected", "withdrawn", "offer"]          # 结局和阶段正交: 可以「OA 阶段被拒」
REFERRALS = ["none", "asked", "got"]

# 前端可以改的字段。白名单而不是黑名单 —— 免得哪天前端多塞个键就写进磁盘
EDITABLE = {"n", "tier", "cat", "size", "bridge", "d", "role", "url",
            "referral", "status", "outcome", "applied", "due", "note"}

MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8"}


def read_plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def read_method() -> dict:
    """方法论那页的正文。没有这个文件也别让页面炸 —— 退成空字符串。"""
    txt = METHOD.read_text(encoding="utf-8") if METHOD.exists() else ""
    return {"file": METHOD.name, "content": txt}


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
        "seed": 1 if plan_seed else 0,
    }


def load_apps() -> list:
    """读盘 + 用 plan.json 的 pool 补齐新公司(不覆盖已有状态)。"""
    DATA.mkdir(exist_ok=True)
    apps = []
    if APPS.exists():
        apps = json.loads(APPS.read_text(encoding="utf-8")).get("apps", [])
    have = {a["id"] for a in apps}
    added = 0
    for e in read_plan().get("pool", []):
        if slug(e["n"]) not in have:
            apps.append(blank(e, True))
            have.add(slug(e["n"]))
            added += 1
    if added or not APPS.exists():
        save_apps(apps)
    return apps


def save_apps(apps: list) -> None:
    DATA.mkdir(exist_ok=True)
    APPS.write_text(json.dumps({"apps": apps}, ensure_ascii=False, indent=1), encoding="utf-8")


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
            if k == "status" and v != "pool" and not a.get("applied"):
                a["applied"] = date.today().isoformat()
                log_event(app_id, "applied", "", a["applied"])
        save_apps(apps)
        return a
    return None


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
        applied = [a for a in rows if a["status"] != "pool"]
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
        if path == "/api/method":
            return self._send(read_method())
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
        if unquote(urlparse(self.path).path) != "/api/apps":
            return self._send({"error": "not found"}, 404)
        try:
            return self._send(add_app(self._body()))
        except ValueError as e:
            return self._send({"error": str(e)}, 400)

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
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
