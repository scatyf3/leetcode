#!/usr/bin/env python3
"""
给 agent 的卡片批注: 复习时顺手记一句「这张卡哪儿不对」, 攒着让 agent 统一改。

    python dashboard/card_comments.py                 # 列出没处理的(默认)
    python dashboard/card_comments.py list --all      # 连处理过的一起列
    python dashboard/card_comments.py done <cid> "改了什么"
    python dashboard/card_comments.py skip <cid> "为什么不改"

存在 dashboard/card-comments.jsonl, 一条批注一行, **两个牌组共用**(靠 deck 区分):

    {"cid": "3f9a1c2e", "ts": 1757880000, "date": "2026-09-14",
     "deck": "problems" | "syntax", "id": 15 | "python-str/标题", "title": "3Sum",
     "text": "干扰项 C 其实也能 AC", "status": "open" | "done" | "skip",
     "reply": "换成了 ...", "resolved": "2026-09-15"}

为什么是一个集中的文件, 而不是往 meta.json 里塞个字段:
语法卡没有 per-card 的 meta(内容在 syntax/*.md, 那份要能通读, 不能插机器字段),
而且 agent 要做的第一件事是「把所有没处理的找出来」—— 一个文件 grep 一遍就完了,
散在一百多个 meta.json 里就得全扫。

处理过的**不删**, 改 status 并写上 reply: 复习面板会把回复贴在那张卡上,
下次问到时能看见 agent 当初改了什么。
"""
import json
import os
import secrets
import sys
import threading
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "card-comments.jsonl"
DECKS = ("problems", "syntax")
STATUSES = ("open", "done", "skip")
_LOCK = threading.Lock()     # server 是 ThreadingHTTPServer, 改状态是"读整份 -> 改 -> 写回"


def read_all() -> list:
    """坏行跳过, 不报错 —— 手改坏了一行不该让复习面板打不开。"""
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(e, dict) and e.get("cid"):
            out.append(e)
    return out


def _write_all(rows: list):
    tmp = LOG.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    os.replace(tmp, LOG)


def add(deck: str, cid_card, title: str, text: str) -> dict:
    text = (text or "").strip()
    if deck not in DECKS:
        return {"ok": False, "error": "bad deck"}
    if not text:
        return {"ok": False, "error": "批注是空的"}
    if cid_card in (None, ""):
        return {"ok": False, "error": "缺 id"}
    # 题号存成整数, 和 reviews.jsonl / attempts.jsonl 一个口径
    if deck == "problems":
        try:
            cid_card = int(cid_card)
        except (TypeError, ValueError):
            return {"ok": False, "error": "题号不是整数"}
    row = {"cid": secrets.token_hex(4), "ts": int(time.time()), "date": date.today().isoformat(),
           "deck": deck, "id": cid_card, "title": title or "", "text": text, "status": "open"}
    with _LOCK:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "comment": row}


def resolve(cid: str, status: str, reply: str = "") -> dict:
    if status not in STATUSES:
        return {"ok": False, "error": f"status 只能是 {STATUSES}"}
    with _LOCK:
        rows = read_all()
        hit = next((r for r in rows if r["cid"] == cid), None)
        if not hit:
            return {"ok": False, "error": "没这条批注"}
        hit["status"] = status
        if status == "open":                 # 重新打开: 把上次的处理记录清掉
            hit.pop("reply", None)
            hit.pop("resolved", None)
        else:
            hit["reply"] = reply
            hit["resolved"] = date.today().isoformat()
        _write_all(rows)
    return {"ok": True, "comment": hit}


def delete(cid: str) -> dict:
    """撤回手滑写的。只删**还没处理**的 —— 处理过的那条是改卡的记录, 不该悄悄抹掉。"""
    with _LOCK:
        rows = read_all()
        hit = next((r for r in rows if r["cid"] == cid), None)
        if not hit:
            return {"ok": False, "error": "没这条批注"}
        if hit.get("status") != "open":
            return {"ok": False, "error": "已经处理过了, 不能撤回"}
        _write_all([r for r in rows if r["cid"] != cid])
    return {"ok": True}


def main(argv: list) -> int:
    cmd = argv[0] if argv else "list"
    if cmd == "list":
        rows = read_all()
        if "--all" not in argv:
            rows = [r for r in rows if r.get("status") == "open"]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if cmd in ("done", "skip", "reopen") and len(argv) >= 2:
        res = resolve(argv[1], "open" if cmd == "reopen" else cmd, argv[2] if len(argv) > 2 else "")
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
