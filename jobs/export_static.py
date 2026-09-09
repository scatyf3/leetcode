#!/usr/bin/env python3
"""
把求职看板烤成一份**只读**静态站, 丢给 GitHub Pages。

    python jobs/export_static.py [输出目录]      # 默认 dist/jobs

和 dashboard/export_static.py 同一个思路: GET 接口都是文件系统的纯函数, 直接复用,
把响应预写成同名 .json, 前端由 static-shim.js 改道过去。

**但这里默认只导方法论, 不导投递数据。** 因为这个仓库是 public 的 ——
线上那份是「三档分层 + 8 周时间线怎么排」, 不是「我投了谁、被谁拒了」。
真想连状态一起公开, 把 EXPORT_APPLICATIONS 改成 True(想清楚再改)。
"""
import json
import shutil
import sys
from pathlib import Path

import server                       # 复用 read_plan / load_apps / stats

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parent / "dist" / "jobs"

# ← 唯一的开关。False = 线上只有 plan.json 那份方法论, 公司状态一概不出仓库。
EXPORT_APPLICATIONS = False

SITE_FILES = ["app.js", "styles.css", "static-shim.js",
              "vendor/vue.global.prod.js", "vendor/marked.min.js"]


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def export(out: Path) -> dict:
    if out.exists():
        shutil.rmtree(out)
    api = out / "api"

    write_json(api / "plan.json", server.read_plan())
    write_json(api / "method.json", server.read_method())    # 方法论正文, 公开站的主体

    if EXPORT_APPLICATIONS:
        apps = server.load_apps()
        write_json(api / "apps.json", {"apps": apps})
        write_json(api / "stats.json", server.stats())
        write_json(api / "events.json", {"events": server.read_events()})
    else:
        # 空壳而不是 404 —— 前端照常渲染, 时间线和漏斗就是一排 0, 方法那页是全的
        write_json(api / "apps.json", {"apps": []})
        write_json(api / "stats.json", {})
        write_json(api / "events.json", {"events": []})

    # index.html 里插一行 static-shim.js —— 源文件不动, 本地那份仍然可写
    html = (HERE / "index.html").read_text(encoding="utf-8")
    html = html.replace('<script src="app.js"></script>',
                        '<script src="static-shim.js"></script>\n<script src="app.js"></script>')
    (out / "index.html").write_text(html, encoding="utf-8")

    for rel in SITE_FILES:
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / rel, dst)

    return {"out": str(out), "apps": EXPORT_APPLICATIONS}


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    r = export(target.resolve())
    print(f"导出到 {r['out']}  ·  投递数据: {'含' if r['apps'] else '不含(只有方法论)'}")
