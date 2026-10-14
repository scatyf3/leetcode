#!/usr/bin/env python3
"""
tracker <-> blog 对账: 题挂没挂上知识库, blog 里指向 tracker 的链接还活不活。

为什么要单独查:
blog 每页底部的「挂在这里的题」是构建时按 meta.json 的 structures / paradigms 自动匹配的
(blog/docs/.vitepress/theme/problems.ts 的 problemsOf)。匹配不上不会报错, 题就静悄悄地
哪页都不出现 —— 10/14 那批新题全没打 tag, 就是这么漏的。
VitePress 的 ignoreDeadLinks 也只管站内链接; 指向 github.com/.../tracker/ 的绝对链接
(blog/README.md 规定的写法)文件被改名删掉了它照样构建通过。

查四件事, 前三件对 tag, 最后一件对链接:

    1. 做过的题(status 不是 todo)structures / paradigms 各至少一个 tag
       todo 只警告 —— scaffold.py 新建的题默认就是空 tag
    2. 每个 tag 在 blog/docs/<层>/ 下有同名页面, 或命中某页 frontmatter 的 alias
    3. plan.json 每个 group 的 tag(s) 有对应页面 —— 看板分组点进去要能打开 doc
    4. blog/docs/**/*.md 里 github.com/scatyf3/leetcode/(blob|tree)/main/tracker/... 的路径存在

有错误退出码 1(CI 里挡发布), 只有警告退出码 0。

run:
    python dashboard/check_links.py
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parent                      # tracker/
ROOT = REPO.parent                      # 仓库根
BLOG = ROOT / "blog" / "docs"
PLAN = HERE / "plan.json"

LAYERS = ("structures", "paradigms")    # 和 blog/docs/.vitepress/layers.ts 里带 tag 的两层对应
FOLDER_RE = re.compile(r"^(\d+)\.\s*(.+)$")   # 同 server.py
GH_RE = re.compile(r"https://github\.com/scatyf3/leetcode/(?:blob|tree)/main/(tracker/[^)\s#?]+)")
ALIAS_RE = re.compile(r"^alias:\s*\[(.*)\]\s*$", re.M)


def page_keys(layer: str) -> set[str]:
    """这一层所有页面能接住的 tag: 文件名 + frontmatter 的 alias。"""
    keys = set()
    for f in (BLOG / layer).glob("*.md"):
        if f.stem == "index":
            continue
        keys.add(f.stem)
        text = f.read_text(encoding="utf-8")
        fm = text.split("---", 2)[1] if text.startswith("---") else ""
        if m := ALIAS_RE.search(fm):
            keys.update(a.strip().strip("'\"") for a in m.group(1).split(",") if a.strip())
    return keys


def main() -> int:
    errors, warnings = [], []
    keys = {layer: page_keys(layer) for layer in LAYERS}

    # 1 + 2: 题目 tag
    for d in sorted(REPO.iterdir(), key=lambda p: p.name):
        m = FOLDER_RE.match(d.name)
        if not (d.is_dir() and m):
            continue
        try:
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            errors.append(f"{d.name}: meta.json 读不了 ({e})")
            continue
        for layer in LAYERS:
            tags = meta.get(layer) or []
            if not tags:
                msg = f"{d.name}: 没有 {layer} tag, 不会出现在任何 {layer} 页"
                (warnings if meta.get("status") == "todo" else errors).append(msg)
            for t in tags:
                if t not in keys[layer]:
                    errors.append(f"{d.name}: {layer} tag '{t}' 没有对应页面 (blog/docs/{layer}/{t}.md 或 alias)")

    # 3: plan.json 分组
    for g in json.loads(PLAN.read_text(encoding="utf-8")).get("groups", []):
        tags = g.get("tags") or ([g["tag"]] if g.get("tag") else [])
        for t in tags:
            if t["kind"] in keys and t["name"] not in keys[t["kind"]]:
                errors.append(f"plan.json「{g['name']}」: {t['kind']}/{t['name']} 没有对应页面")

    # 4: blog 指向 tracker 的绝对链接
    for f in sorted(BLOG.rglob("*.md")):
        if ".vitepress" in f.parts:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in GH_RE.finditer(line):
                path = unquote(m.group(1)).rstrip("/")
                if not (ROOT / path).exists():
                    errors.append(f"{f.relative_to(ROOT)}:{n}: 链接目标不存在 {path}")

    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
