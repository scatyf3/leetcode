<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'

// intervals.md 里的单步演示：<IntervalViz cases="sched-end,sched-start" />。
// 多个 case 渲染成 tab，同一组输入换排序键对比；每一步给出每个区间的状态 + 一句话说明。
type IV = [number, number]
type St = 'pending' | 'kept' | 'merged' | 'drop' | 'cand' | 'done'
interface Step {
  st: St[]
  msg: string
  i?: number                          // 当前在看第几行
  mark?: { t: number; label: string } // 竖线：end / reach / res[-1].end / 时刻
  band?: IV[]                         // 底下那一行：res 或已覆盖的段
  curve?: [number, number][]          // 扫描线：同时进行数
}
interface Run {
  tab: string
  sort: string
  input: IV[]
  rows: IV[]
  key?: [string, (v: IV) => number]
  legend: [St, string][]
  steps: Step[]
  verdict: string
  ok: boolean
  bandLabel?: string
  T?: number
  maxY?: number
}

const fmt = (v: IV) => `[${v[0]},${v[1]}]`
const KEYS = {
  start: (v: IV) => v[0],
  end: (v: IV) => v[1],
  len: (v: IV) => v[1] - v[0],
}
const sortBy = (ivs: IV[], k: keyof typeof KEYS) => [...ivs].sort((a, b) => KEYS[k](a) - KEYS[k](b))
const overlap = (a: IV, b: IV) => a[0] < b[1] && b[0] < a[1] // 435 口径：端点相碰不算

// ---------- §1 合并 ----------

function mergeTrue(ivs: IV[]): IV[] {
  const res: IV[] = []
  for (const [s, e] of sortBy(ivs, 'start')) {
    const last = res[res.length - 1]
    if (last && s <= last[1]) last[1] = Math.max(last[1], e)
    else res.push([s, e])
  }
  return res
}

function merge(ivs: IV[], k: 'start' | 'end'): Run {
  const rows = sortBy(ivs, k)
  const st: St[] = rows.map(() => 'pending')
  const res: IV[] = []
  const snap = () => res.map((v) => [...v] as IV)
  const steps: Step[] = [{ st: [...st], msg: `按 ${k} 排好序，res 为空。`, band: [] }]
  rows.forEach(([s, e], i) => {
    const last = res[res.length - 1]
    let msg: string
    if (last && s <= last[1]) {
      const back = s < last[0]
      last[1] = Math.max(last[1], e)
      st[i] = 'merged'
      msg = `start=${s} ≤ res[-1].end，吸收 → res[-1] 变成 ${fmt(last)}。`
      if (back) msg += `但 start=${s} 跑到了 res[-1].start 左边：它本该把更早的段也吞掉，模板只看 res[-1]，不回头。`
    } else {
      msg = last ? `start=${s} > res[-1].end=${last[1]}，不重叠 → 开新的。` : `第一个，直接放进 res。`
      res.push([s, e])
      st[i] = 'kept'
    }
    steps.push({ st: [...st], msg, i, band: snap(), mark: { t: res[res.length - 1][1], label: 'res[-1].end' } })
  })
  const truth = mergeTrue(ivs)
  const ok = JSON.stringify(truth) === JSON.stringify(res)
  return {
    tab: `按 ${k} 排`,
    sort: k === 'start' ? 'sort by start ✓' : 'sort by end ✗',
    input: ivs, rows, steps, ok,
    key: [k, KEYS[k]],
    legend: [['kept', '开新的'], ['merged', '被吸收']],
    bandLabel: 'res',
    verdict: `res = ${res.map(fmt).join(' ')}` + (ok ? '' : `，正确答案是 ${truth.map(fmt).join(' ')}`),
  }
}

// ---------- §2 调度 ----------

function bestKeep(ivs: IV[]) {
  let n = 0, end = -Infinity
  for (const [s, e] of sortBy(ivs, 'end')) if (s >= end) { n++; end = e }
  return n
}

