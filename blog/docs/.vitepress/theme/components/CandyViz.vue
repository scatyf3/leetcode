<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'

// combinatorics.md 2929 的容斥演示：<CandyViz cases="6,2;5,2;9,2" />（每组是 n,limit）。
// 三角形里每个点是一种分法 (a, b, c)，三个角是某个孩子全拿；点上的数字 = 目前被算了几次。
// 一步一项：ways(n) 全部 +1，再逐个减「某人超限」、加回「两人都超限」、减「三人都超限」。
type P = [number, number, number]
interface Step {
  cnt: number[]
  msg: string
  k: number              // 第几项（terms 下标），结束那一步 = terms.length
  S?: number[]           // 这一项指定超限的孩子
  sign?: number
  changed: Set<number>
}
interface Term { S: number[]; sign: number; m: number; w: number }
interface Run { n: number; limit: number; L: number; pts: P[]; terms: Term[]; steps: Step[]; ans: number; truth: number; tab: string }

const ways = (m: number) => (m < 0 ? 0 : ((m + 2) * (m + 1)) / 2)
const fmt = (p: P) => `(${p.join(',')})`
const who = (S: number[]) => S.map((i) => i + 1).join('、')
const TERMS = [[], [0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]]

function build(n: number, limit: number): Run {
  const L = limit + 1
  const pts: P[] = []
  for (let a = n; a >= 0; a--) for (let b = n - a; b >= 0; b--) pts.push([a, b, n - a - b])
  const cnt = pts.map(() => 0)
  const terms: Term[] = []
  const steps: Step[] = []

  TERMS.forEach((S, k) => {
    const sign = S.length % 2 ? -1 : 1
    const m = n - S.length * L
    const w = ways(m)
    const changed = new Set<number>()
    pts.forEach((p, i) => { if (S.every((c) => p[c] >= L)) { cnt[i] += sign; changed.add(i) } })
    terms.push({ S, sign, m, w })

    let msg: string
    if (S.length === 0) {
      msg = `隔板法：a + b + c = ${n} 一共 ways(${n}) = ${w} 种分法，每个点是一种，先都算 1 次。`
    } else {
      const give = S.length === 1 ? `先给他 ${L} 颗` : `${S.length === 2 ? '两' : '三'}人各先塞 ${L} 颗`
      const verb = sign < 0 ? '减' : '加回'
      const what = S.length === 1 ? `孩子 ${who(S)} 超限` : S.length === 2 ? `孩子 ${who(S)} 都超限` : '3 个孩子都超限'
      if (m < 0) {
        msg = `${verb}「${what}」：${give}，糖不够，ways(${m}) = 0，这一项是空的。`
      } else {
        msg = `${verb}「${what}」：${give}，剩下 ${m} 颗随便分 → ways(${m}) = ${w} 个点，每个 ${sign < 0 ? '−1' : '+1'}。`
        if (S.length === 1 && k === 1) msg += `这块是一个缩小的三角形，形状和整个一样，所以点数也是 ways(·)。`
        if (S.length === 2) msg += `这些点刚才被两块同时盖住、减了两次，现在回到 0。`
        if (S.length === 3) msg += `这些点 +1 −3 +3 = 1，还得再减一次才是 0。`
      }
      if (k === 3) {
        const dbl = pts.filter((_, i) => cnt[i] < 0)
        if (dbl.length) msg += `　现在 ${dbl.slice(0, 3).map(fmt).join(' ')}${dbl.length > 3 ? ' …' : ''} 是负数：被减多了，后面要加回来。`
      }
    }
    steps.push({ cnt: [...cnt], msg, k, S, sign, changed })
  })

  const ans = terms.reduce((s, t) => s + t.sign * t.w, 0)
  const good = pts.filter((p) => p.every((x) => x <= limit))
  const truth = good.length
  const left = pts.filter((_, i) => cnt[i] === 1)
  steps.push({
    cnt: [...cnt], k: TERMS.length, changed: new Set(),
    msg: `最后还算 1 次的点就是答案，一共 ${ans} 种${left.length && left.length <= 7 ? '：' + left.map(fmt).join(' ') : ''}；其余的点都被消成 0 了。`,
  })
  const most = Math.min(3, Math.floor(n / L))
  const tab = `n=${n}, limit=${limit}` + (most >= 2 ? `（${most} 人可同时超限）` : '（不会两人同时超限）')
  return { n, limit, L, pts, terms, steps, ans, truth, tab }
}

