#!/usr/bin/env python3
"""
把看板烤成一份**只读**静态站, 丢给 GitHub Pages。

    python dashboard/export_static.py [输出目录]     # 默认 dist/

思路: server.py 的每个 GET 接口都只是文件系统的纯函数, 所以直接复用它们,
把响应预先写成同名的 .json 文件:

    /api/plan            -> api/plan.json
    /api/syntax          -> api/syntax.json
    /api/problems        -> api/problems.json
    /api/problems/98     -> api/problems/98.json
    /api/attempts        -> api/attempts.json
    /api/notes           -> api/notes.json
    /api/notes/x.md      -> api/notes/x.md.json
    /api/structures/array-> api/structures/array.json

前端用的是同一份 Vite 产物(dashboard/web/dist/, 先 `npm run build`), 只在 index.html 里
多挂一个 static-shim.js: 它把 fetch 改道到这些文件, 写请求一律拒绝(见那个文件)。
所以本地 `python dashboard/server.py` 的可写体验完全不受影响。
"""
import json
import shutil
import sys
from pathlib import Path

import server                       # 复用 sync/list/get_* —— 单一真相还是 meta.json
import inbox                        # 手机复习记录的账本(哪些事件已经落进 main)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_OUT = REPO / "dist"

# notes/*.md 暂时整个不上线 —— 里面有私人内容(methodology.md 那种自述)。
# 想放出来就把 EXPORT_NOTES 改回 True, 再用 PRIVATE_NOTES 逐个排除。
# 注意这只挡住看板; 仓库是 public 的, notes/ 在 GitHub 上照样能直接看到。
EXPORT_NOTES = False
PRIVATE_NOTES = {"scratch.md", "todo.md"}

# 语法卡组照常上线 —— syntax/*.md 里就是 Python 语法坑, 没有私人内容, 而且仓库本来就是
# public 的。只读站上它退化成纯自测(空格揭晓 -> 下一张, 不记录), 和题目牌组一个待遇。
EXPORT_SYNTAX = True

# 前端是 Vite 的构建产物(源码 dashboard/web/), 先在仓库根目录 `npm run build`。
# 产物里 ro.css / static-shim.js 来自 web/public/, 原样拷过来, 只在这里被 index.html 引用 ——
# 本地 server.py 伺候的同一份 dist 不挂它们, 所以本地照样可写。
WEB_DIST = HERE / "web" / "dist"


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def safe_name(name: str) -> str | None:
    """文档/笔记名要当文件名用, 带路径成分的直接跳过, 而不是悄悄改名。"""
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return None
    return name


def export(out: Path) -> dict:
    if not (WEB_DIST / "index.html").is_file():
        sys.exit("dashboard/web/dist/ 不存在 —— 先在仓库根目录跑 `npm ci && npm run build`")
    n = server.sync()                       # 从各文件夹的 meta.json 重建索引
    if out.exists():
        shutil.rmtree(out)
    api = out / "api"

    problems = server.list_problems()
    write_json(api / "problems.json", problems)
    for p in problems:
        write_json(api / "problems" / f"{p['id']}.json", server.get_detail(p["id"]))

    # 第二个牌组。不导的话前端拉到空壳 -> 语法队列是 0, 页面照常(见 app.js 的 reload)
    write_json(api / "syntax.json",
               server.syntax_list() if EXPORT_SYNTAX else {"cards": [], "orphans": []})

    write_json(api / "plan.json", server.read_plan())     # 坐标系的分层 + 时间线
    write_json(api / "lists.json", server.read_lists())   # 题单定义, 只读站照样能看进度
    write_json(api / "reviews.json", {"reviews": server.read_reviews()})  # 📈 进度的历史部分
    write_json(api / "edits.json", {"edits": server.read_edits()})      # 标签改动时间轴
    write_json(api / "attempts.json", {"attempts": server.read_attempts()})  # 做题打卡: 日课那两半
    write_json(api / "weak.json", server.weak_list())                 # 攻坚: 弱题列表
    write_json(api / "mock.json", {"mocks": server.read_mocks()})     # 随机两题 mock 的历史
    # 已经落进 main 的手机事件。手机据此把它们从 data 分支的 inbox 里删掉、也不再重放(见 inbox.py)
    write_json(api / "sync-applied.json", {"eids": sorted(inbox.applied_eids())})

    # 分组标签 = 看板上可点开的通用 trick 文档, 两个维度各导一份
    docs = 0
    for kind, field in (("structures", "structures"), ("paradigms", "paradigms")):
        names = {t for p in problems for t in p[field]}
        for name in sorted(names):
            fn = safe_name(name)
            if fn is None:
                print(f"  skip {kind}/{name!r} (名字里有路径成分)", file=sys.stderr)
                continue
            write_json(api / kind / f"{fn}.json", server.get_doc(kind, name))
            docs += 1

    # list_notes 是按 mtime 排的, 但 CI 里全是 checkout 的时间 -> 顺序随机且每次构建都变。
    # 按文件名排, 并丢掉 mtime(前端不用), 这样同一个 commit 构建出来的产物是确定的。
    notes = sorted((x for x in server.list_notes() if x["file"] not in PRIVATE_NOTES),
                   key=lambda x: x["file"]) if EXPORT_NOTES else []
    for x in notes:
        x.pop("mtime", None)
    write_json(api / "notes.json", notes)
    for x in notes:
        fn = safe_name(x["file"])
        if fn is None:
            continue
        write_json(api / "notes" / f"{fn}.json", server.get_note(x["file"]))

    shutil.copytree(WEB_DIST, out, dirs_exist_ok=True)   # assets/ + ro.css + static-shim.js
    out.joinpath("index.html").write_text(build_index(), encoding="utf-8")
    (out / ".nojekyll").touch()             # Pages 别拿 Jekyll 处理这堆文件

    return {"problems": n, "docs": docs, "notes": len(notes),
            "syntax": len(server.syntax_list()["cards"]) if EXPORT_SYNTAX else 0}


def build_index() -> str:
    """把构建出的 index.html 改成只读版: 挂上 ro.css + shim, 去掉"双击编辑"的提示。"""
    html = (WEB_DIST / "index.html").read_text(encoding="utf-8")
    # 都塞在 </head> 前面:
    #   ro.css 排在 Vite 注入的样式表之后, 同优先级时后来者赢;
    #   shim 是普通同步脚本, 解析到就跑 —— 而 Vite 的入口是 type=module(天然 defer),
    #   所以 shim 一定先把 fetch 改道、先挂上 .ro, app.js 顶层的 reload() 才发请求。
    assert html.count("</head>") == 1, "构建出的 index.html 里找不到 </head>"
    html = html.replace(
        "</head>",
        '  <link rel="stylesheet" href="ro.css">\n  <script src="static-shim.js"></script>\n</head>',
    )
    html = html.replace(' title="双击进入源码编辑"', "")
    return html


def main():
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT
    stat = export(out)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"exported {stat['problems']} problems, {stat['syntax']} syntax cards, "
          f"{stat['docs']} docs, {stat['notes']} notes -> {out}  ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