function schedule(ivs: IV[], k: 'start' | 'end' | 'len'): Run {
  const rows = sortBy(ivs, k)
  const st: St[] = rows.map(() => 'pending')
  const kept: number[] = []
  let end = -Infinity
  const steps: Step[] = [{ st: [...st], msg: `按 ${k === 'len' ? '长度' : k} 排好序，一个个看：和已保留的不冲突就留。` }]
  rows.forEach((v, i) => {
    const hit = kept.find((j) => overlap(rows[j], v))
    let msg: string
    if (hit === undefined) {
      st[i] = 'kept'
      kept.push(i)
      msg = k === 'len'
        ? `${fmt(v)} 长度 ${v[1] - v[0]}，和已保留的都不重叠 → 留。`
        : `start=${v[0]} ≥ end=${end === -Infinity ? '-∞' : end}，不重叠 → 留，end = ${v[1]}。`
      end = Math.max(end, v[1])
    } else {
      st[i] = 'drop'
      msg = k === 'len'
        ? `${fmt(v)} 和已保留的 ${fmt(rows[hit])} 重叠 → 删。`
        : `start=${v[0]} < end=${end}，重叠 → 删。`
    }
    steps.push({ st: [...st], msg, i, mark: k === 'len' || end === -Infinity ? undefined : { t: end, label: `end = ${end}` } })
  })
  const n = rows.length, best = bestKeep(ivs), got = kept.length
  return {
    tab: { start: '按 start 排', end: '按 end 排', len: '按长度排' }[k],
    sort: k === 'end' ? 'sort by end ✓' : `sort by ${k} ✗`,
    input: ivs, rows, steps,
    key: [k, KEYS[k]],
    legend: [['kept', '保留'], ['drop', '删']],
    ok: got === best,
    verdict: `保留 ${got} 个，删 ${n - got} 个` + (got === best ? '' : `；最优是保留 ${best} 个、删 ${n - best} 个`),
  }
}

// 按 start 排也能救：冲突时留 end 小的那个
function scheduleStartMin(ivs: IV[]): Run {
  const rows = sortBy(ivs, 'start')
  const st: St[] = rows.map(() => 'pending')
  let end = -Infinity, cur = -1, removed = 0
  const steps: Step[] = [{ st: [...st], msg: '按 start 排好序。区别只在冲突时：两个里留 end 小的。' }]
  rows.forEach(([s, e], i) => {
    let msg: string
    if (s >= end) {
      st[i] = 'kept'
      msg = `start=${s} ≥ end=${end === -Infinity ? '-∞' : end}，不重叠 → 留，end = ${e}。`
      cur = i; end = e
    } else if (e < end) {
      removed++
      st[cur] = 'drop'; st[i] = 'kept'
      msg = `重叠。它的 end=${e} 比当前保留的 ${fmt(rows[cur])} 小 → 删旧的、留它，end = ${e}。`
      cur = i; end = e
    } else {
      removed++
      st[i] = 'drop'
      msg = `重叠。它的 end=${e} ≥ ${end} → 留旧的、删它。`
    }
    steps.push({ st: [...st], msg, i, mark: { t: end, label: `end = ${end}` } })
  })
  const n = rows.length, best = n - bestKeep(ivs)
  return {
    tab: '按 start 排 + 冲突留小 end',
    sort: 'sort by start，冲突时 end = min ✓',
    input: ivs, rows, steps,
    key: ['start', KEYS.start],
    legend: [['kept', '保留'], ['drop', '删']],
    ok: removed === best,
    verdict: `删 ${removed} 个` + (removed === best ? '' : `；最优是删 ${best} 个`),
  }
}

// ---------- §2.5 覆盖 ----------