const props = defineProps<{ cases: string }>()
const runs = computed(() => props.cases.split(';').map((c) => c.split(',').map(Number)).filter(([n, l]) => n >= 1 && l >= 0).map(([n, l]) => build(n, l)))
const ti = ref(0)
const si = ref(0)
const run = computed(() => runs.value[ti.value])
const step = computed(() => run.value.steps[si.value])
const last = computed(() => si.value === run.value.steps.length - 1)
const running = computed(() => run.value.terms.slice(0, step.value.k + 1).reduce((s, t) => s + t.sign * t.w, 0))

// ---------- 几何：孩子 1 左下角，孩子 2 右下角，孩子 3 顶上 ----------
const W = 560, SIDE = 420, TOP = 62
const TH = (SIDE * Math.sqrt(3)) / 2
const H = TOP + TH + 52
const V = [[(W - SIDE) / 2, TOP + TH], [(W + SIDE) / 2, TOP + TH], [W / 2, TOP]]
const pos = (p: P) => {
  const n = run.value.n
  return [0, 1].map((d) => (p[0] * V[0][d] + p[1] * V[1][d] + p[2] * V[2][d]) / n) as [number, number]
}
const R = computed(() => Math.min(15, (SIDE / run.value.n) * 0.36))

// 指定的孩子都超限 → 角上一个小三角形：其余 m 颗全给某一个人，就是它的三个顶点
const region = computed(() => {
  const S = step.value.S
  if (!S || !S.length) return null
  const { n, L } = run.value
  const m = n - S.length * L
  if (m < 0) return null
  const corners = [0, 1, 2].map((k) => {
    const p = [0, 1, 2].map((c) => (S.includes(c) ? L : 0) + (c === k ? m : 0)) as P
    return pos(p)
  })
  const cx = (corners[0][0] + corners[1][0] + corners[2][0]) / 3
  const cy = (corners[0][1] + corners[1][1] + corners[2][1]) / 3
  const pad = R.value + 4
  if (m === 0) return { dot: [cx, cy], r: pad }
  const out = corners.map(([x, y]) => {
    const dx = x - cx, dy = y - cy, d = Math.hypot(dx, dy)
    return [x + (dx / d) * pad * 2, y + (dy / d) * pad * 2]
  })
  return { poly: out.map((q) => q.join(',')).join(' ') }
})
const cls = (v: number) => (v >= 1 ? 'one' : v === 0 ? 'zero' : v === -1 ? 'neg' : 'neg2')
const showNum = (v: number) => (v < 0 ? `−${-v}` : `${v}`)

let timer: ReturnType<typeof setInterval> | undefined
const playing = ref(false)
function stop() { if (timer) clearInterval(timer); timer = undefined; playing.value = false }
function go(k: number) { si.value = Math.max(0, Math.min(run.value.steps.length - 1, k)) }
function play() {
  if (playing.value) return stop()
  if (last.value) si.value = 0
  playing.value = true
  timer = setInterval(() => { if (last.value) stop(); else si.value++ }, 1600)
}
function pick(k: number) { stop(); ti.value = k; si.value = 0 }
onUnmounted(stop)
</script>

