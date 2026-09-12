#!/usr/bin/env python3
"""
把 JD 原文抓下来存进看板(jd 的 text 字段)。岗位一下架 ATS 链接就 404,
面试前想回看「他们到底要什么」全靠这份快照。

    python3 jobs/fetch_jd.py motional              # 这家所有还没存原文的岗位
    python3 jobs/fetch_jd.py motional --force      # 已经存过的也重抓覆盖
    python3 jobs/fetch_jd.py --all                 # 全表扫一遍, 只补缺的

只认三家 ATS 的公开 JSON API(不要 key), 从 jd 的 url 里认出是哪家:
    Greenhouse  gh_jid= / token= / greenhouse.io/<slug>/jobs/<id>
    Ashby       jobs.ashbyhq.com/<slug>/<uuid>
    Lever       jobs.lever.co/<slug>/<uuid>
别的链接(公司自建 careers 页、Workday)抓不了, 在看板里手动粘。
"""
import html
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

API = "http://localhost:8766"


def get(url: str):
    req = urllib.request.Request(url, headers={"accept": "application/json",
                                               "user-agent": "jobs-board-fetch/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


class _Text(HTMLParser):
    """HTML -> 纯文本。只保留段落和列表的结构, 其余样式一概扔掉。"""
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"}

    def __init__(self):
        super().__init__()
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.out.append("\n- ")
        elif tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK or tag == "li":
            self.out.append("\n")

    def handle_data(self, data):
        self.out.append(re.sub(r"\s+", " ", data))

    def text(self) -> str:
        s = "".join(self.out).replace("\xa0", " ")
        s = re.sub(r"[ \t]+\n", "\n", s)
        s = re.sub(r"\n[ \t]+(?!- )", "\n", s)
        return re.sub(r"\n{3,}", "\n\n", s).strip()


def html2text(h: str) -> str:
    p = _Text()
    p.feed(h)
    return p.text()


def greenhouse(u, board: str) -> str | None:
    q = parse_qs(u.query)
    jid = (q.get("gh_jid") or q.get("token") or [None])[0]
    if not jid:
        m = re.search(r"/jobs/(\d+)", u.path)
        jid = m and m.group(1)
    slug = (q.get("for") or [None])[0]
    if not slug and "greenhouse.io" in u.netloc:
        m = re.match(r"/([^/]+)/jobs/", u.path)
        slug = m and m.group(1)
    if not slug:                                  # 公司官网嵌的板子: slug 从 board 字段拿
        m = re.search(r"greenhouse\.io/v1/boards/([^/]+)", board or "")
        slug = m and m.group(1)
    if not (jid and slug):
        return None
    d = get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{jid}")
    head = f"{d.get('title', '')}\n{(d.get('location') or {}).get('name', '')}"
    return head + "\n\n" + html2text(html.unescape(d.get("content") or ""))


def ashby(u) -> str | None:
    parts = [x for x in u.path.split("/") if x]
    if len(parts) < 2:
        return None
    slug, jid = parts[0], parts[1]
    for j in get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}").get("jobs") or []:
        if j.get("id") == jid:
            body = j.get("descriptionPlain") or html2text(j.get("descriptionHtml") or "")
            return f"{j.get('title', '')}\n{j.get('location', '')}\n\n{body}"
    return None


def lever(u) -> str | None:
    parts = [x for x in u.path.split("/") if x]
    if len(parts) < 2:
        return None
    d = get(f"https://api.lever.co/v0/postings/{parts[0]}/{parts[1]}")
    out = [d.get("text", ""), (d.get("categories") or {}).get("location", ""), "",
           d.get("descriptionPlain", "")]
    for sec in d.get("lists") or []:              # Lever 把 requirements 拆在 lists 里
        out += ["", sec.get("text", ""), html2text(sec.get("content", ""))]
    out += ["", d.get("additionalPlain", "")]
    return "\n".join(out).strip()


def which_ats(url: str) -> str | None:
    u = urlparse(url)
    if "gh_jid=" in url or "greenhouse.io" in u.netloc:
        return "greenhouse"
    if "ashbyhq.com" in u.netloc:
        return "ashby"
    if "lever.co" in u.netloc:
        return "lever"
    return None


def fetch_text(url: str, board: str = "") -> str | None:
    """认得的链接但板上没这条 -> None(多半是下架了; Ashby 的岗位页下架了照样回 200)。"""
    u = urlparse(url)
    ats = which_ats(url)
    if ats == "greenhouse":
        return greenhouse(u, board)
    if ats == "ashby":
        return ashby(u)
    if ats == "lever":
        return lever(u)
    return None


def put_text(app_id: str, jid: str, text: str):
    req = urllib.request.Request(f"{API}/api/apps/{app_id}/jds/{jid}", method="PUT",
                                 data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = {x for x in sys.argv[1:] if x.startswith("--")}
    force = "--force" in flags
    rows = get(f"{API}/api/apps")["apps"]
    if "--all" in flags:
        targets = rows
    else:
        if not args:
            raise SystemExit(__doc__)
        want = {x.lower() for x in args}
        targets = [a for a in rows if a["id"].lower() in want or a["n"].lower() in want]
        if not targets:
            raise SystemExit(f"表里没有: {', '.join(args)}")

    for a in targets:
        for j in a.get("jds") or []:
            tag = f"  {a['n']} · {j.get('role') or j['id']}"
            if j.get("text") and not force:
                continue
            if not j.get("url"):
                print(f"{tag}: 没有链接, 跳过")
                continue
            if not which_ats(j["url"]):
                print(f"{tag}: 不是 Greenhouse / Ashby / Lever 链接, 去看板里手动粘")
                continue
            try:
                t = fetch_text(j["url"], a.get("board", ""))
            except Exception as e:                # 404 / 网络挂了: 报一声, 别停整批
                print(f"{tag}: 抓取失败 ({e})")
                continue
            if not t:
                print(f"{tag}: 板上已经没有这条, 多半下架了")
                continue
            put_text(a["id"], j["id"], t)
            print(f"{tag}: 存了 {len(t)} 字")


if __name__ == "__main__":
    main()