function cover(clips: IV[], T: number): Run {
  const rows = sortBy(clips, 'start')
  const st: St[] = rows.map(() => 'pending')
  let reach = 0, nxt = 0, cnt = 0, i = 0, best = -1
  const steps: Step[] = [{ st: [...st], msg: `按 start 排好序，reach = 0，目标盖满 [0,${T}]。`, band: [], mark: { t: 0, label: 'reach = 0' } }]
  let ok = true
  while (reach < T) {
    while (i < rows.length && rows[i][0] <= reach) {
      st[i] = 'cand'
      if (rows[i][1] > nxt) { nxt = rows[i][1]; best = i }
      steps.push({ st: [...st], i, band: [[0, reach]], mark: { t: reach, label: `reach = ${reach}` },
        msg: `start=${rows[i][0]} ≤ reach=${reach}，够得着 → 进候选，nxt = ${nxt}。` })
      i++
    }
    if (nxt <= reach) { ok = false; steps.push({ st: [...st], msg: '推不动了，覆盖不了。' }); break }
    st.forEach((s, j) => { if (s === 'cand') st[j] = j === best ? 'kept' : 'drop' })
    reach = nxt; cnt++
    steps.push({ st: [...st], i: best, band: [[0, reach]], mark: { t: reach, label: `reach = ${reach}` },
      msg: `候选里 ${fmt(rows[best])} 推得最远 → 只选它，其余丢掉。reach = ${reach}，cnt = ${cnt}。` })
  }
  return {
    tab: '按 start 排，挑最大 end',
    sort: 'sort by start，候选里取 max end ✓',
    input: clips, rows, steps, T, ok,
    key: ['start', KEYS.start],
    legend: [['cand', '够得着的候选'], ['kept', '选中'], ['drop', '没选']],
    bandLabel: '已覆盖',
    verdict: `用了 ${cnt} 段`,
  }
}

function coverByEnd(clips: IV[], T: number): Run {
  const rows = sortBy(clips, 'end')
  const st: St[] = rows.map(() => 'pending')
  let reach = 0, cnt = 0
  const steps: Step[] = [{ st: [...st], msg: `套 §2 的思路按 end 排：够得着、又能往前推就收下。`, band: [], mark: { t: 0, label: 'reach = 0' } }]
  rows.forEach(([s, e], i) => {
    if (reach >= T) return
    let msg: string
    if (s <= reach && e > reach) {
      st[i] = 'kept'; reach = e; cnt++
      msg = `start=${s} 够得着，end=${e} 能往前推 → 收下，reach = ${e}，cnt = ${cnt}。`
    } else {
      st[i] = 'drop'
      msg = s > reach ? `start=${s} > reach=${reach}，够不着 → 跳过。` : `end=${e} ≤ reach=${reach}，推不动 → 跳过。`
    }
    steps.push({ st: [...st], msg, i, band: [[0, reach]], mark: { t: reach, label: `reach = ${reach}` } })
  })
  const best = cover(clips, T).steps.filter((x) => x.msg.startsWith('候选里')).length
  return {
    tab: '按 end 排（套 §2）',
    sort: 'sort by end ✗',
    input: clips, rows, steps, T,
    key: ['end', KEYS.end],
    legend: [['kept', '收下'], ['drop', '跳过']],
    bandLabel: '已覆盖',
    ok: cnt === best,
    verdict: `用了 ${cnt} 段` + (cnt === best ? '' : `；最少只要 ${best} 段`),
  }
}

// ---------- §3 扫描线 ----------

function sweep(ivs: IV[]): Run {
  const rows = sortBy(ivs, 'start')
  const st: St[] = rows.map(() => 'pending')
  // 同一时刻 -1 排在 +1 前面：端点相碰不算重叠（会议室口径）
  const ev = rows.flatMap(([s, e], k) => [[s, 1, k], [e, -1, k]]).sort((a, b) => a[0] - b[0] || a[1] - b[1])
  let cur = 0, best = 0
  const curve: [number, number][] = [[rows[0][0], 0]]
  const steps: Step[] = [{ st: [...st], msg: '不排区间，把每个 [s,e] 拆成 (s,+1) 和 (e,−1) 两个事件，按时刻排。', curve: [...curve] }]
  for (const [t, d, k] of ev) {
    st[k] = d > 0 ? 'kept' : 'done'
    curve.push([t, cur])
    cur += d
    best = Math.max(best, cur)
    curve.push([t, cur])
    steps.push({ st: [...st], i: k, curve: [...curve], mark: { t, label: `t = ${t}` },
      msg: `t=${t}：${fmt(rows[k])} ${d > 0 ? '开始，+1' : '结束，−1'} → 同时进行 ${cur} 个，最多 ${best} 个。` })
  }
  return {
    tab: '扫描线',
    sort: 'sort events by (t, delta)',
    input: ivs, rows, steps,
    legend: [['kept', '进行中'], ['done', '已结束']],
    ok: true,
    maxY: best,
    verdict: `最多同时 ${best} 个 → 要 ${best} 间会议室`,
  }
}

