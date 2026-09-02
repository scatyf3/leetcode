#!/usr/bin/env python3
"""
把看板烤成一份**只读**静态站, 丢给 GitHub Pages。

    python dashboard/export_static.py [输出目录]     # 默认 dist/

思路: server.py 的每个 GET 接口都只是文件系统的纯函数, 所以直接复用它们,
把响应预先写成同名的 .json 文件:

    /api/problems        -> api/problems.json
    /api/problems/98     -> api/problems/98.json
    /api/notes           -> api/notes.json
    /api/notes/x.md      -> api/notes/x.md.json
    /api/structures/array-> api/structures/array.json

前端一行没改: static-shim.js 把 fetch 改道到这些文件, 写请求一律拒绝(见那个文件)。
所以本地 `python dashboard/server.py` 的可写体验完全不受影响。
"""
import json
import shutil
import sys
from pathlib import Path

import server                       # 复用 sync/list/get_* —— 单一真相还是 meta.json

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_OUT = REPO / "dist"

# notes/*.md 暂时整个不上线 —— 里面有私人内容(methodology.md 那种自述)。
# 想放出来就把 EXPORT_NOTES 改回 True, 再用 PRIVATE_NOTES 逐个排除。
# 注意这只挡住看板; 仓库是 public 的, notes/ 在 GitHub 上照样能直接看到。
EXPORT_NOTES = False
PRIVATE_NOTES = {"scratch.md", "todo.md"}

SITE_FILES = ["app.js", "styles.css", "static-shim.js", "ro.css"]


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def safe_name(name: str) -> str | None:
    """文档/笔记名要当文件名用, 带路径成分的直接跳过, 而不是悄悄改名。"""
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return None
    return name


def export(out: Path) -> dict:
    n = server.sync()                       # 从各文件夹的 meta.json 重建索引
    if out.exists():
        shutil.rmtree(out)
    api = out / "api"

    problems = server.list_problems()
    write_json(api / "problems.json", problems)
    for p in problems:
        write_json(api / "problems" / f"{p['id']}.json", server.get_detail(p["id"]))

    write_json(api / "lists.json", server.read_lists())   # 题单定义, 只读站照样能看进度

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

    for f in SITE_FILES:
        shutil.copy(HERE / f, out / f)
    out.joinpath("index.html").write_text(build_index(), encoding="utf-8")
    (out / ".nojekyll").touch()             # Pages 别拿 Jekyll 处理这堆文件

    return {"problems": n, "docs": docs, "notes": len(notes)}


def build_index() -> str:
    """把 index.html 改成只读版: 挂上 ro.css + shim, 去掉"双击编辑"的提示。"""
    html = (HERE / "index.html").read_text(encoding="utf-8")
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        '<link rel="stylesheet" href="styles.css">\n  <link rel="stylesheet" href="ro.css">',
    )
    # shim 必须在 app.js 之前跑 —— app.js 末尾就直接 reload() 发请求了
    html = html.replace(
        '<script src="app.js"></script>',
        '<script src="static-shim.js"></script>\n  <script src="app.js"></script>',
    )
    html = html.replace(' title="双击进入源码编辑"', "")
    return html


def main():
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT
    stat = export(out)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"exported {stat['problems']} problems, {stat['docs']} docs, "
          f"{stat['notes']} notes -> {out}  ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
