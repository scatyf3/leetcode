"""把 Claude Code 里讨论题目的会话存成题目文件夹里的 chat.md(看板「💬 讨论」tab 渲染它)。

    python dashboard/save_chat.py                 # 扫本仓库全部会话, 能认出题目的段都落盘
    python dashboard/save_chat.py -n              # 只打印「哪段 -> 哪题」, 不写文件
    python dashboard/save_chat.py -s 6f2a01ea -p 2608   # 认不出题的段(开头没报题名)手动指给 2608

会话从哪来: ~/.claude/projects/<仓库路径>/<session>.jsonl。这些文件 Claude Code 默认 30 天后清理,
所以 chat.md 是存档 —— 已存的段不会因为原会话被删而消失。

怎么切段: 一个会话里常连着问好几题(先 2608 再 2836), 按「用户这条消息换题了」切。
换题的认法(只看用户消息, 不看 Claude 的):
  - 第一行以完整题名开头(至少两个词, 免得 "Combinations" 这种单词误伤),
    或带「题号. 题名」/「#题号」/「LC 题号」
  - 贴进来的代码里 class Solution 的方法名 / 设计题的类名, 能唯一对上某个题目文件夹里的 .py
认不出题的开头段(比如先闲聊再报题)跳过, 除非 -p 指定。

存什么: 用户消息(贴的代码转成代码块) + Claude 的可见回复。工具调用 / 工具输出 / system-reminder 都丢掉;
Claude 的 thinking 在会话文件里是空的(只存签名), 所以「推理过程」就是可见回复本身。

chat.md 的格式(看板按这两种行切气泡, 手写/从 claude.ai 粘的没这些标记就整篇当 markdown 渲染):
  <!-- chat 6f2a01ea/1a2b3c4d 2026-11-22 -->     一段会话的开头, 重跑时按这个 key 原地替换
  #### 🧑 我 / #### 🤖 Claude                     说话人
第一个标记之前的内容(手粘的)原样保留。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DASH = Path(__file__).resolve().parent
TRACKER = DASH.parent
REPO = TRACKER.parent
SESS_DIR = Path.home() / ".claude" / "projects" / ("-" + str(REPO).strip("/").replace("/", "-").replace(" ", "-"))
CHAT_FILE = "chat.md"

USER_H, BOT_H = "#### 🧑 我", "#### 🤖 Claude"
MARK = re.compile(r"^<!-- chat (\S+) (\S+) -->$", re.M)


# ---- 题目索引 ------------------------------------------------------------------

def load_problems():
    """{pid: folder}, 标题索引 [(lower title, pid)], 方法名索引 {name: pid}(只留唯一的)"""
    folders, titles, names = {}, [], {}
    for f in TRACKER.iterdir():
        m = re.match(r"^(\d+)\. (.+)$", f.name)
        if not (f.is_dir() and m):
            continue
        pid = int(m.group(1))
        folders[pid] = f
        if len(m.group(2).split()) >= 2:
            titles.append((m.group(2).lower(), pid))
        for py in f.glob("*.py"):
            src = py.read_text(encoding="utf-8", errors="replace")
            found = re.findall(r"^class (?!Solution\b)(\w+)", src, re.M)          # 设计题
            sol = re.search(r"^class Solution\b", src, re.M)
            if sol:   # 主方法: 只看 class Solution 之后的, 前面可能先定义了 UF 之类的辅助类
                found += re.findall(r"^    def (?!__)(\w+)\(self", src[sol.end():], re.M)[:1]
            for n in found:
                names.setdefault(n, set()).add(pid)
    titles.sort(key=lambda t: -len(t[0]))           # 长题名先匹配
    uniq = {n: next(iter(p)) for n, p in names.items() if len(p) == 1}
    return folders, titles, uniq


def detect(text: str, code: list[str], folders, titles, names) -> int | None:
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    low = first.lower()
    # 显式题号: "#45" / "LC 45" 任意位置; 行首的裸题号("372 快速幂…")至少两位;
    # 其余位置的 "1866. Title" 要题号后面真跟着题名 —— 不然 "1. 固定符号…" 这种列表会认成 Two Sum
    for m in re.finditer(r"(#|\blc\s*)?\b(\d{1,4})\b\.?\s*", low):
        pid = int(m.group(2))
        if pid not in folders:
            continue
        title = folders[pid].name.lower().split(". ", 1)[1]
        if (m.group(1) or low[m.end():].startswith(title)
                or m.start() == 0 and len(m.group(2)) >= 2 and not low[m.end(2):].startswith(".")):
            return pid
    # 只报题名: 得在行首("Binary Search" 夹在句子里多半是在说算法, 不是在报题)
    for t, pid in titles:
        if low.startswith(t):
            return pid
    for c in code:
        for n in re.findall(r"^\s*(?:class|def) (\w+)", c, re.M):
            if n in names:
                return names[n]
    return None


# ---- 会话 -> 轮次 ---------------------------------------------------------------

PASTE = re.compile(r'<pasted_content[^>]*>\n?(.*?)\n?</pasted_content[^>]*>', re.S)   # 闭合标签也带 id
NOISE = re.compile(r"<(system-reminder|ide_selection|ide_opened_file|browser_instruction|"
                   r"command-message|command-name|command-args|local-command-stdout)>.*?</\1>", re.S)


def clean_user(text: str) -> tuple[str, list[str]]:
    text = NOISE.sub("", text)
    # 贴的代码有两种: 粘贴块 <pasted_content>, 或自己打的 ``` 围栏 —— 都拿去对方法名
    code = [c.strip("\n") for c in PASTE.findall(text) + re.findall(r"```\w*\n(.*?)```", text, re.S)]

    def fence(m):
        body = m.group(1).strip("\n")
        lang = "python" if re.search(r"^\s*(def|class|import|from) ", body, re.M) else ""
        return f"\n```{lang}\n{body}\n```\n"
    return PASTE.sub(fence, text).strip(), code


def turns(path: Path):
    """[(role, text, uuid, timestamp, code)], 同一说话人连续的块合成一轮"""
    out = []
    for line in path.open(encoding="utf-8"):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") not in ("user", "assistant") or o.get("isSidechain") or o.get("isMeta"):
            continue
        c = o["message"].get("content")
        blocks = [{"type": "text", "text": c}] if isinstance(c, str) else c
        texts = [b["text"] for b in blocks if b.get("type") == "text" and b.get("text")]
        if not texts:
            continue                                  # 纯工具调用 / 工具结果 / thinking
        role = "user" if o["type"] == "user" else "bot"
        code = []
        if role == "user":
            parts = [clean_user(t) for t in texts]
            texts = [t for t, _ in parts if t]
            code = [c for _, cs in parts for c in cs]
            if not texts:
                continue
        text = "\n\n".join(t.strip() for t in texts)
        if out and out[-1][0] == role:
            prev = out[-1]
            out[-1] = (role, prev[1] + "\n\n" + text, prev[2], prev[3], prev[4] + code)
        else:
            out.append((role, text, o.get("uuid", ""), o.get("timestamp", ""), code))
    return out


def segments(path: Path, idx, force: int | None):
    """[(pid, key, date, turns)]: 在「用户换题」处切开"""
    segs, cur = [], None
    for t in turns(path):
        if t[0] == "user":
            pid = detect(t[1], t[4], *idx)
            if cur is None or (pid is not None and pid != cur[0]):
                if cur is None and pid is None:
                    pid = force
                cur = [pid, f"{path.stem[:8]}/{t[2][:8]}", t[3][:10], []]
                segs.append(cur)
        if cur is not None:
            cur[3].append(t)
    return [s for s in segs if s[0] is not None and any(r == "bot" for r, *_ in s[3])]


# ---- 写 chat.md ------------------------------------------------------------------

def render(key, date, ts) -> str:
    body = "\n\n".join(f"{USER_H if r == 'user' else BOT_H}\n\n{text}" for r, text, *_ in ts)
    return f"<!-- chat {key} {date} -->\n\n{body}\n"


def merge(path: Path, new: dict[str, tuple[str, str]]) -> bool:
    """new: {key: (date, rendered)}。已有的同 key 段原地替换, 新段按日期排进去"""
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    ms = list(MARK.finditer(old))
    pre = old[: ms[0].start()] if ms else old
    blocks = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(old)
        blocks[m.group(1)] = (m.group(2), old[m.start():end].rstrip() + "\n")
    blocks.update(new)
    out = pre.rstrip() + ("\n\n" if pre.strip() else "")
    out += "\n---\n\n".join(b for _, b in sorted(blocks.values(), key=lambda v: v[0]))
    if out == old:
        return False
    path.write_text(out, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-s", "--session", help="只处理 id 以此开头的会话")
    ap.add_argument("-p", "--problem", type=int, help="认不出题的开头段归给这题(配合 -s 用)")
    ap.add_argument("-n", "--dry-run", action="store_true")
    a = ap.parse_args()

    idx = load_problems()
    files = sorted(SESS_DIR.glob(f"{a.session or ''}*.jsonl"), key=lambda p: p.stat().st_mtime)
    plan: dict[int, dict] = {}
    for f in files:
        for pid, key, date, ts in segments(f, idx, a.problem):
            n = sum(r == "user" for r, *_ in ts)
            print(f"{key}  {date}  -> {pid:<5} {idx[0][pid].name[:50]}  ({n} 问)")
            plan.setdefault(pid, {})[key] = (date, render(key, date, ts))
    if a.dry_run:
        return
    for pid, new in plan.items():
        if merge(idx[0][pid] / CHAT_FILE, new):
            print(f"写入 {idx[0][pid].name}/{CHAT_FILE}")


if __name__ == "__main__":
    main()