<template>
  <figure v-if="run" class="cv">
    <div v-if="runs.length > 1" class="cv-tabs">
      <button v-for="(r, k) in runs" :key="k" :class="{ on: k === ti }" @click="pick(k)">{{ r.tab }}</button>
    </div>

    <div class="cv-terms">
      <span v-for="(t, j) in run.terms" :key="j" class="cv-term"
            :class="{ now: j === step.k, todo: j > step.k, empty: t.w === 0 }">
        <span class="cv-tl">{{ t.sign < 0 ? '−' : j ? '+' : '' }}ways({{ t.m }})</span>
        <span class="cv-tv">{{ t.w === 0 ? '' : t.sign < 0 ? '−' : j ? '+' : '' }}{{ t.w }}</span>
        <span class="cv-tw">{{ t.S.length ? '孩子 ' + who(t.S) : '全部' }}</span>
      </span>
      <span class="cv-sum">= {{ running }}</span>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="cv-svg" role="img" :aria-label="step.msg">
      <polygon :points="V.map((q) => q.join(',')).join(' ')" class="cv-frame" />
      <template v-if="region">
        <polygon v-if="region.poly" :points="region.poly" class="cv-region" :class="step.sign! < 0 ? 'minus' : 'plus'" />
        <circle v-else :cx="region.dot![0]" :cy="region.dot![1]" :r="region.r" class="cv-region" :class="step.sign! < 0 ? 'minus' : 'plus'" />
      </template>

      <g v-for="(p, i) in run.pts" :key="i">
        <circle :cx="pos(p)[0]" :cy="pos(p)[1]" :r="R" class="cv-pt" :class="[cls(step.cnt[i]), { hit: step.changed.has(i) }]">
          <title>{{ fmt(p) }}：现在算了 {{ showNum(step.cnt[i]) }} 次</title>
        </circle>
        <text :x="pos(p)[0]" :y="pos(p)[1]" class="cv-num" :class="cls(step.cnt[i])" :style="{ fontSize: R * 0.95 + 'px' }">{{ showNum(step.cnt[i]) }}</text>
      </g>

      <text :x="V[0][0]" :y="V[0][1] + R + 26" class="cv-corner" text-anchor="middle">孩子 1 全拿 ({{ run.n }},0,0)</text>
      <text :x="V[1][0]" :y="V[1][1] + R + 26" class="cv-corner" text-anchor="middle">孩子 2 全拿 (0,{{ run.n }},0)</text>
      <text :x="V[2][0]" :y="V[2][1] - 2 * (R + 4) - 8" class="cv-corner" text-anchor="middle">孩子 3 全拿 (0,0,{{ run.n }})</text>
    </svg>

    <div class="cv-legend">
      <span><i class="cv-sw one" />算 1 次</span>
      <span><i class="cv-sw zero" />算 0 次</span>
      <span><i class="cv-sw neg" />算 −1 次</span>
      <span><i class="cv-sw neg2" />算 −2 次</span>
      <span><i class="cv-sw hit" />这一步改动的点</span>
    </div>
    <div class="cv-msg">{{ step.msg }}</div>
    <div class="cv-ctl">
      <button @click="stop(); go(0)" title="回到开头">⏮</button>
      <button @click="stop(); go(si - 1)" :disabled="si === 0">◀</button>
      <button class="play" @click="play">{{ playing ? '暂停' : '播放' }}</button>
      <button @click="stop(); go(si + 1)" :disabled="last">▶</button>
      <button @click="stop(); go(run.steps.length - 1)" title="跳到结果">⏭</button>
      <span class="cv-count">{{ si }} / {{ run.steps.length - 1 }}</span>
      <span v-if="last" class="cv-verdict" :class="run.ans === run.truth ? 'ok' : 'bad'">
        {{ run.ans === run.truth ? '✓' : '✗' }} 答案 {{ run.ans }}，和逐个检查 a, b, c ≤ {{ run.limit }} 数出来的 {{ run.truth }} 一致
      </span>
    </div>
  </figure>
</template>

