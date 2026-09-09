#!/usr/bin/env python3
"""
把求职看板烤好, 放进个人主页仓库(scatyf3.github.io)的 jobs/ 下。

    python jobs/deploy_ghio.py ~/Documents/GitHub/scatyf3.github.io

只写文件, **不 commit 不 push** —— 那一步自己来, 或者让我做。

为什么不是直接 export_static.py:
  1. 那个仓库是 **Jekyll**(academicpages), GitHub 内置构建, 没有 workflow。
     Jekyll 只渲染带 YAML front matter 的文件, 我们的 index.html 没有,
     所以会被当静态文件原样拷走 —— Vue 的 {{ }} 不会被 Liquid 吃掉。**别给它加 front matter。**
  2. 那个仓库的 _config.yml 里 `vendor` 在 exclude 列表。它多半只匹配根目录的
     vendor/, 但赌错了就是 Vue 加载不到、整页白屏。所以这里把目录改名成 lib/,
     顺手把 index.html 里的引用一起改掉 —— 绕开比赌便宜。
"""
import re
import shutil
import sys
from pathlib import Path

import export_static

HERE = Path(__file__).resolve().parent


def deploy(repo: Path) -> Path:
    if not (repo / "_config.yml").exists():
        raise SystemExit(f"{repo} 不像是那个 Jekyll 主页仓库(没有 _config.yml)")
    out = repo / "jobs"
    export_static.export(out)

    # vendor/ -> lib/, 避开 Jekyll 的 exclude
    (out / "vendor").rename(out / "lib")
    idx = out / "index.html"
    idx.write_text(idx.read_text(encoding="utf-8").replace('src="vendor/', 'src="lib/'),
                   encoding="utf-8")

    left = re.findall(r'(?:src|href)="vendor/[^"]*"', idx.read_text(encoding="utf-8"))
    assert not left, f"还有指向 vendor/ 的引用: {left}"
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    o = deploy(Path(sys.argv[1]).expanduser().resolve())
    n = sum(1 for _ in o.rglob("*") if _.is_file())
    print(f"写好了 {n} 个文件 -> {o}")
    print(f"下一步(在 {o.parent} 里): git add jobs && git commit && git push")
    print("注意那个仓库发布的是 **master** 分支, 不是 main。")
