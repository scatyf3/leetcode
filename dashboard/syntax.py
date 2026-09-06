#!/usr/bin/env python3
"""
语法卡组 —— FSRS 的第二个牌组。

和题目牌组的关系: **只共用调度器和历史**(dashboard/fsrs.py + dashboard/reviews.jsonl),
其余全分开。题目的真相在各题文件夹的 meta.json, 语法卡的真相在 syntax/*.md。

    syntax/<主题>.md     卡片内容(手写, git 追踪)。一个文件一个主题, 一个 `##` 一张卡
    syntax/state.json    调度状态, 按卡 id 索引(程序写, git 追踪)

为什么这边内容和状态**分开**存, 题目那边却合在一个 meta.json 里:
卡片文件是手写手读的 —— 它同时还要能当 checklist 从头通读一遍(见 notes/off-by-one-checklist.md
那个形态), 每张卡底下插一坨 FSRS 数字就没法看了。题目那边没这个矛盾, meta.json 本来就是机器文件。

卡片格式:

    # 大标题(可选)
    第一个 `##` 之前的一切都是前言, 不是卡。

    ## 这张卡的标题
    正面: 揭晓**前**看到的东西(markdown, 可以是一段有 bug 的代码)
    ---
    背面: 揭晓**后**看到的东西

正反面之间那行单独的 `---` 是分隔符。**没写 `---` 的话整段都算背面**, 正面就只剩标题 ——
"给语义问 API" 那种一句话卡可以这么偷懒。代码块(``` 围起来的)里的 `---` 和 `##` 都不算数。

卡 id = `<文件名(去掉.md)>/<卡标题>`, 例: `str/isalpha 还是 isalnum`。
⚠️ **改卡标题 = 换了个 id**, 那张卡的复习历史会断掉(旧状态留在 state.json 里成为孤儿,
不会被删 —— 历史不该被悄悄抹掉)。想改措辞尽量改正面/背面, 别动标题。
"""
import json
import os
import re
import time
from datetime import date
from pathlib import Path

import fsrs

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SYNTAX_DIR = REPO / "syntax"
STATE_FILE = SYNTAX_DIR / "state.json"
REVIEW_LOG = HERE / "reviews.jsonl"     # 和题目牌组同一份历史, 靠 deck 字段区分
DECK = "syntax"                         # 写进 reviews.jsonl 的牌组名

FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")
SPLIT_RE = re.compile(r"^-{3,}\s*$")    # 正反面分隔线
FILE_RE = re.compile(r"^[\w一-鿿\-.]+\.md$")
WS_RE = re.compile(r"\s+")


# ------------------------------------------------------------------ 解析 ----
def _scan(lines):
    """逐行走一遍, 顺带维护"当前在不在代码块里"。

    不跟踪围栏的话, 卡里贴的 Python 注释 `## 这里` 会被当成新卡的标题, 贴的 diff 里那行
    `---` 会被当成正反面分隔线 —— 两个都会**静默**把卡切碎, 不报错, 只是卡面莫名其妙。
    """
    fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            fence = not fence
            yield i, line, True          # 围栏那行本身也算在代码块内
            continue
        yield i, line, fence


def card_id(topic: str, title: str) -> str:
    """`<主题>/<标题>`。标题里的斜杠换成短横 —— 否则 id 里会多出一层, 看着像另一个文件。"""
    clean = WS_RE.sub(" ", title).strip().replace("/", "-")
    return topic + "/" + clean


