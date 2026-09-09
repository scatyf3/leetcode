---
name: jd
description: 查一家(或一批)公司当前开着的 infra / AI infra / platform / MLE 岗位, 把找到的 JD 摆出来给用户挑, 然后写进 localhost:8766 的求职看板(jobs/)。用在用户说「查一下 X 公司」「X 有什么岗」「把 X 加进看板」「找几家做推理的公司」的时候, 也用在用户给了一串公司名要批量补 JD 链接和岗位名的时候。只查公开的招聘页, 不编造链接。
---

# 查 JD 并填看板

看板在 `jobs/`,数据走 `http://localhost:8766` 的 HTTP API。这个 skill 做三件事:
**找到真实的 JD → 摆出来让用户挑 → 写进表**。

## 0. 先确认服务活着

```bash
curl -sf http://localhost:8766/api/apps >/dev/null || (nohup python3 jobs/server.py > /tmp/jobs-server.log 2>&1 &)
```

分组定义从 `jobs/plan.json` 现读,**不要把组名写死在这里** —— 用户随时会改:

```bash
python3 -c "import json;d=json.load(open('jobs/plan.json'));print([(t['k'],t['role'],t['d']) for t in d['tiers']])"
```

## 1. 找 JD

按这个顺序试,**先命中先停**:

1. 公司自己的 ATS —— `site:job-boards.greenhouse.io <公司>`、`site:jobs.lever.co <公司>`、
   `site:jobs.ashbyhq.com <公司>`。这是唯一权威的来源,而且能一次看到全部在招岗位。
2. 公司官网 `/careers`。
3. 聚合站(Hiring Cafe / HN Who is Hiring)—— 只用来**发现**,拿到之后回到 1 或 2 取真链接。

**LinkedIn 的岗位页不要用**:大量过期和转载,而且投递要走公司 ATS。

### 岗位标题:要什么

```
Infrastructure Engineer      Platform Engineer         Systems Engineer
Distributed Systems Engineer Performance Engineer      Backend Engineer, Infrastructure
ML Platform Engineer         GPU Infrastructure Engineer
Software Engineer, ML/Inference/Training
```

**不要**标题里是 `SRE` / `On-call` / `Production Support` / `GPU Operations` 的 ——
定位粘性:第一份工作 title 落在 ops,之后往 infra 开发转要费力,薪资带也低一档。
同样的活,搜 `ML Platform Engineer` 出来的是开发岗。

MLE 岗**只要**标题里带 infra / systems / platform / training / inference 的 ——
其余的 MLE 多数要建模经验或发表,infra 简历会被直接筛掉。

## 2. 摆出来让用户挑

先给一张紧凑的表,**不要直接写库**:

| # | 岗位 | 地点 | 备注 |
|---|---|---|---|
| 1 | Software Engineer, Inference | SF | C++/CUDA,JD 里点名 vLLM |
| 2 | Platform Engineer | Remote US | 偏 K8s |

再给一句你建议归哪个组、为什么(依据是 `plan.json` 里那几组的 `d`)。
然后问用户要哪几条 —— 一家公司在表里**只留一条**,多个岗位就挑最对口的那个,
其余写进 `note`。

找不到就直说「没有在招的相关岗位」,**不要凑数、不要编链接**。

## 3. 写进表

先看在不在表里:

```bash
curl -s http://localhost:8766/api/apps | python3 -c "
import json,sys; n='Together AI'
print([a['id'] for a in json.load(sys.stdin)['apps'] if a['n'].lower()==n.lower()] or '不在表里')"
```

**不在** → 新建(`id` 由后端从公司名生成):

```bash
curl -s -X POST http://localhost:8766/api/apps \
  -H 'Content-Type: application/json' \
  -d '{"n":"Together AI","tier":"B"}'
```

**在 / 刚建好** → 补字段(一次一个 PUT,可以连发):

```bash
curl -s -X PUT http://localhost:8766/api/apps/together-ai \
  -H 'Content-Type: application/json' \
  -d '{"role":"Software Engineer, Inference","url":"https://job-boards.greenhouse.io/togetherai/jobs/…","cat":"推理服务","size":"mid","d":"JD 点名 vLLM / TensorRT-LLM"}'
```

批量加一串公司名(只建条目,不带字段):

```bash
curl -s -X POST http://localhost:8766/api/apps/bulk \
  -H 'Content-Type: application/json' \
  -d '{"names":["Sierra","Decagon"],"tier":"C"}'
```

### 字段怎么填

| 字段 | 填什么 |
|---|---|
| `role` | JD 上的**原标题**,别翻译别简写 |
| `url` | 那条 JD 的直链(不是公司首页) |
| `cat` | 和表里已有的类别对齐 —— 先 `curl .../api/apps` 看现有取值,别造新词 |
| `size` | `large` >5000 / `mid` 200-5000 / `small` <200,按 LinkedIn 员工数 |
| `d` | 一句话,**事实**(技术栈、地点、JD 里的关键要求)。不写「值得投」「练手好」这类主观判断 —— 这些字段会上公开页面 |
| `tier` | 按 `plan.json` 各组的 `d` 判断;拿不准就问 |

### 不要碰的字段

`status` / `outcome` / `applied` / `referral` / `resume` / `essay` —— 这些是用户自己的
进度和材料,**只有用户明确说了才改**。查完 JD 默认停在 `pool`;用户说「这个要投」
才 `{"status":"todo"}`(= 决定要投、排队中,还不填投递日期)。

## 4. 收尾

一句话说明改了哪几家、加了什么。让用户去 http://localhost:8766 的「公司」页点开看
—— 表里有 JD 链接的行会显示 `JD` 小标,点行打开详情能直接跳。

`plan.json` 的 `pool` 是**播种清单**,这个 skill 不改它 —— 新公司只进
`jobs/data/applications.json`(已 gitignore,不出仓库)。用户要把某家固化进计划里
再手动加到 `pool`。
