<script lang="ts">
// ---- 🧠 FSRS 复习面板: 看题面 -> 心里过思路 -> 揭晓 -> 1-4 自评 ----------------
// 迁到 Vue 的理由: 这一屏状态最多(队列 / 揭晓与否 / 选择题 / 就地编辑 / tab),
// 以前全靠手工 classList.toggle + innerHTML 对齐, 加一个元素就容易漏一处。
// 现在 DOM 一律从 data/computed 推导出来。
//
// 和看板其余部分(app.js, 手写 DOM)之间只走 `host` 这一个口子 —— 读两组行、重画看板、
// 改 meta、开 📈。以前是直接摸全局变量, 拆成模块之后得写明白依赖了谁。
import { defineComponent, type PropType } from 'vue'
import { api, postJSON, isReadOnly } from '@/api'
import { esc } from '@/lib/esc'
import { fmtInterval, todayStr } from '@/lib/dates'
import { highlightPython } from '@/lib/highlight'
import { DECKS, DECK_LABEL, RV_MODES, orderQueue } from '@/lib/queue'
import { newCard, preview as fsrsPreview } from '@/lib/fsrs'
import type { InboxEvent } from '@/lib/inbox'
import { syncState } from '@/sync'
import type { QuizBlock, QuizState } from '@/lib/quiz'
import type { Deck, QueueMode } from '@/lib/types'

/* eslint-disable @typescript-eslint/no-explicit-any */
export interface ReviewHost {
  /** 当前牌组的全部行(活的引用, 就地改 due 用) */
  rows: (deck: Deck) => any[]
  /** 今天这一轮的队列: 现算 + 扣掉今天已评过的上限 */
  queue: (mode: QueueMode, deck: Deck) => (number | string)[]
  quiz: (d: any) => { ideas: QuizBlock[]; cx: QuizState | null }
  md: (src: string) => string
  /** 重画背后的看板, 返回两个牌组的到期数 */
  refresh: () => Record<Deck, number>
  /** 只刷徽章, 返回两个牌组的到期数 */
  badge: () => Record<Deck, number>
  putMeta: (id: number, body: Record<string, unknown>) => Promise<Response>
  openStats: () => void
  /** reviews.jsonl 多了一行, 让 📈 下次重新拉 */
  reviewsChanged: () => void
  // ---- 下面三个只有只读站连上 GitHub 时用(见 ../sync.ts): 本地是直接打 server.py ----
  /** 记一条事件, 并且就地放到行上(评分改调度字段, 暂停记日期) */
  record: (e: Pick<InboxEvent, 'deck' | 'id' | 'op'> & Partial<InboxEvent>) => InboxEvent
  /** 今天最后一次评 1 的(server.review_carry 的 again, 从还没落进 main 的事件里算) */
  again: (deck: Deck) => (number | string)[]
  /** 还没落进 main 的批注, 和 card-comments.jsonl 的行同形状 */
  pendingComments: () => any[]
}

// 只读站没有 session.json, 「押到队尾」记在浏览器里, 形状同 session.json 的 defers
const DEFERS_KEY = 'lc-rv-defers'
function loadDefers(deck: Deck): (number | string)[] {
  try {
    const d = JSON.parse(localStorage.getItem(DEFERS_KEY) || 'null')
    return d && d.date === todayStr() && Array.isArray(d[deck]) ? d[deck] : []
  } catch { return [] }
}
function saveDefers(deck: Deck, ids: (number | string)[]) {
  try {
    const old = JSON.parse(localStorage.getItem(DEFERS_KEY) || 'null')
    const keep = old && old.date === todayStr() ? old : {}
    localStorage.setItem(DEFERS_KEY, JSON.stringify({ ...keep, date: todayStr(), [deck]: ids }))
  } catch { /* 隐私模式 */ }
}

function savedMode(): QueueMode {
  try {
    const m = localStorage.getItem('rv-mode') as QueueMode
    if (RV_MODES.includes(m)) return m
  } catch { /* 隐私模式 */ }
  return 'fsrs'
}

function savedDeck(): Deck {
  try {
    const d = localStorage.getItem('rv-deck') as Deck
    if (DECKS.includes(d)) return d
  } catch { /* 隐私模式 */ }
  return 'problems'
}