// ---------- 例子 ----------

const MERGE: IV[] = [[2, 3], [5, 6], [1, 8], [9, 10], [10, 12]]
const SCHED: IV[] = [[1, 4], [2, 3], [3, 6], [5, 7], [6, 9], [8, 10], [0, 11]]
const SCHED_LEN: IV[] = [[1, 5], [4, 6], [5, 9]]
const CLIPS: IV[] = [[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]]
const MEET: IV[] = [[1, 5], [2, 5], [3, 6], [5, 8], [7, 9]]

const CASES: Record<string, () => Run> = {
  'merge-start': () => merge(MERGE, 'start'),
  'merge-end': () => merge(MERGE, 'end'),
  'sched-end': () => schedule(SCHED, 'end'),
  'sched-start': () => schedule(SCHED, 'start'),
  'sched-len': () => schedule(SCHED_LEN, 'len'),
  'sched-start-min': () => scheduleStartMin(SCHED),
  'cover-start': () => cover(CLIPS, 10),
  'cover-end': () => coverByEnd(CLIPS, 10),
  sweep: () => sweep(MEET),
}

// ---------- 渲染 ----------

const props = defineProps<{ cases: string }>()
const runs = computed(() => props.cases.split(',').map((c) => c.trim()).filter((c) => CASES[c]).map((c) => CASES[c]()))
const ti = ref(0)
const si = ref(0)
const run = computed(() => runs.value[ti.value])
const step = computed(() => run.value.steps[si.value])
const last = computed(() => si.value === run.value.steps.length - 1)

const W = 640, PL = 18, PR = 120, TOP = 30, RH = 24, BH = 12
const lo = computed(() => Math.min(...run.value.rows.map((v) => v[0]), run.value.T !== undefined ? 0 : Infinity))
const hi = computed(() => Math.max(...run.value.rows.map((v) => v[1]), run.value.T ?? -Infinity))
const x = (t: number) => PL + ((t - lo.value) / (hi.value - lo.value)) * (W - PL - PR)
const rowY = (i: number) => TOP + i * RH
const rowsEnd = computed(() => TOP + run.value.rows.length * RH)
const extraH = computed(() => (run.value.bandLabel ? RH + 4 : run.value.maxY ? 70 : 0))
const axisY = computed(() => rowsEnd.value + extraH.value)
const H = computed(() => axisY.value + 22)
const ticks = computed(() => {
  const span = hi.value - lo.value, gap = span > 20 ? 5 : 1
  const out: number[] = []
  for (let t = Math.ceil(lo.value / gap) * gap; t <= hi.value; t += gap) out.push(t)
  return out
})
const bandY = computed(() => rowsEnd.value + 6)
const curveTop = computed(() => rowsEnd.value + 10)
const curveH = 52
const cy = (n: number) => curveTop.value + curveH - (n / (run.value.maxY || 1)) * curveH
const curvePath = computed(() => {
  const pts = step.value.curve
  if (!pts || pts.length < 2) return ''
  return pts.map(([t, n], k) => `${k ? 'L' : 'M'}${x(t)},${cy(n)}`).join(' ')
})

let timer: ReturnType<typeof setInterval> | undefined
const playing = ref(false)
function stop() { if (timer) clearInterval(timer); timer = undefined; playing.value = false }
function go(n: number) { si.value = Math.max(0, Math.min(run.value.steps.length - 1, n)) }
function play() {
  if (playing.value) return stop()
  if (last.value) si.value = 0
  playing.value = true
  timer = setInterval(() => { if (last.value) stop(); else si.value++ }, 1100)
}
function pick(k: number) { stop(); ti.value = k; si.value = 0 }
onUnmounted(stop)
</script>

