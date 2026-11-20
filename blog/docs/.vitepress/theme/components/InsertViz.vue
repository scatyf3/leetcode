<script setup lang="ts">
import { computed, ref } from 'vue'

// combinatorics.md 第 7 节：<InsertViz :n="3" :k="2" />。
// 插入递推 dp[n][k] = dp[n-1][k-1] + (n-1)·dp[n-1][k] 的完整展开：
// 先把其余 n-1 根（高度 2..n）排好，再把最矮的 1 插进去。
// ① 插最左：1 看得见，其余要看见 k-1 根；② 插其余 n-1 个空位：1 被挡住，其余要看见 k 根。
// 1 最矮、挡不住任何人，所以其余木棍看不看得见在插入前后不变。点 dp 表的格子换 (n, k)。
const props = withDefaults(defineProps<{ n?: number; k?: number }>(), { n: 3, k: 2 })
const MAX = 5
const clamp = (x: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, x))
const n = ref(clamp(props.n, 1, MAX))
const k = ref(clamp(props.k, 1, n.value))

function perms(m: number): number[][] {
  if (m === 0) return [[]]
  const out: number[][] = []
  for (const p of perms(m - 1)) for (let i = 0; i <= p.length; i++) out.push([...p.slice(0, i), m, ...p.slice(i)])
  return out
}
const seenCount = (p: number[]) => { let top = 0, c = 0; for (const v of p) if (v > top) { c++; top = v } return c }

// dp 表 0..MAX，和题解同一个递推
const DP: number[][] = Array.from({ length: MAX + 1 }, () => Array(MAX + 1).fill(0))
DP[0][0] = 1
for (let i = 1; i <= MAX; i++) for (let j = 1; j <= i; j++) DP[i][j] = DP[i - 1][j - 1] + (i - 1) * DP[i - 1][j]

// 其余 m 根看见 j 根的全部排法，高度整体 +1（变成 2..m+1），给 1 腾位置
const sources = (m: number, j: number) => perms(m).filter((p) => seenCount(p) === j).map((p) => p.map((v) => v + 1))

interface Pic { p: number[]; slots: number[] }
interface Row { src: Pic; outs: Pic[] }
const leftRows = computed<Row[]>(() =>
  sources(n.value - 1, k.value - 1).map((src) => ({ src: { p: src, slots: [0] }, outs: [{ p: [1, ...src], slots: [] }] })))
const restRows = computed<Row[]>(() =>
  sources(n.value - 1, k.value).map((src) => {
    const idx = src.map((_, i) => i + 1)
    return { src: { p: src, slots: idx }, outs: idx.map((i) => ({ p: [...src.slice(0, i), 1, ...src.slice(i)], slots: [] })) }
  }))

const a = computed(() => DP[n.value - 1][k.value - 1])
const b = computed(() => DP[n.value - 1][k.value])
const leftEmpty = computed(() => (n.value - 1 === 0 ? '' : `其余 ${n.value - 1} 根至少看得见最左那根，不可能看见 0 根`))
const restEmpty = computed(() => `其余只有 ${n.value - 1} 根，凑不出 ${k.value} 根看得见`)

function pick(i: number, j: number) { if (j >= 1 && j <= i) { n.value = i; k.value = j } }
function cellClass(i: number, j: number) {
  return {
    cur: i === n.value && j === k.value,
    fromL: i === n.value - 1 && j === k.value - 1,
    fromU: i === n.value - 1 && j === k.value,
    pickable: j >= 1 && j <= i,
    blank: j > i,
  }
}

// 小图：一根木棍一个竖条，高度 = 长度；虚线 = 1 可以插的空位
const BW = 16, GAP = 8, PAD = 9, HH = 58
const width = (p: number[]) => Math.max(26, PAD * 2 + p.length * (BW + GAP) - GAP)
function bars(p: number[]) {
  let top = 0
  return p.map((v, i) => {
    const vis = v > top
    if (vis) top = v
    return { x: PAD + i * (BW + GAP), v, vis, ins: v === 1 }
  })
}
const slotX = (s: number) => PAD + s * (BW + GAP) - GAP / 2
const barH = (v: number) => (v / n.value) * (HH - 6)
</script>