export default defineComponent({
  name: 'ReviewPanel',
  props: { host: { type: Object as PropType<ReviewHost>, required: true } },

  data() {
    return {
      open: false,
      queue: [] as (number | string)[], done: 0, total: 0,
      d: null as any,                // 当前这道的详情; null = 队列空了(显示收尾屏)
      loading: false,                // 拉详情中。不加这个会先闪一下"没有到期的题"
      revealed: false,
      quiz: { ideas: [], cx: null } as { ideas: QuizBlock[]; cx: QuizState | null },
      items: [] as { name: string; md?: string; code?: string }[], active: 0,  // 揭晓后的 note / 各解法 tab
      editing: false, draft: '', amsg: '',
      attempt: '',                   // 揭晓前自己默写的那一遍。**只活在这一张卡的这一次**:
                                     // 不发给后端、不写 syntax/*.md、换一张就清空
      note: '',                      // 顶部那行临时提示(写失败 / 已经是队尾)
      comments: [] as any[],         // card-comments.jsonl 全部行(两个牌组), 开面板时拉一次
      cbox: false, cdraft: '',       // 批注框开没开 / 草稿。Esc 收起不清草稿, 换卡才清
      busy: false,                   // 评分->取下一题这一整段在飞。见 rate() 上面那段注释
      failMsg: '',                   // 拉下一题失败时的收尾屏文案(替掉"复习完了")
      deferred: [] as (number | string)[],  // 今天(当前牌组)按过「押到队尾」的题, 按发生顺序, 可重复
      startGen: 0,                   // start() 的代号: 异步拉 carry 期间被新的 start() 顶掉就作废
      mode: savedMode(),
      deck: savedDeck(),
      counts: { problems: 0, syntax: 0 } as Record<Deck, number>,   // 标在牌组按钮上的到期数
      readOnly: isReadOnly(),
      sync: syncState,               // 只读站连上 GitHub 之后能评分(见 writable)
      MODES: [{ k: 'fsrs', label: '到期优先' }, { k: 'order', label: '顺序' }, { k: 'random', label: '随机' }] as { k: QueueMode; label: string }[],
      DECKS: [{ k: 'problems', label: '题目' }, { k: 'syntax', label: '语法' }] as { k: Deck; label: string }[],
      KEYS: 'ABCD',
      RATE: { 1: ['忘了', '想不起来'], 2: ['勉强', '想了很久'], 3: ['想起来了', '正常'], 4: ['很熟', '秒答'] } as Record<number, [string, string]>,
      CMT_ST: { open: '待改', done: '已改', skip: '没改' } as Record<string, string>,
    }
  },

  computed: {
    isSyntax(): boolean { return this.deck === 'syntax' },
    // 能不能评分 / 暂停 / 批注: 本地 server.py 永远能; 只读站要连上 GitHub(记成事件推到 data 分支)。
    // 「改一下」答案卡不算在内 —— 那是改内容文件, 只读站上一直是 readOnly 说了算
    writable(): boolean { return !this.readOnly || this.sync.mode === 'github' },
    // 左上角那个胶囊: 题目是题号, 语法卡是主题(= 文件名), 都是"这是哪一类"的定位信息
    pillText(): string { return this.d ? String(this.isSyntax ? this.d.topic : this.d.id) : '' },
    metaLine(): string {
      if (!this.d) return ''
      const reps = this.d.fsrs && this.d.fsrs.reps ? `第 ${this.d.fsrs.reps + 1} 次复习` : '第一次进复习'
      return `${this.isSyntax ? this.d.file : (this.d.difficulty || '?')} · ${reps}`
    },
    // v-html: 两句提示里都有加粗。内容是写死的常量, 没有外部输入
    askText(): string {
      return this.isSyntax
        ? '先<b>说出答案</b>再揭晓'
        : '心里说清 <b>结构 · 范式 · 触发条件</b>, 不写代码'
    },
    // 只渲染题面 / 卡片正面。绝不碰 d.note / d.solutions / d.back —— 剧透了这个功能就没意义了
    descHtml(): string {
      if (!this.d) return ''
      if (this.isSyntax) {
        // 正面可以是空的: 那种卡的问题**就是标题**(「想判断字符是字母或数字, 用哪个方法」),
        // 标题已经在上面大字显示了, 这里不用再补一句废话
        return this.d.front ? this.host.md(this.d.front) : ''
      }
      return this.d.description
        || '<p class="hint">这题没有抓到题面(problem.html 是空的)。只能靠标题回忆 —— 或者跑 dashboard/fetch_desc.py 补抓。</p>'
    },
    // 拉详情的空档不能显示收尾屏 —— 会闪一下"今天没有到期的题"
    showEmpty(): boolean { return !this.d && !this.loading },
    // 默写框只有语法卡有。题目牌组揭晓前的规矩是"不写代码"(见 askText), 它测的是
    // 辨别力, 那边对应的是选择题 —— 两个牌组各有各的"揭晓前动一下手"。
    canWrite(): boolean { return this.isSyntax },
    // 空白/只有空格的不算写过: 揭晓后就不必贴一个空框上去
    mine(): string { return this.attempt.trim() },
    // 这张卡上的批注。题号在 jsonl 里是整数、语法卡 id 是字符串, 统一按字符串比
    cardComments(): any[] {
      if (!this.d) return []
      const id = String(this.d.id)
      return this.comments.filter((c) => c.deck === this.deck && String(c.id) === id)
    },
    openComments(): number { return this.cardComments.filter((c) => c.status === 'open').length },
    showCmt(): boolean { return this.cbox || this.cardComments.length > 0 },
    // 选择题只有题目牌组有 —— 它测的是"该用哪个模板"的辨别力, 语法卡没有这个维度
    hasQuiz(): boolean { return !this.isSyntax && (this.quiz.ideas.some((b) => b.state) || !!this.quiz.cx) },
    quizBlocks(): QuizBlock[] {
      const b = [...this.quiz.ideas]
      if (this.quiz.cx) b.push({ key: 'cx', label: '时间 / 空间复杂度？', state: this.quiz.cx })
      return b                                    // cx 关掉时整块不占位
    },
    verdict(): { cls: string; text: string } {
      if (!this.revealed) return { cls: '', text: '' }
      // 多选要**恰好**选中全部正确项才算对: 漏一个、多一个都是错
      const v = (st: QuizState | null) => (!st || !st.pick.length ? ''
        : st.pick.length === st.correct.length && st.pick.every((i) => st.correct.includes(i)) ? 'ok' : 'no')
      const vs = [...this.quiz.ideas.map((b) => v(b.state)), v(this.quiz.cx)].filter(Boolean)
      if (!vs.length) return { cls: '', text: '' }
      const allOk = vs.every((x) => x === 'ok')
      return {
        cls: allOk ? 'ok' : 'no',
        text: allOk ? '选择题全对' : `选择题错了 ${vs.filter((x) => x === 'no').length} 项`,
      }
    },
    // 标签就是答案的一部分 —— 「用什么结构 / 什么范式」正是揭晓时该对照的东西
    tagline(): string {
      const tag = (label: string, arr?: string[]) => (arr && arr.length ? `${label} <b>${esc(arr.join(' · '))}</b>` : '')
      return [tag('结构', this.d.structures), tag('范式', this.d.paradigms)].filter(Boolean).join('　　')
        || '<span class="rv-none">(还没打标签)</span>'
    },
    cxLine(): string {
      const cx = (this.d && this.d.complexity) || {}
      return [cx.time, cx.space].filter(Boolean).join('  /  ')
    },
    ideaHtml(): string {
      if (this.isSyntax) {
        return this.d.back
          ? this.host.md(this.d.back)
          : '<span class="rv-none">这张卡还没写背面 —— 点右边「改一下」补上</span>'
      }
      return this.d.answer
        ? this.host.md(this.d.answer)
        : '<span class="rv-none">还没写答案卡 —— 点右边「改一下」把刚才想的那套写进去</span>'
    },
    bodyHtml(): string {
      const item = this.items[this.active]
      if (!item) return ''
      return item.code !== undefined ? `<pre><code>${highlightPython(item.code)}</code></pre>` : this.host.md(item.md || '')
    },
    preview(): Record<number, number> { return (this.d && this.d.fsrs_preview) || {} },
    emptyMsg(): string {
      if (this.failMsg) return this.failMsg
      const unit = this.isSyntax ? '张' : '道'
      const other: Deck = this.isSyntax ? 'problems' : 'syntax'
      const rest = this.counts[other]
        ? `<br><span class="hint">「${DECK_LABEL[other]}」还有 ${this.counts[other]} ${other === 'syntax' ? '张' : '道'}</span>`
        : ''
      if (this.done) {
        return `这一轮复习完了 —— 共 ${this.done} ${unit} 🎉`
          + rest
      }
      return (this.isSyntax
        ? '今天没有到期的语法卡 🎉'
        : '今天没有到期的题 🎉') + rest
    },
  },

  methods: {
    fmtInterval,                                   // 模板里要用

    // 把当前队列快照发给后端存成 dashboard/session.json。队列仍然是每次开面板现算的,
    // 快照里只有 deferred(今天押过队尾的)会被 start() 经 /api/review/carry 读回来。
    // 失败了不影响复习, 顶多是关掉重开后押过的题回到原位。
    syncSession() {
      if (this.readOnly) { saveDefers(this.deck, this.deferred); return }   // 只读站没有写接口, 只留押队尾
      postJSON('/api/review/session', {
        open: this.open, deck: this.deck, mode: this.mode, done: this.done, total: this.total,
        current: this.d ? this.d.id : null, queue: this.queue, deferred: this.deferred,
      }).catch(() => { /* 存不上就算了, 这不是数据源 */ })
    },

    // 队列每次现算, 但今天这一轮里有两类题不能因为关掉重开就走样(见 server.review_carry):
    //   押过队尾的 -> 还在现算队列里, 挪回队尾;
    //   今天最后一次评 1 的 -> due 已是明天, 现算里没有, 追加到队尾。
    // 只动**现算队列里本来就有**或**牌组里还在**的 id —— 改了语法卡标题留下的旧 id 会被
    // 自然滤掉, "关掉重开就好"那条恢复路径照旧有效。
    async start() {
      const deck = this.deck
      const gen = ++this.startGen
      this.counts = this.host.badge()
      this.open = true
      this.d = null
      this.loading = true                 // 拉 carry 期间别闪"没有到期的题"
      this.loadComments()                 // 不等它: 批注是旁支, 慢了顶多晚一点显示
      let carry: { deferred?: (number | string)[]; again?: (number | string)[] } = { deferred: [], again: [] }
      if (!this.readOnly) {
        try {
          carry = await api(`/api/review/carry?deck=${deck}`)
        } catch (e) {
          console.error('[review] 拉今天的押队尾/评 1 记录失败, 按现算队列来', e)
        }
      } else {
        carry = { deferred: loadDefers(deck), again: this.writable ? this.host.again(deck) : [] }
      }
      // 等的时候又开了一次 / 切了牌组(都会再进 start(), 由新的那次接手), 或者已经关掉了
      if (gen !== this.startGen || !this.open) return
      this.loading = false
      // 每天上限 review_cap 张(plan.json, 默认 10): 今天已经评过的先扣掉。
      // 逾期堆得再多也不一次清 —— 多出来的留在明天的队列里, 不欠账也不补课。
      const queue = this.host.queue(this.mode, deck)
      const inDeck = new Set(this.host.rows(deck).map((p) => p.id))
      const deferred = (carry.deferred || []).filter((id) => inDeck.has(id))
      // 押了好几次的按最后一次的先后排, 和会话内 push 到队尾的效果一致
      const tail = [...new Set([...deferred].reverse())].reverse().filter((id) => queue.includes(id))
      const again = (carry.again || []).filter((id) => inDeck.has(id) && !queue.includes(id))
      this.queue = [...queue.filter((id) => !tail.includes(id)), ...tail, ...again]
      this.done = 0
      this.total = this.queue.length
      this.deferred = deferred             // 接着记, 不从零开始 —— 否则下次同步就把今天押过的冲掉了
      this.next()
    },

    // 换牌组 = **重开一轮**, 不是重排队列: 两组的 id 空间都不一样(整数 vs 字符串),
    // 混在一个 queue 里 next() 会拿着题号去语法卡里找。所以 done/total 一起清零。
    setDeck(k: Deck) {
      if (!DECKS.includes(k) || k === this.deck) return
      this.deck = k
      try { localStorage.setItem('rv-deck', k) } catch { /* 隐私模式 */ }
      this.start()
    },
    close() {
      this.open = false
      this.d = null
      this.editing = false
      this.syncSession()
    },
    toStats() { this.close(); this.host.openStats() },

    // 拉详情要是失败, 绝不能让 this.d / revealed 停在**上一道**题上 —— 那样卡面纹丝不动,
    // 看着像前端卡死, 而 1-4 还照样响应, 于是每按一次就给上一道重复记一次复习。
    // (真发生过: reviews.jsonl 里 #1 在 4 秒内被记了 6 次, #206 记了 4 次, stability
    //  一路 8→60 天。) 所以: 先落下 revealed, 失败就把题号放回队头 + 走收尾屏说明白。
    async next() {
      this.note = ''
      this.failMsg = ''
      this.editing = false
      this.amsg = ''
      this.attempt = ''                                 // 上一张写的别串到这张来
      this.cbox = false; this.cdraft = ''               // 批注草稿同理
      this.revealed = false                             // 先落下答案, 再去拉
      const id = this.queue.shift()
      if (id === undefined) { this.d = null; return }   // 队列空了 -> 收尾屏
      // 语法卡整组在 /api/syntax 里一次拉完(几十张而已), 不需要逐张再请求一次 ——
      // 所以这条路没有"拉详情失败"这种状态, 直接从内存里取。
      let d: any = null
      if (this.isSyntax) {
        d = this.host.rows('syntax').find((c) => c.id === id) || null
      } else {
        this.loading = true
        try {
          d = await api(`/api/problems/${id}`)
        } catch (e) {
          console.error('[review] 拉题详情失败', id, e)
        } finally {
          this.loading = false
        }
      }
      if (!d || d.id === undefined) {                    // 没拿到: id 放回队头, 不丢
        this.queue.unshift(id)
        this.d = null
        this.failMsg = this.isSyntax
          ? `⚠ 队列里的「${esc(String(id))}」在 syntax/*.md 里找不到了<br>`
            + `<span class="hint">多半是刚改了卡标题(改标题 = 换 id)。关掉重开就好</span>`
          : `⚠ 拉 #${id} 的详情失败(服务没起? 看 console)<br>`
            + `<span class="hint">这道题还在队列里 —— 关掉重开就接着问它</span>`
        this.syncSession()
        return
      }
      // 只读站: 导出的 fsrs / fsrs_preview 是导出那天的, 还没算上手机上评过的。
      // 行上的调度字段已经重放过(app.js 的 applyPending), 按它和今天现算按钮上的间隔
      if (this.readOnly) {
        const row = this.host.rows(this.deck).find((x) => x.id === id)
        const card = row && row.fsrs && Object.keys(row.fsrs).length ? row.fsrs : newCard()
        d = { ...d, fsrs: card, fsrs_preview: fsrsPreview(card, todayStr()) }
      }
      this.d = d
      this.quiz = this.host.quiz(this.isSyntax ? {} : this.d)
      this.active = 0
      this.$nextTick(() => { const c = this.$refs.card as HTMLElement | undefined; if (c) c.scrollTop = 0 })
      this.syncSession()
    },
    // 只读站用: 没有评分按钮, 空格 = 下一题。busy 同 rate() —— 连按两下空格
    // 会在上一道还没拉回来的时候再 shift 一个题号, 那道就被静默跳过了。
    async skip() {
      if (this.busy) return
      this.busy = true
      this.done++
      try { await this.next() } finally { this.busy = false }
    },

    // 换模式: 只重排**剩下**的题, 当前这道不动, done/total 也不重来
    setMode(m: QueueMode) {
      if (!RV_MODES.includes(m)) return
      this.mode = m
      try { localStorage.setItem('rv-mode', m) } catch { /* 隐私模式 */ }
      const byId = new Map(this.host.rows(this.deck).map((p) => [p.id, p]))
      this.queue = orderQueue(this.queue.map((id) => byId.get(id)).filter(Boolean), m, this.deck)
      this.syncSession()
    },

    pick(state: QuizState, i: number) {
      if (this.revealed) return                       // 揭晓后不能再改答案
      const has = state.pick.includes(i)              // 再点一下取消
      if (state.multi) state.pick = has ? state.pick.filter((x) => x !== i) : [...state.pick, i]
      else state.pick = has ? [] : [i]                // 单选: 点别的就换过去
    },
    optClass(state: QuizState, i: number) {
      const picked = state.pick.includes(i), right = state.correct.includes(i)
      if (!this.revealed) return { picked }
      // missed 只在多选里标: 单选没选的那项本来就是"没作答", 不算漏
      return { done: true, right, wrong: picked && !right, missed: state.multi && right && !picked }
    },

    reveal() {
      if (!this.d || this.revealed || this.busy) return
      // 焦点还留在默写框里的话, 接下来的 1-4 会被 onKey 的 TEXTAREA 那道闸放行 ——
      // 表现是"揭晓了但评不了分, 键盘像死了"。趁 DOM 还没重渲染(框是 v-if)先抬走焦点。
      const w = this.$refs.write as HTMLElement | undefined
      const cb = this.$refs.cbox as HTMLElement | undefined
      if (w && document.activeElement === w) w.blur()
      if (cb && document.activeElement === cb) cb.blur()
      this.revealed = true
      // 语法卡的背面就是全部, 没有次要 tab —— items 留空, 模板里那一块整个不占位
      this.items = this.isSyntax ? []
        : [{ name: '📝 笔记', md: this.d.note || '_(还没写笔记)_' },
          ...this.d.solutions.map((x: any) => ({ name: x.name, code: x.content }))]
      this.active = 0
    },

    // w = 跳进默写框。不自动 focus 是故意的 —— 一进卡就把焦点塞进 textarea 的话,
    // 空格就成了打空格, 原来"空格揭晓"的手感整个没了。
    focusWrite() {
      (this.$refs.write as HTMLElement | undefined)?.focus()
    },

    // 就地改答案卡: 复习时脑子正热, 这时候压缩成一句话最准
    startEdit() {
      if (!this.revealed || this.readOnly) return
      this.draft = (this.isSyntax ? this.d.back : this.d.answer) || ''
      this.editing = true
      this.$nextTick(() => (this.$refs.aedit as HTMLElement | undefined)?.focus())
    },
    cancelEdit() { this.editing = false },

    // 给 agent 的批注: 复习时只记「哪儿不对」, 不当场改 —— 攒进 dashboard/card-comments.jsonl,
    // 之后跟 agent 说一句「处理卡片批注」统一改(见 .claude/skills/card-comments)。
    // 和「改一下」的分工: 那个是自己一句话就能改完的; 这个是要查 note / 对全库口径 / 重写干扰项的。
    async loadComments() {
      if (this.readOnly) {                        // 只读站不导出批注, 只看得到自己记的、还没落进 main 的
        this.comments = this.host.pendingComments()
        return
      }
      try {
        this.comments = (await api('/api/card-comments')).comments || []
      } catch (e) { console.error('[review] 拉卡片批注失败', e) }
    },
    openComment() {
      if (!this.d || !this.writable) return
      this.cbox = true
      this.$nextTick(() => {
        (this.$refs.cmt as HTMLElement | undefined)?.scrollIntoView({ block: 'nearest' });
        (this.$refs.cbox as HTMLElement | undefined)?.focus()
      })
    },
    closeComment() {
      (this.$refs.cbox as HTMLElement | undefined)?.blur()
      this.cbox = false
    },
    async sendComment() {
      const text = this.cdraft.trim()
      if (!text || !this.d) return
      if (this.readOnly) {
        if (!this.writable) return
        this.host.record({ deck: this.deck, id: this.d.id, op: 'comment', title: this.d.title, text })
        this.comments = this.host.pendingComments()
        this.cdraft = ''
        this.closeComment()
        return
      }
      let r: any
      try {
        r = await postJSON('/api/card-comments', { deck: this.deck, id: this.d.id, title: this.d.title, text })
      } catch { r = null }
      if (!r || !r.ok) { this.note = `⚠ 批注没存上${r && r.error ? ': ' + r.error : '(服务没起?)'}`; return }
      this.comments.push(r.comment)
      this.cdraft = ''
      this.closeComment()
    },
    async dropComment(c: any) {
      let r: any
      try {
        r = await postJSON('/api/card-comments', { op: 'delete', cid: c.cid })
      } catch { r = null }
      if (!r || !r.ok) { this.note = `⚠ 没撤回${r && r.error ? ': ' + r.error : ''}`; return }
      this.comments = this.comments.filter((x) => x.cid !== c.cid)
    },
    async saveAnswer() {
      if (!this.editing) return
      const content = this.draft
      // 语法卡的背面存回 syntax/<主题>.md 的对应行区间(见 syntax.save_back), 题目的存 answer.md
      const [url, body] = this.isSyntax
        ? ['/api/syntax/card', { id: this.d.id, content }]
        : [`/api/problems/${this.d.id}/answer`, { content }]
      let r: any
      try {
        r = await postJSON(url, body, 'PUT')
      } catch { r = null }
      if (!r || !r.ok) { this.amsg = '没存上(只读站?)'; return }
      if (this.isSyntax) this.d.back = content; else this.d.answer = content
      this.editing = false
      this.amsg = '已存 ✓'
      setTimeout(() => { this.amsg = '' }, 1500)
    },

    // 押到队尾: 不评分 / 不写 FSRS / 不算进度, 只把这道题挪到本次会话的最后再问一遍。
    // 和评 1 的区别 —— 评 1 是**真的记一次复习**(写 reviews.jsonl, due 会变);
    // 这里表达的是"现在没空细看", 不该污染调度数据。
    defer() {
      if (!this.d || this.busy) return
      if (!this.queue.length) {                        // 后面没题了, 挪了还是它
        this.note = '⚠ 已经是本轮最后一道了 —— 队尾就在这儿'
        return
      }
      this.queue.push(this.d.id)                       // done/total 都不动: 这道题还欠着
      this.deferred.push(this.d.id)
      this.next()                                      // next() 里会同步给后端
    },

    // 暂停当前这道: 不评分, 从本轮队列里整个拿掉(押过队尾 / 评 1 追加的也一起), 以后也不再进队列,
    // 直到在详情页取消勾选。和押队尾的区别 —— 押队尾是"等会儿再问", 这个是"这阵子都别问"。
    async pause() {
      if (!this.d || this.busy || this.isSyntax || !this.writable) return
      const id = this.d.id
      this.busy = true
      let ok = false
      if (this.readOnly) {                         // 记成事件, 行上的 paused 由 record 就地写好
        this.host.record({ deck: 'problems', id, op: 'pause' })
        ok = true
      } else {
        try { ok = (await this.host.putMeta(id, { paused: true })).ok } catch { ok = false }
      }
      if (!ok) {
        this.busy = false
        this.note = '⚠ 没暂停成功(服务没起?) —— 这道还在'
        return
      }
      const p = this.host.rows('problems').find((x) => x.id === id)
      if (p && !p.paused) p.paused = todayStr()
      this.queue = this.queue.filter((x) => x !== id)
      this.deferred = this.deferred.filter((x) => x !== id)
      this.total = this.done + this.queue.length   // 这道不再算进本轮
      try {
        this.counts = this.host.refresh()
      } catch (e) { console.error('[review] 刷新看板失败', e) }
      try { await this.next() } finally { this.busy = false }
    },

    // busy 是**去重闸**, 不是转圈动画: 一次评分要走 POST -> 刷看板 -> 再 GET 下一题,
    // 这中间卡面还停在当前这道且 revealed=true, 手快按第二下就会给同一道题再记一次复习。
    // 服务端每条都照单全收(reviews.jsonl 里 #1 连记 6 次那次就是这么来的), 只能前端拦。
    async rate(r: number) {
      if (!this.revealed || this.busy || !this.writable) return
      const id = this.d.id
      this.busy = true
      if (this.readOnly) {
        // 只读站: 记一条事件(先存本机, 停手 2 秒推到 data 分支), 行上的调度字段由 record 就地重算。
        // 不会失败 —— 推不上去的留在本机, 下次联网再推
        this.host.record({ deck: this.deck, id, op: 'rate', rating: r as 1 | 2 | 3 | 4 })
        await this.afterRate(id, r)
        return
      }
      // 语法卡的 id 是 "主题/标题"(带中文和空格), 塞不进 URL 路径, 所以走 body
      const [url, body] = this.isSyntax
        ? ['/api/syntax/review', { id, rating: r }]
        : [`/api/review/${id}`, { rating: r }]
      let res: any
      try {
        res = await postJSON(url, body)
      } catch { res = null }
      if (!res || !res.ok) {
        this.busy = false
        // 只读站的 403 也走这里(static-shim 是 resolve 不是 reject)。写失败就**不推进**——
        // 假装评过了会让这道题的调度悄悄丢一次, 比停下来更糟。
        this.note = '⚠ 没记录下来(只读站或服务没起) —— 按「下一题」继续自测'
        return
      }
      // 就地更新内存里那一行, 免得为了一个 due 重拉整组。两个牌组的行是同形状的
      // (语法卡的调度字段在 /api/syntax 里就摊平到顶层了), 所以这段不用分叉。
      const p = this.host.rows(this.deck).find((x) => x.id === id)
      if (p) {
        p.due = res.card.due; p.reps = res.card.reps; p.stability = res.card.stability
        p.last_review = res.card.last_review; p.fsrs_state = res.card.state
        p.fsrs = res.card; p.fsrs_preview = res.preview
      }
      await this.afterRate(id, r)
    },
    // 评完之后两边一样的那半段: 评 1 排回队尾、刷看板、取下一题, 最后放开 busy
    async afterRate(id: number | string, r: number) {
      if (r === 1) { this.queue.push(id); this.total++ }   // 忘了 -> 本次会话末尾再问一遍
      this.host.reviewsChanged()
      this.done++
      // 看板重绘是**旁支**: 它抛了顶多是背后那屏没刷新, 不能连累复习推进。
      try {
        this.counts = this.host.refresh()
      } catch (e) { console.error('[review] 刷新看板失败', e) }
      try { await this.next() } finally { this.busy = false }
    },

    // 键盘由 app.js 末尾那个全局 handler 转进来 —— 保持和其它 overlay 同一套分发顺序
    onKey(e: KeyboardEvent): boolean {
      const cb = this.$refs.cbox as HTMLElement | undefined
      // 批注框里: 只认 Ctrl+Enter 存, 其余键都是打字 —— 必须在默写框那条 Ctrl+Enter 揭晓**之前**
      if (cb && document.activeElement === cb) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { this.sendComment(); return true }
        return false
      }
      if (this.editing && (e.ctrlKey || e.metaKey) && e.key === 's') { this.saveAnswer(); return true }
      // 默写框里空格是空格, 所以另给一个揭晓键。这条必须在下面那道修饰键闸**之前**
      if (!this.revealed && this.canWrite && (e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        this.reveal(); return true
      }
      if (e.ctrlKey || e.metaKey || e.altKey || e.isComposing || e.keyCode === 229) return false
      if (/^(INPUT|TEXTAREA|SELECT)$/.test((e.target as HTMLElement).tagName)) return false
      if (e.key === 'w' && !this.revealed && this.canWrite) { this.focusWrite(); return true }
      if (e.key === 'c' && this.writable) { this.openComment(); return true }
      if (e.key === ' ') {
        if (!this.revealed) this.reveal()
        else if (!this.writable) this.skip()    // 没连 GitHub 的只读站没有评分按钮, 空格 = 下一题
        // 本地站揭晓后不响应空格: 必须按 1-4, 防止手滑跳过一道没评分
        return true
      }
      if (e.key === '0') { this.defer(); return true }
      if (this.revealed && this.writable && '1234'.includes(e.key)) { this.rate(+e.key); return true }
      return false
    },
    onEsc() {
      const cb = this.$refs.cbox as HTMLElement | undefined
      const w = this.$refs.write as HTMLElement | undefined
      // 批注框里 Esc = 收起框, 草稿留在 cdraft 里(再按 c 还在)
      if (cb && document.activeElement === cb) { this.closeComment(); return }
      // 在默写框里按 Esc 只退出输入框。直接关面板会把刚写的一起吞掉(attempt 不存盘),
      // 而 Esc 恰恰是打字时最容易顺手按的那个键
      if (w && document.activeElement === w) { w.blur(); return }
      if (this.editing) this.cancelEdit()
      else this.close()
    },
  },
})
</script>