<style scoped>
.cv {
  margin: 20px 0; padding: 12px 14px 10px; border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.cv-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.cv-tabs button, .cv-ctl button {
  font-size: 13px; padding: 3px 10px; border-radius: 6px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer;
}
.cv-tabs button.on { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.cv-ctl button:disabled { opacity: .4; cursor: default; }
.cv-ctl button.play { min-width: 52px; }

.cv-terms { display: flex; flex-wrap: wrap; align-items: stretch; gap: 4px; font-family: var(--vp-font-family-mono); }
.cv-term {
  display: inline-flex; flex-direction: column; align-items: center; padding: 3px 6px; border-radius: 6px;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg); transition: opacity .2s;
}
.cv-term.todo { opacity: .35; }
.cv-term.empty .cv-tv { color: var(--vp-c-text-3); }
.cv-term.now { border-color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.cv-tl { font-size: 11px; color: var(--vp-c-text-2); }
.cv-tv { font-size: 15px; font-weight: 600; color: var(--vp-c-text-1); }
.cv-tw { font-size: 10px; color: var(--vp-c-text-3); font-family: var(--vp-font-family-base); }
.cv-sum { align-self: center; font-size: 16px; font-weight: 600; margin-left: 6px; color: var(--vp-c-brand-1); }

.cv-svg { display: block; width: 100%; max-width: 560px; height: auto; margin: 8px auto 2px; overflow: visible; }
.cv-frame { fill: none; stroke: var(--vp-c-divider); stroke-width: 1; }
.cv-region { stroke-width: 1.5; stroke-dasharray: 5 3; stroke-linejoin: round; }
.cv-region.minus { fill: var(--vp-c-red-soft); stroke: var(--vp-c-red-1); }
.cv-region.plus { fill: var(--vp-c-indigo-soft); stroke: var(--vp-c-indigo-1); }

.cv-pt { stroke-width: 1; transition: fill .25s, stroke .25s; }
.cv-pt.one { fill: var(--vp-c-green-soft); stroke: var(--vp-c-green-1); }
.cv-pt.zero { fill: var(--vp-c-bg); stroke: var(--vp-c-text-3); stroke-dasharray: 2 2; }
.cv-pt.neg { fill: var(--vp-c-red-soft); stroke: var(--vp-c-red-1); }
.cv-pt.neg2 { fill: var(--vp-c-red-3); stroke: var(--vp-c-red-1); }
.cv-pt.hit { stroke: var(--vp-c-brand-1); stroke-width: 2.5; stroke-dasharray: none; }
.cv-num { text-anchor: middle; dominant-baseline: central; font-family: var(--vp-font-family-mono); fill: var(--vp-c-text-1); pointer-events: none; }
.cv-num.zero { fill: var(--vp-c-text-3); }
.cv-num.neg, .cv-num.neg2 { fill: var(--vp-c-red-1); font-weight: 600; }
.cv-num.neg2 { fill: var(--vp-c-white); }
.cv-corner { font-size: 12px; fill: var(--vp-c-text-2); }

.cv-legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: var(--vp-c-text-2); }
.cv-legend span { display: inline-flex; align-items: center; gap: 5px; }
.cv-sw { display: inline-block; width: 12px; height: 12px; border-radius: 50%; border: 1px solid var(--vp-c-text-3); }
.cv-sw.one { background: var(--vp-c-green-soft); border-color: var(--vp-c-green-1); }
.cv-sw.zero { background: var(--vp-c-bg); border-style: dashed; }
.cv-sw.neg { background: var(--vp-c-red-soft); border-color: var(--vp-c-red-1); }
.cv-sw.neg2 { background: var(--vp-c-red-3); border-color: var(--vp-c-red-1); }
.cv-sw.hit { background: transparent; border: 2.5px solid var(--vp-c-brand-1); }

.cv-msg {
  margin: 8px 0; padding: 8px 10px; min-height: 3.4em; border-radius: 6px; font-size: 14px; line-height: 1.5;
  background: var(--vp-c-bg); border-left: 3px solid var(--vp-c-brand-1);
}
.cv-ctl { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.cv-count { font-size: 12px; color: var(--vp-c-text-3); margin-left: 4px; font-variant-numeric: tabular-nums; }
.cv-verdict { font-size: 13px; font-weight: 600; margin-left: 6px; }
.cv-verdict.ok { color: var(--vp-c-green-1); }
.cv-verdict.bad { color: var(--vp-c-red-1); }
</style>