<template>
  <figure class="iv">
    <div class="iv-top">
      <table class="iv-dp">
        <thead>
          <tr><th>i \ j</th><th v-for="j in MAX + 1" :key="j">{{ j - 1 }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="i in MAX + 1" :key="i">
            <th>{{ i - 1 }}</th>
            <td v-for="j in MAX + 1" :key="j" :class="cellClass(i - 1, j - 1)" @click="pick(i - 1, j - 1)">
              {{ j - 1 > i - 1 ? '' : DP[i - 1][j - 1] }}
            </td>
          </tr>
        </tbody>
      </table>
      <div class="iv-formula">
        <div>dp[{{ n }}][{{ k }}] = <span class="cL">dp[{{ n - 1 }}][{{ k - 1 }}]</span> + {{ n - 1 }} × <span class="cU">dp[{{ n - 1 }}][{{ k }}]</span></div>
        <div>= <span class="cL">{{ a }}</span> + {{ n - 1 }} × <span class="cU">{{ b }}</span> = <b>{{ DP[n][k] }}</b></div>
        <div class="iv-hint">点表格里的格子换 (n, k)。<span class="cL">左上</span>：1 插最左；<span class="cU">正上</span>：1 插其他空位</div>
      </div>
    </div>

    <section class="iv-case">
      <div class="iv-ch">
        <span class="iv-tag cLbg">①</span>
        1 插<b>最左</b> → 看得见。其余 {{ n - 1 }} 根要看见 {{ k - 1 }} 根：<span class="cL">{{ a }}</span> 种 × 1 个空位 = <b>{{ a }}</b>
      </div>
      <div v-if="!leftRows.length" class="iv-empty">没有：{{ leftEmpty }}</div>
      <div v-for="(row, r) in leftRows" :key="r" class="iv-row">
        <template v-for="(pic, c) in [row.src, ...row.outs]" :key="c">
          <span v-if="c === 1" class="iv-arrow">→</span>
          <svg :viewBox="`0 0 ${width(pic.p)} ${HH + 16}`" :width="width(pic.p)" :height="HH + 16" class="iv-pic" :class="{ src: c === 0 }"
               role="img" :aria-label="pic.p.join(' ') || '空'">
            <text v-if="!pic.p.length" :x="width(pic.p) / 2" :y="HH - 10" class="iv-num">∅</text>
            <line v-for="s in pic.slots" :key="'s' + s" :x1="slotX(s)" :x2="slotX(s)" y1="3" :y2="HH" class="iv-slot" />
            <g v-for="(bar, j) in bars(pic.p)" :key="j">
              <rect :x="bar.x" :y="HH - barH(bar.v)" :width="BW" :height="barH(bar.v)" rx="1.5" class="iv-bar" :class="{ vis: bar.vis, ins: bar.ins }" />
              <text :x="bar.x + BW / 2" :y="HH + 12" class="iv-num" :class="{ vis: bar.vis, ins: bar.ins }">{{ bar.v }}</text>
            </g>
          </svg>
        </template>
      </div>
    </section>

    <section class="iv-case">
      <div class="iv-ch">
        <span class="iv-tag cUbg">②</span>
        1 插<b>其他 {{ n - 1 }} 个空位</b> → 被挡住。其余 {{ n - 1 }} 根要看见 {{ k }} 根：<span class="cU">{{ b }}</span> 种 × {{ n - 1 }} 个空位 = <b>{{ (n - 1) * b }}</b>
      </div>
      <div v-if="!restRows.length" class="iv-empty">没有：{{ restEmpty }}</div>
      <div v-for="(row, r) in restRows" :key="r" class="iv-row">
        <template v-for="(pic, c) in [row.src, ...row.outs]" :key="c">
          <span v-if="c === 1" class="iv-arrow">→</span>
          <svg :viewBox="`0 0 ${width(pic.p)} ${HH + 16}`" :width="width(pic.p)" :height="HH + 16" class="iv-pic" :class="{ src: c === 0 }"
               role="img" :aria-label="pic.p.join(' ') || '空'">
            <line v-for="s in pic.slots" :key="'s' + s" :x1="slotX(s)" :x2="slotX(s)" y1="3" :y2="HH" class="iv-slot" />
            <g v-for="(bar, j) in bars(pic.p)" :key="j">
              <rect :x="bar.x" :y="HH - barH(bar.v)" :width="BW" :height="barH(bar.v)" rx="1.5" class="iv-bar" :class="{ vis: bar.vis, ins: bar.ins }" />
              <text :x="bar.x + BW / 2" :y="HH + 12" class="iv-num" :class="{ vis: bar.vis, ins: bar.ins }">{{ bar.v }}</text>
            </g>
          </svg>
        </template>
      </div>
    </section>

    <div class="iv-legend">
      <span><i class="iv-sw vis" />看得见</span>
      <span><i class="iv-sw" />被挡住</span>
      <span><i class="iv-sw ins" />插进来的最矮的 1</span>
      <span><i class="iv-sw slot" />1 可以插的空位</span>
      <span>每行：其余 {{ n - 1 }} 根的一种排法 → 插完的结果</span>
    </div>
  </figure>
</template>

<style scoped>
.iv {
  margin: 20px 0; padding: 12px 14px 10px; border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft);
  --iv-l: var(--vp-c-brand-1);
  --iv-u: var(--vp-c-warning-1);
  --iv-ins: var(--vp-c-danger-1);
}
.iv-top { display: flex; flex-wrap: wrap; gap: 12px 20px; align-items: center; }

