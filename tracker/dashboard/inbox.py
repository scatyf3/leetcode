#!/usr/bin/env python3
"""
手机上的复习记录 -> 本机仓库。

只读站(GitHub Pages)连上 GitHub token 之后, 复习面板里的评分 / 暂停 / 批注不再丢掉,
而是记成一条条**事件**, 同步到仓库 `data` 分支的 dashboard/sync-inbox.json
(前端见 web/src/sync.ts 和 web/src/lib/inbox.ts)。这里负责把它们落回真相源:

    评分 rate     -> 那道题的 meta.json fsrs / syntax/state.json + reviews.jsonl 一行
    暂停 pause    -> meta.json 的 paused + edits.jsonl 一行
    批注 comment  -> card-comments.jsonl 一行(cid 就是事件的 eid)

落过的事件记进 dashboard/sync-applied.jsonl(git 追踪, 账本)。**按 eid 去重**, 所以同一份
inbox 读多少遍都只落一次; 账本随 main 导出到只读站, 手机看到哪些已经进了 main,
就把它们从 inbox 里删掉(inbox 不会一直长)。

为什么是事件而不是像 ai-infra-inferview 那样同步整份状态:
这边的调度状态散在一百多个 meta.json 里, 而且本机的看板也在同时评分。事件只追加、不修改,
两台设备怎么交错都是取并集, 没有"谁盖掉谁"的问题; FSRS 统一由这边的 fsrs.py 重放,
手机上算出来的 due 只是临时显示。

    python dashboard/inbox.py              # 拉 data 分支, 落还没落过的事件
    python dashboard/inbox.py --dry-run    # 只列出来, 不写
    python dashboard/inbox.py --no-fetch   # 不联网, 用上次拉下来的 origin/data

server.py 启动时和点 ↻ Sync 时会自己跑一遍, 平时不用手动。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INBOX_PATH = "dashboard/sync-inbox.json"      # data 分支上的路径(前端 lib/inbox.ts 里写死同一个)
LEDGER = HERE / "sync-applied.jsonl"
REMOTE, BRANCH = "origin", "data"
OPS = ("rate", "pause", "comment")
DECKS = ("problems", "syntax")


def _git(*args, timeout=30):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}   # 要密码就直接失败, 别在后台线程里卡住
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, timeout=timeout, env=env)


def fetch(timeout=20) -> str:
    """git fetch data 分支。返回错误信息, 成功是空串。失败了也照样能读上次拉下来的那份。"""
    try:
        r = _git("fetch", "--quiet", REMOTE, f"+{BRANCH}:refs/remotes/{REMOTE}/{BRANCH}", timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"git fetch 失败: {e}"
    if r.returncode:
        msg = r.stderr.decode("utf-8", "replace").strip()
        # data 分支还没建(手机还没同步过一次): 不算错
        return "" if "couldn't find remote ref" in msg else f"git fetch 失败: {msg}"
    return ""


def read_remote() -> list:
    """origin/data 上的 inbox。分支或文件不存在 / 格式不对都当空。"""
    try:
        r = _git("show", f"{REMOTE}/{BRANCH}:{INBOX_PATH}")
    except (OSError, subprocess.TimeoutExpired):
        return []
    if r.returncode:
        return []
    try:
        d = json.loads(r.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    evs = d.get("events") if isinstance(d, dict) else None
    return [e for e in evs if valid(e)] if isinstance(evs, list) else []


def valid(e) -> bool:
    """和前端 lib/inbox.ts 的 isEvent 同一套口径。不认的事件跳过, 不进账本 —— 修好了还能再落。"""
    if not isinstance(e, dict) or not isinstance(e.get("eid"), str) or not e["eid"]:
        return False
    if e.get("op") not in OPS or e.get("deck") not in DECKS:
        return False
    if not isinstance(e.get("ts"), (int, float)) or not isinstance(e.get("date"), str):
        return False
    if e["deck"] == "problems" and not isinstance(e.get("id"), int):
        return False
    if e["deck"] == "syntax" and not isinstance(e.get("id"), str):
        return False
    if e["op"] == "rate" and e.get("rating") not in (1, 2, 3, 4):
        return False
    if e["op"] == "comment" and not str(e.get("text") or "").strip():
        return False
    return True


def read_ledger() -> list:
    if not LEDGER.exists():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(e, dict) and e.get("eid"):
            out.append(e)
    return out


def applied_eids() -> set:
    return {e["eid"] for e in read_ledger()}


def append_ledger(rows: list):
    if not rows:
        return
    with LEDGER.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def pending(events: list, applied: set) -> list:
    """还没落过的, 按发生顺序(ts, eid)。同一个 eid 出现两次只取一次。"""
    seen, out = set(applied), []
    for e in sorted(events, key=lambda e: (e["ts"], e["eid"])):
        if e["eid"] in seen:
            continue
        seen.add(e["eid"])
        out.append(e)
    return out


def ledger_row(e: dict, result: str) -> dict:
    return {"eid": e["eid"], "applied": time.strftime("%Y-%m-%d"), "op": e["op"],
            "deck": e["deck"], "id": e["id"], "result": result}


def main(argv: list) -> int:
    import server                  # 只在命令行用; server.py 自己 import 这个模块时不走这里
    if "--no-fetch" not in argv:
        err = fetch()
        if err:
            print(err, file=sys.stderr)
    events = pending(read_remote(), applied_eids())
    if "--dry-run" in argv:
        for e in events:
            print(json.dumps(e, ensure_ascii=False))
        print(f"{len(events)} 条待落")
        return 0
    res = server.ingest_inbox(fetch_first=False)
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