<template>
  <div class="overlay" :class="{ hidden: !open }" @click.self="close">
    <div class="detail review-detail">
      <div class="detail-head">
        <div>
          <span class="pill" v-text="pillText"></span>
          <span class="d-title" v-text="d ? d.title : ''"></span>
          <span class="hint" v-text="note || metaLine"></span>
        </div>
        <div class="rv-head-right">
          <!-- 两个牌组: 题目(meta.json) / 语法(syntax/*.md)。换组 = 重开一轮 -->
          <div class="groupby rv-deck" title="换牌组会重开一轮 —— 两组的 id 空间不一样, 不能混在一个队列里">
            <button v-for="k in DECKS" :key="k.k" class="gb-btn" :class="{ on: deck === k.k }"
                    @click="setDeck(k.k)">
              <span v-text="k.label"></span>
              <em v-if="counts[k.k]" class="rv-deck-n" v-text="counts[k.k]"></em>
            </button>
          </div>
          <div class="groupby rv-mode" title="只改队列顺序, 不改范围(到期的 + 还没进过复习的)">
            <button v-for="m in MODES" :key="m.k" class="gb-btn" :class="{ on: mode === m.k }"
                    @click="setMode(m.k)" v-text="m.label"></button>
          </div>
          <span class="rv-verdict" :class="verdict.cls" v-text="verdict.text"></span>
          <span class="hint" v-text="d ? (done + 1) + ' / ' + total : ''"></span>
          <button class="icon-btn" @click="close">✕</button>
        </div>
      </div>

      <div v-if="showEmpty" class="rv-empty">
        <span v-html="emptyMsg"></span>
        <br><button class="ghost rv-stats" @click="toStats">📈 看看复习进度</button>
      </div>

      <template v-else-if="d">
        <div class="rv-card" ref="card">
          <div>
            <div class="rv-ask" v-html="askText"></div>
            <div class="lc-desc" v-html="descHtml"></div>
            <div v-if="hasQuiz" class="rv-quiz">
              <div class="rv-q" v-for="b in quizBlocks" :key="b.key">
                <div class="rv-q-label" v-text="b.label"></div>
                <div class="rv-opts">
                  <span v-if="!b.state" class="rv-q-hint">(这题还没写选项)</span>
                  <template v-else>
                    <button v-for="(t, i) in b.state.opts" :key="i"
                            class="rv-opt" :class="optClass(b.state, i)" @click="pick(b.state, i)">
                      <span class="k" v-text="KEYS[i]"></span><span v-text="t"></span>
                    </button>
                  </template>
                </div>
              </div>
            </div>
            <!-- 默写框(只有语法卡有)。纯草稿纸: 不存盘、不判对错、不进 FSRS ——
                 揭晓后原样贴到答案上面自己比。之所以不自动判, 是因为「只保留符合条件的
                 字符」这种卡写法自由度太高, 机器判错会比不判更烦人。 -->
            <div v-if="canWrite && !revealed" class="rv-write">
              <div class="rv-q-label">默写一遍(可选)</div>
              <textarea id="rv-write-box" ref="write" v-model="attempt" spellcheck="false"
                        placeholder="默写…"></textarea>
              <div class="rv-q-hint"><b>w</b> 写 · <b>Ctrl+Enter</b> 揭晓</div>
            </div>
          </div>

          <!-- 给 agent 的批注(dashboard/card-comments.jsonl)。放在答案卡**上面**:
               揭晓后底下还有笔记 / 解法 tab, 放最底下一打开就在视口外。
               揭晓前只报条数不显示内容 —— 批注和 agent 的回复多半会提到正确答案 -->
          <div v-if="showCmt" class="rv-cmt" ref="cmt">
            <div class="rv-q-label">给 agent 的批注</div>
            <template v-if="revealed">
              <div v-for="c in cardComments" :key="c.cid" class="rv-cmt-item" :class="c.status">
                <span class="rv-cmt-st" v-text="CMT_ST[c.status] || c.status"></span>
                <span class="rv-cmt-text" v-text="c.text"></span>
                <span class="hint" v-text="c.date"></span>
                <span v-if="c.pending" class="hint" title="在 data 分支上等电脑的 server.py 拉下来">未落盘</span>
                <span v-else-if="c.status === 'open'" class="rv-cmt-x" @click="dropComment(c)">撤回</span>
                <div v-if="c.reply" class="rv-cmt-reply" v-text="'↳ ' + c.reply"></div>
              </div>
            </template>
            <div v-else-if="cardComments.length" class="rv-q-hint"
                 v-text="'这张卡有 ' + cardComments.length + ' 条批注 —— 揭晓后显示(防剧透)'"></div>
            <template v-if="cbox">
              <textarea id="rv-cmt-box" ref="cbox" v-model="cdraft" spellcheck="false"
                        placeholder="这张卡哪儿不对…"></textarea>
              <div class="rv-q-hint"><button class="ghost" :disabled="!cdraft.trim()" @click="sendComment">存</button>
                <b>Ctrl+Enter</b> 存 · <b>Esc</b> 收起</div>
            </template>
          </div>

          <!-- 答案卡: 标签 + 复杂度 + 一句话思路。note/解法退成次要 tab -->
          <div v-if="revealed" id="rv-answer">
            <!-- 你刚才写的, 原样贴在答案卡**上面** —— 要比的两半挨着才比得动 -->
            <div v-if="mine" class="rv-mine">
              <div class="rv-q-label">你写的</div>
              <pre v-text="mine"></pre>
            </div>
            <div class="rv-acard">
              <div class="rv-acard-head">
                <!-- 标签和复杂度是**题目**答案卡的一部分(正是揭晓时该对照的东西);
                     语法卡没有这两样, 那一行换成它出自哪个文件 -->
                <template v-if="!isSyntax">
                  <span class="rv-tagline" v-html="tagline"></span>
                  <span v-if="cxLine" class="rv-cx" v-text="cxLine"></span>
                </template>
                <span v-else class="rv-tagline">来自 <b v-text="d.file"></b></span>
                <span v-if="!readOnly" class="rv-aedit" title="双击那段答案也能编辑"
                      @click="editing ? cancelEdit() : startEdit()"
                      v-text="editing ? 'Ctrl+S 保存 · Esc 取消' : '改一下'"></span>
                <span class="msg" v-text="amsg"></span>
              </div>
              <div v-show="!editing" class="rv-idea" title="双击编辑"
                   @dblclick="startEdit" v-html="ideaHtml"></div>
              <div v-if="!isSyntax && d.pit" class="rv-pit"><b>坑</b><span v-text="d.pit"></span></div>
              <textarea v-show="editing" id="rv-aedit-box" ref="aedit" v-model="draft"
                        spellcheck="false" placeholder="一句话思路… Ctrl+S 保存，Esc 取消"></textarea>
            </div>
            <!-- 语法卡的背面就是全部, items 是空的 -> 次要 tab 整块不出现 -->
            <template v-if="items.length">
              <div class="tabs">
                <button v-for="(x, k) in items" :key="k" class="tab" :class="{ on: active === k }"
                        @click="active = k" v-text="x.name"></button>
              </div>
              <div class="rv-body" v-html="bodyHtml"></div>
            </template>
          </div>
        </div>

        <div class="rv-foot">
          <button v-if="!revealed" class="rv-reveal" @click="reveal">显示答案 <em>空格</em></button>
          <!-- 没连 GitHub 的只读站没有写接口: 没有评分按钮, 只有单纯的「下一题」自测 -->
          <div v-else-if="writable" class="rv-rate">
            <button v-for="r in [1, 2, 3, 4]" :key="r" class="rv-btn" :data-r="r" @click="rate(r)">
              <b v-text="RATE[r][0]"></b>
              <i v-text="fmtInterval(preview[r] || 0)"></i>
              <u v-text="r + ' · ' + RATE[r][1]"></u>
            </button>
          </div>
          <button v-else class="rv-next" @click="skip">下一题 <em>空格</em></button>
          <button class="ghost rv-defer" :class="{ off: !queue.length }" @click="defer"
                  title="不评分 · 不写 FSRS —— 只把当前这张挪到本次会话的最后再问一遍">↓ 押到队尾 <em>0</em></button>
          <button v-if="!isSyntax && writable" class="ghost rv-pause" @click="pause"
                  title="这阵子都别问: 不评分, 以后不进复习队列, interval 一起冻住 —— 在详情页取消勾选恢复">⏸ 暂停</button>
          <button v-if="writable" class="ghost rv-cmt-btn" @click="openComment"
                  title="给 agent 留一句这张卡哪儿不对 —— 攒着让 agent 统一改, 不评分、不影响调度">💬 批注 <em>c</em><b v-if="openComments" v-text="openComments"></b></button>
        </div>
      </template>
    </div>
  </div>
</template>