<template>
  <figure v-if="run" class="iv">
    <div v-if="runs.length > 1" class="iv-tabs">
      <button v-for="(r, k) in runs" :key="k" :class="{ on: k === ti }" @click="pick(k)">{{ r.tab }}</button>
    </div>
    <div class="iv-head">
      <code class="iv-sort" :class="run.ok ? 'ok' : 'bad'">{{ run.sort }}</code>
      <span class="iv-in">输入 {{ run.input.map(fmt).join(' ') }}<template v-if="run.T !== undefined">，T = {{ run.T }}</template></span>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="iv-svg" role="img" :aria-label="step.msg">
      <g v-for="t in ticks" :key="'t' + t">
        <line :x1="x(t)" :x2="x(t)" :y1="TOP - 8" :y2="axisY" class="iv-grid" />
        <text :x="x(t)" :y="axisY + 15" class="iv-tick">{{ t }}</text>
      </g>
      <line v-if="run.T !== undefined" :x1="x(run.T)" :x2="x(run.T)" :y1="TOP - 8" :y2="axisY" class="iv-goal" />

      <g v-for="(v, i) in run.rows" :key="i">
        <text v-if="step.i === i" :x="x(v[0]) - 5" :y="rowY(i) + BH - 1" class="iv-now">▶</text>
        <rect :x="x(v[0])" :y="rowY(i)" :width="Math.max(x(v[1]) - x(v[0]), 2)" :height="BH" rx="3"
              class="iv-bar" :class="step.st[i]" />
        <text :x="x(v[1]) + 6" :y="rowY(i) + BH - 2" class="iv-lab" :class="step.st[i]">{{ fmt(v) }}<tspan v-if="run.key" class="iv-key"> {{ run.key[0] }} {{ run.key[1](v) }}</tspan></text>
      </g>

      <g v-if="run.bandLabel">
        <rect v-for="(b, k) in step.band ?? []" :key="'b' + k" :x="x(b[0])" :y="bandY" :width="Math.max(x(b[1]) - x(b[0]), 2)"
              :height="BH + 2" rx="3" class="iv-band" />
        <text :x="x(Math.max(lo, ...(step.band ?? []).map((b) => b[1]))) + 6" :y="bandY + BH" class="iv-band-lab">{{ run.bandLabel }}</text>
      </g>

      <g v-if="run.maxY">
        <line :x1="x(lo)" :x2="x(hi)" :y1="cy(0)" :y2="cy(0)" class="iv-grid" />
        <line :x1="x(lo)" :x2="x(hi)" :y1="cy(run.maxY)" :y2="cy(run.maxY)" class="iv-grid dash" />
        <text :x="x(hi) + 6" :y="cy(run.maxY) + 4" class="iv-band-lab">最多 {{ run.maxY }}</text>
        <text :x="x(hi) + 6" :y="cy(0) + 4" class="iv-band-lab">同时进行数</text>
        <path :d="curvePath" class="iv-curve" />
      </g>

      <g v-if="step.mark" class="iv-mark">
        <line :x1="x(step.mark.t)" :x2="x(step.mark.t)" :y1="TOP - 10" :y2="axisY" />
        <text :x="x(step.mark.t)" :y="TOP - 14">{{ step.mark.label }}</text>
      </g>
    </svg>

    <div class="iv-legend">
      <span v-for="[s, label] in run.legend" :key="s"><i class="iv-sw" :class="s" />{{ label }}</span>
    </div>
    <div class="iv-msg">{{ step.msg }}</div>
    <div class="iv-ctl">
      <button @click="stop(); go(0)" title="回到开头">⏮</button>
      <button @click="stop(); go(si - 1)" :disabled="si === 0">◀</button>
      <button class="play" @click="play">{{ playing ? '暂停' : '播放' }}</button>
      <button @click="stop(); go(si + 1)" :disabled="last">▶</button>
      <button @click="stop(); go(run.steps.length - 1)" title="跳到结果">⏭</button>
      <span class="iv-count">{{ si }} / {{ run.steps.length - 1 }}</span>
      <span v-if="last" class="iv-verdict" :class="run.ok ? 'ok' : 'bad'">{{ run.ok ? '✓' : '✗' }} {{ run.verdict }}</span>
    </div>
  </figure>
</template>