.iv-dp { border-collapse: collapse; margin: 0; font-family: var(--vp-font-family-mono); font-size: 12px; display: table; }
.iv-dp th, .iv-dp td { border: 1px solid var(--vp-c-divider); padding: 2px 7px; text-align: center; min-width: 28px; }
.iv-dp th { color: var(--vp-c-text-3); background: transparent; font-weight: 500; }
.iv-dp tr { background: transparent !important; }
.iv-dp td { background: var(--vp-c-bg); color: var(--vp-c-text-2); }
.iv-dp td.blank { background: transparent; }
.iv-dp td.pickable { cursor: pointer; }
.iv-dp td.pickable:hover { color: var(--vp-c-text-1); background: var(--vp-c-default-soft); }
.iv-dp td.cur { outline: 2px solid var(--vp-c-text-1); outline-offset: -2px; color: var(--vp-c-text-1); font-weight: 700; }
.iv-dp td.fromL { background: var(--vp-c-brand-soft); color: var(--iv-l); font-weight: 600; }
.iv-dp td.fromU { background: var(--vp-c-warning-soft); color: var(--iv-u); font-weight: 600; }

.iv-formula { font-family: var(--vp-font-family-mono); font-size: 14px; line-height: 1.8; min-width: 0; }
.iv-formula b { font-size: 15px; }
.iv-hint { font-family: var(--vp-font-family-base); font-size: 12px; color: var(--vp-c-text-3); }
.cL { color: var(--iv-l); font-weight: 600; }
.cU { color: var(--iv-u); font-weight: 600; }

.iv-case { margin-top: 12px; padding-top: 8px; border-top: 1px dashed var(--vp-c-divider); }
.iv-ch { font-size: 13px; color: var(--vp-c-text-2); margin-bottom: 6px; }
.iv-tag { display: inline-block; width: 18px; height: 18px; line-height: 18px; text-align: center; border-radius: 50%; color: var(--vp-c-white); font-size: 11px; margin-right: 4px; }
.cLbg { background: var(--iv-l); }
.cUbg { background: var(--iv-u); }
.iv-empty { font-size: 13px; color: var(--vp-c-text-3); font-style: italic; }

.iv-row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 6px; }
.iv-arrow { color: var(--vp-c-text-3); font-size: 16px; padding: 0 2px; }
.iv-pic { display: block; padding: 2px; border-radius: 6px; background: var(--vp-c-bg); border: 1px solid var(--vp-c-divider); }
.iv-pic.src { border-style: dashed; background: transparent; }

.iv-slot { stroke: var(--iv-ins); stroke-width: 1.5; stroke-dasharray: 3 2; opacity: 0.8; }
.iv-bar { fill: var(--vp-c-text-3); opacity: 0.45; }
.iv-bar.vis, .iv-bar.ins { opacity: 1; }
.iv-bar.vis { fill: var(--vp-c-brand-2); }
.iv-bar.ins { fill: var(--iv-ins); }
.iv-num { font-size: 11px; text-anchor: middle; fill: var(--vp-c-text-3); font-family: var(--vp-font-family-mono); }
.iv-num.vis { fill: var(--vp-c-brand-1); font-weight: 600; }
.iv-num.ins { fill: var(--iv-ins); font-weight: 700; }

.iv-legend { display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 10px; font-size: 12px; color: var(--vp-c-text-2); }
.iv-legend span { display: inline-flex; align-items: center; gap: 5px; }
.iv-sw { display: inline-block; width: 10px; height: 14px; border-radius: 2px; background: var(--vp-c-text-3); opacity: 0.45; }
.iv-sw.vis, .iv-sw.ins, .iv-sw.slot { opacity: 1; }
.iv-sw.vis { background: var(--vp-c-brand-2); }
.iv-sw.ins { background: var(--iv-ins); }
.iv-sw.slot { width: 0; border-left: 2px dashed var(--iv-ins); border-radius: 0; background: transparent; }
</style>
