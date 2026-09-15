---
name: card-comments
description: 批量处理复习闪卡上攒下来的「给 agent 的批注」—— 读 dashboard/card-comments.jsonl 里 status=open 的条目, 逐条按批注改对应的卡(题目牌组的 meta.json quiz / answer.md / 标签 / 复杂度, 语法牌组的 syntax/*.md), 改完把条目标成 done 或 skip 并写一句回复。用在用户说「处理卡片批注」「按批注改卡」「扫一下 comment」「把闪卡上的意见改了」的时候。
---

# 处理卡片批注

用户复习时在卡上按 `c` 记一句「这张卡哪儿不对」,攒在 `dashboard/card-comments.jsonl`。
这个 skill 把它们**一次性清掉**:读 → 改卡 → 回写状态 → 汇报。

## 1. 列出待处理的

```bash
python3 dashboard/card_comments.py          # 只列 status=open 的, JSON
```

每条长这样:`{"cid", "date", "deck": "problems"|"syntax", "id", "title", "text", "status"}`。
一张卡可能有好几条 —— **按卡分组,每张卡只读一遍、改一遍**。没有 open 的就直接告诉用户,结束。

## 2. 找到卡

| deck | id 长什么样 | 要读的文件 |
|---|---|---|
| `problems` | 题号整数 `15` | `<id>. <题名>/` 下的 `meta.json`(`quiz` / `structures` / `paradigms` / `techniques` / `complexity`)、`answer.md`、`note.md`、`*.py`、`problem.html` |
| `syntax` | `<文件名>/<卡标题>` | `syntax/<文件名>.md` 里 `## <卡标题>` 那一节:单独一行 `---` 以上是正面,以下是背面 |

改之前先读 `note.md` 和解法 —— 批注常常是「答案卡和我实际写法对不上」,真相在 note 里。

## 3. 改卡的规矩

这些是 `dashboard/README.md`「🧠 复习」一节里定死的,改卡时**一条都不能破**:

**选择题(`meta.json` 的 `quiz`)**
- 形状:`{"q"?, "idea": "正确项" | [多个正确项], "wrong": [...], "then"?: [{q, idea, wrong}, ...]}`。选项总数至多 4 个。
- 干扰项必须**真的是错的** —— 另一种也能 AC 的写法既不能当干扰项,也不能当正确项。
- 干扰项**长度要和正确项差不多**,否则「选最长的」就能蒙对。
- **一类题只认一套写法**:二分只写闭区间 `[l, r]`,半开区间不出现在任何选项里。好的干扰项是那套写法里真实踩过的坑。
- 「两种说法是一回事」的题用多选,别用单选配一个「两者都行」。
- 复杂度题的干扰项是自动抽的,**不要手写**。

**答案卡(`answer.md`)**:一句话思路,压缩过的结论,不是流水账。长了就砍,细节留在 note。

**语法卡(`syntax/*.md`)**
- **不要改 `##` 卡标题** —— 标题就是 id,改了复习历史就断了。批注明确要求改标题的话,照改,但回复里写明「id 变了,旧历史成孤儿」。
- 只收用户真栽过的坑;背面末尾那行「栽过:<题号>」保留。
- 按行原样替换,别顺手重排空行 / 统一列表符号。

**不碰的字段**:`fsrs`、`familiarity`、`status`、`paused` —— 前两个分别归调度器和用户自己管。

## 4. 拿不准就 skip,别猜

批注看不懂、和上面的规矩冲突、或者你认为原卡其实是对的 —— **不改**,标 `skip` 并在回复里说清楚为什么。
用户揭晓那张卡时会看到这句回复,不同意可以再批一次。

## 5. 回写状态

```bash
python3 dashboard/card_comments.py done <cid> "干扰项 C 换成「没找到返回 mid」, 原来那个其实也能 AC"
python3 dashboard/card_comments.py skip <cid> "原答案是对的: 闭区间写法 while l <= r, 批注里的 l < r 是半开区间"
```

回复会**贴在卡上揭晓后显示**,所以写成「改了什么 / 为什么没改」的一句话,别写「已处理」这种空话。
同一张卡的几条批注被一次改动解决了,每条都要各自标。

改了 `structures` / `paradigms` / `techniques` / `complexity` 的话,最后跑一次(服务没起就跳过):

```bash
curl -s -X POST localhost:8765/api/sync
```

`quiz` 和 `answer.md` 是详情接口现读的,不用 sync。

## 6. 汇报

结束时给用户一张表:卡 · 批注 · 结果(已改 / 没改)· 一句话说明。skip 的放前面 —— 那些是需要用户再看一眼的。