<style scoped>
.iv {
  margin: 20px 0; padding: 12px 14px 10px; border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.iv-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.iv-tabs button, .iv-ctl button {
  font-size: 13px; padding: 3px 10px; border-radius: 6px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer;
}
.iv-tabs button.on { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.iv-ctl button:disabled { opacity: .4; cursor: default; }
.iv-ctl button.play { min-width: 52px; }
.iv-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px; font-size: 13px; color: var(--vp-c-text-2); }
.iv-sort.ok { color: var(--vp-c-green-1); }
.iv-sort.bad { color: var(--vp-c-red-1); }
.iv-svg { display: block; width: 100%; height: auto; margin: 6px 0 2px; overflow: visible; }

.iv-grid { stroke: var(--vp-c-divider); stroke-width: 1; }
.iv-grid.dash { stroke-dasharray: 3 3; }
.iv-goal { stroke: var(--vp-c-text-3); stroke-width: 1.5; stroke-dasharray: 5 3; }
.iv-tick { font-size: 10px; fill: var(--vp-c-text-3); text-anchor: middle; }
.iv-now { font-size: 10px; fill: var(--vp-c-brand-1); text-anchor: end; }

.iv-bar { fill: var(--vp-c-default-soft); stroke: var(--vp-c-text-3); stroke-width: 1; transition: fill .2s, stroke .2s; }
.iv-bar.kept { fill: var(--vp-c-green-soft); stroke: var(--vp-c-green-1); stroke-width: 1.5; }
.iv-bar.merged { fill: var(--vp-c-indigo-soft); stroke: var(--vp-c-indigo-1); stroke-width: 1.5; }
.iv-bar.cand { fill: var(--vp-c-yellow-soft); stroke: var(--vp-c-yellow-1); stroke-width: 1.5; }
.iv-bar.drop { fill: var(--vp-c-red-soft); stroke: var(--vp-c-red-1); stroke-dasharray: 3 2; opacity: .7; }
.iv-bar.done { fill: transparent; stroke: var(--vp-c-text-3); stroke-dasharray: 2 2; opacity: .6; }

.iv-lab { font-size: 11px; fill: var(--vp-c-text-1); font-family: var(--vp-font-family-mono); }
.iv-lab.drop, .iv-lab.done { fill: var(--vp-c-text-3); text-decoration: line-through; }
.iv-key { fill: var(--vp-c-text-3); font-size: 10px; }

.iv-band { fill: var(--vp-c-brand-soft); stroke: var(--vp-c-brand-1); stroke-width: 1.5; }
.iv-band-lab { font-size: 11px; fill: var(--vp-c-text-2); }
.iv-curve { fill: none; stroke: var(--vp-c-brand-1); stroke-width: 2; }

.iv-mark line { stroke: var(--vp-c-brand-1); stroke-width: 1.5; stroke-dasharray: 4 3; }
.iv-mark text { font-size: 11px; fill: var(--vp-c-brand-1); text-anchor: middle; font-family: var(--vp-font-family-mono); }

.iv-legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: var(--vp-c-text-2); }
.iv-legend span { display: inline-flex; align-items: center; gap: 5px; }
.iv-sw { display: inline-block; width: 18px; height: 9px; border-radius: 2px; border: 1px solid var(--vp-c-text-3); }
.iv-sw.kept { background: var(--vp-c-green-soft); border-color: var(--vp-c-green-1); }
.iv-sw.merged { background: var(--vp-c-indigo-soft); border-color: var(--vp-c-indigo-1); }
.iv-sw.cand { background: var(--vp-c-yellow-soft); border-color: var(--vp-c-yellow-1); }
.iv-sw.drop { background: var(--vp-c-red-soft); border-color: var(--vp-c-red-1); border-style: dashed; }
.iv-sw.done { border-style: dashed; }

.iv-msg {
  margin: 8px 0; padding: 8px 10px; min-height: 3.4em; border-radius: 6px; font-size: 14px; line-height: 1.5;
  background: var(--vp-c-bg); border-left: 3px solid var(--vp-c-brand-1);
}
.iv-ctl { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.iv-count { font-size: 12px; color: var(--vp-c-text-3); margin-left: 4px; font-variant-numeric: tabular-nums; }
.iv-verdict { font-size: 13px; font-weight: 600; margin-left: 6px; }
.iv-verdict.ok { color: var(--vp-c-green-1); }
.iv-verdict.bad { color: var(--vp-c-red-1); }
</style>