def parse_text(text: str, topic: str) -> list:
    """一个文件的正文 -> 卡片列表。back_lines 是背面在原文里的行区间(半开), 给就地编辑用。"""
    lines = text.splitlines()
    marks = [(i, in_fence, line) for i, line, in_fence in _scan(lines)]
    heads = [(i, H2_RE.match(line).group(1))
             for i, in_fence, line in marks if not in_fence and H2_RE.match(line)]

    cards = []
    for n, (start, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        # 正反面分隔线取**第一条**; 后面再出现的 `---` 留在背面里当普通分割线
        cut = next((i for i, in_fence, line in marks
                    if not in_fence and start < i < end and SPLIT_RE.match(line)), None)
        if cut is None:
            front_span, back_span = None, (start + 1, end)
        else:
            front_span, back_span = (start + 1, cut), (cut + 1, end)
        cards.append({
            "id": card_id(topic, title),
            "topic": topic,
            "file": topic + ".md",
            "title": title,
            "front": "\n".join(lines[slice(*front_span)]).strip() if front_span else "",
            "back": "\n".join(lines[slice(*back_span)]).strip(),
            "back_lines": list(back_span),
        })
    return cards


def read_cards() -> list:
    """syntax/*.md 全部卡片, 按文件名 -> 文件内顺序。某个文件读不动就跳过, 不连累整组。"""
    if not SYNTAX_DIR.exists():
        return []
    out = []
    for f in sorted(SYNTAX_DIR.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.extend(parse_text(text, f.stem))
    return out


# ------------------------------------------------------------------ 状态 ----
def load_state() -> dict:
    """{卡 id: fsrs card}。文件不在/坏了都当空 —— 调度记录丢了也不该让面板打不开。"""
    try:
        d = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    c = d.get("cards")
    return c if isinstance(c, dict) else {}


def save_state(cards: dict):
    """原子写, 同 server.write_meta —— 一天要写几十次, 中途断了不能留半个文件。"""
    SYNTAX_DIR.mkdir(exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    body = {"note": "语法卡的 FSRS 调度状态, 由看板写。卡片内容在同目录的 *.md 里。",
            "cards": cards}
    tmp.write_text(json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    os.replace(tmp, STATE_FILE)


def list_cards(today: str) -> dict:
    """给前端的一整组。调度字段**摊平到顶层**, 和 /api/problems 的行同形状 ——
    这样 app.js 里 isCard / isDue / orderQueue 那几个纯函数两个牌组能共用一份。"""
    state = load_state()
    live = set()
    out = []
    for c in read_cards():
        live.add(c["id"])
        f = state.get(c["id"]) or {}
        out.append({
            **{k: v for k, v in c.items() if k != "back_lines"},
            "fsrs": f,
            "fsrs_preview": fsrs.preview(f or fsrs.new_card(), today),
            "due": f.get("due", ""),            # "" = 还没成为卡片, 前端靠这个判断
            "stability": float(f.get("stability") or 0),
            "reps": int(f.get("reps") or 0),
            "last_review": f.get("last_review", ""),
            "fsrs_state": f.get("state", ""),
        })
    # 孤儿 = state 里有、md 里已经没有的 id(多半是改了卡标题)。不删, 只报个数。
    return {"cards": out, "orphans": sorted(set(state) - live)}


# ------------------------------------------------------------------ 复习 ----
def review_card(cid: str, rating: int, today: str):
    """评一次分: 更新 state.json + 往 reviews.jsonl 追一行。

    ⚠️ 调用方必须持有 server 的 _REVIEW_LOCK —— 这里是"读 state -> 改 -> 写回"加追加日志,
    两个请求同时进来会丢掉其中一次评分。
    """
    if cid not in {c["id"] for c in read_cards()}:
        return None
    state = load_state()
    before = state.get(cid) or fsrs.new_card()
    card, interval = fsrs.review(before, rating, today)
    state[cid] = card
    save_state(state)

    last = before.get("last_review") or ""
    entry = {
        "ts": int(time.time()),
        "date": today,
        "deck": DECK,                  # 老行没有这个字段 = 题目牌组, 见 README
        "id": cid,
        "rating": rating,
        # --- 评分前的状态(FSRS 优化器要的就是这个, 别记成评分后的) ---
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
    }
    with REVIEW_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"ok": True, "id": cid, "interval": interval, "due": card["due"],
            "card": card, "preview": fsrs.preview(card, today)}


def reset_card(cid: str) -> bool:
    """退回成没复习过。日志不动 —— 那是历史, 不该被抹。"""
    state = load_state()
    if cid in state:
        del state[cid]
        save_state(state)
    return True


# ------------------------------------------------------------ 就地改背面 ----
def save_back(cid: str, content: str) -> bool:
    """把一张卡的背面写回 syntax/<主题>.md。

    做法是**按行区间原样替换**, 不是"解析成结构再序列化回去" —— 后者会顺手重排空行、
    统一列表符号, 把你手写的排版洗一遍。这里除了背面那几行, 文件其它字节纹丝不动。
    """
    topic = cid.split("/", 1)[0]
    f = SYNTAX_DIR / (topic + ".md")
    if not FILE_RE.match(f.name) or not f.exists():
        return False
    text = f.read_text(encoding="utf-8", errors="replace")
    card = next((c for c in parse_text(text, topic) if c["id"] == cid), None)
    if card is None:
        return False
    lines = text.splitlines()
    a, b = card["back_lines"]
    body = content.strip().splitlines() or [""]
    f.write_text("\n".join(lines[:a] + body + lines[b:]) + "\n", encoding="utf-8")
    return True


if __name__ == "__main__":       # 快速自查: 解析出几张卡、有没有孤儿
    r = list_cards(time.strftime("%Y-%m-%d"))
    for c in r["cards"]:
        print("  {}   front={}b back={}b due={}".format(
            c["id"], len(c["front"]), len(c["back"]), c["due"] or "-"))
    print(len(r["cards"]), "张卡",
          "· {} 个孤儿 {}".format(len(r["orphans"]), r["orphans"]) if r["orphans"] else "")
