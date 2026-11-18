<script setup lang="ts">
import { computed, ref } from 'vue'

// combinatorics.md 第 7 节：<StickViz :n="4" :k="2" />。
// 列出 n 根里看得见 k 根的全部排法，每种切成 k 组（看得见的那根 + 它后面被挡住的），
// 再按「组的大小怎么分」归类：每类的个数不一样，所以 c(n, k) 只能分情况加，收不成一个公式。
const props = withDefaults(defineProps<{ n?: number; k?: number }>(), { n: 4, k: 2 })
const NS = [3, 4, 5]
const n = ref(NS.includes(props.n) ? props.n : 4)
const k = ref(Math.min(props.k, n.value))

function perms(m: number): number[][] {
  if (m === 0) return [[]]
  const out: number[][] = []
  for (const p of perms(m - 1)) for (let i = 0; i <= p.length; i++) out.push([...p.slice(0, i), m, ...p.slice(i)])
  return out
}
// 从左往右，比前面都高的那根开一个新组
function blocks(p: number[]): number[][] {
  const out: number[][] = []
  let top = 0
  for (const v of p) {
    if (v > top) { out.push([v]); top = v } else out[out.length - 1].push(v)
  }
  return out
}
const fact = (m: number): number => (m <= 1 ? 1 : m * fact(m - 1))
const comb = (a: number, b: number) => (b < 0 || b > a ? 0 : fact(a) / (fact(b) * fact(a - b)))

interface Group { key: string; sizes: number[]; items: number[][][]; split: number; inside: number }
const groups = computed<Group[]>(() => {
  const byKey = new Map<string, Group>()
  for (const p of perms(n.value)) {
    const bs = blocks(p)
    if (bs.length !== k.value) continue
    const sizes = bs.map((b) => b.length).sort((a, b) => b - a)
    const key = sizes.join(' + ')
    if (!byKey.has(key)) {
      // 把 n 根分成这些大小的组有几种：n! / (∏ s! · ∏ 同样大小的组数!)；组内：每组 (s-1)!
      const mult = new Map<number, number>()
      sizes.forEach((s) => mult.set(s, (mult.get(s) ?? 0) + 1))
      const split = fact(n.value) / (sizes.reduce((x, s) => x * fact(s), 1) * [...mult.values()].reduce((x, c) => x * fact(c), 1))
      const inside = sizes.reduce((x, s) => x * fact(s - 1), 1)
      byKey.set(key, { key, sizes, items: [], split, inside })
    }
    byKey.get(key)!.items.push(bs)
  }
  return [...byKey.values()].sort((a, b) => (a.key < b.key ? 1 : -1))
})
const total = computed(() => groups.value.reduce((s, g) => s + g.items.length, 0))

function pickN(m: number) { n.value = m; if (k.value > m) k.value = m }

// 小图：一根木棍一个竖条，高度 = 长度；每组外面画一个框
const BW = 14, GAP = 3, BG = 10, HH = 56, PAD = 4
const width = (bs: number[][]) => PAD * 2 + bs.reduce((s, b) => s + b.length * (BW + GAP) - GAP, 0) + (bs.length - 1) * BG
function layout(bs: number[][]) {
  const out: { x: number; v: number; head: boolean }[] = []
  const boxes: { x: number; w: number }[] = []
  let x = PAD
  for (const b of bs) {
    const x0 = x
    b.forEach((v, i) => { out.push({ x, v, head: i === 0 }); x += BW + GAP })
    boxes.push({ x: x0 - 2, w: x - GAP - x0 + 4 })
    x += BG - GAP
  }
  return { bars: out, boxes }
}
const barH = (v: number) => (v / n.value) * (HH - 8)
</script>

<template>
  <figure class="sv">
    <div class="sv-pick">
      <span>n =</span>
      <button v-for="m in NS" :key="m" :class="{ on: m === n }" @click="pickN(m)">{{ m }}</button>
      <span class="sv-sep">k =</span>
      <button v-for="m in n" :key="m" :class="{ on: m === k }" @click="k = m">{{ m }}</button>
    </div>

    <div class="sv-sum">
      c({{ n }}, {{ k }}) =
      <template v-for="(g, i) in groups" :key="g.key">{{ i ? ' + ' : '' }}<b>{{ g.items.length }}</b></template>
      <template v-if="groups.length > 1"> = <b>{{ total }}</b></template>
      <span class="sv-vs">　对比组合数 C({{ n }}, {{ k }}) = {{ comb(n, k) }}</span>
    </div>

    <section v-for="g in groups" :key="g.key" class="sv-group">
      <div class="sv-gh">
        <span class="sv-key">每组大小 {{ g.key }}</span>
        <span>{{ g.items.length }} 种 = 分组方式 {{ g.split }} 种 × 组内排法 {{ g.inside }} 种</span>
      </div>
      <div class="sv-items">
        <div v-for="(bs, i) in g.items" :key="i" class="sv-item">
          <svg :viewBox="`0 0 ${width(bs)} ${HH + 17}`" :width="width(bs)" :height="HH + 17" role="img"
               :aria-label="bs.map((b) => '[' + b.join(' ') + ']').join(' ')">
            <rect v-for="(bx, j) in layout(bs).boxes" :key="'b' + j" :x="bx.x" y="1" :width="bx.w" :height="HH - 1" rx="3" class="sv-box" />
            <g v-for="(bar, j) in layout(bs).bars" :key="j">
              <rect :x="bar.x" :y="HH - barH(bar.v)" :width="BW" :height="barH(bar.v)" rx="1.5" class="sv-bar" :class="{ head: bar.head }" />
              <text :x="bar.x + BW / 2" :y="HH + 13" class="sv-num" :class="{ head: bar.head }">{{ bar.v }}</text>
            </g>
          </svg>
        </div>
      </div>
    </section>

    <div class="sv-legend">
      <span><i class="sv-sw head" />看得见（组头，这组里最高）</span>
      <span><i class="sv-sw" />被组头挡住</span>
      <span><i class="sv-sw box" />一组</span>
    </div>
  </figure>
</template>

<style scoped>
.sv {
  margin: 20px 0; padding: 12px 14px 10px; border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft);
}
.sv-pick { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 13px; color: var(--vp-c-text-2); }
.sv-pick button {
  font-size: 13px; min-width: 30px; padding: 2px 8px; border-radius: 6px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer; font-family: var(--vp-font-family-mono);
}
.sv-pick button.on { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.sv-sep { margin-left: 10px; }
.sv-sum { margin: 10px 0 4px; font-size: 15px; font-family: var(--vp-font-family-mono); }
.sv-sum b { color: var(--vp-c-brand-1); }
.sv-vs { font-size: 13px; color: var(--vp-c-text-3); font-family: var(--vp-font-family-base); }

.sv-group { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--vp-c-divider); }
.sv-gh { display: flex; flex-wrap: wrap; gap: 4px 12px; font-size: 13px; color: var(--vp-c-text-2); margin-bottom: 6px; }
.sv-key { font-weight: 600; color: var(--vp-c-text-1); }
.sv-items { display: flex; flex-wrap: wrap; gap: 6px; }
.sv-item { padding: 3px 4px 1px; border-radius: 6px; background: var(--vp-c-bg); border: 1px solid var(--vp-c-divider); }
.sv-item svg { display: block; }

.sv-box { fill: none; stroke: var(--vp-c-text-3); stroke-width: 1; stroke-dasharray: 3 2; }
.sv-bar { fill: var(--vp-c-default-3); }
.sv-bar.head { fill: var(--vp-c-brand-1); }
.sv-num { font-size: 11px; text-anchor: middle; fill: var(--vp-c-text-3); font-family: var(--vp-font-family-mono); }
.sv-num.head { fill: var(--vp-c-brand-1); font-weight: 600; }

.sv-legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; font-size: 12px; color: var(--vp-c-text-2); }
.sv-legend span { display: inline-flex; align-items: center; gap: 5px; }
.sv-sw { display: inline-block; width: 10px; height: 14px; border-radius: 2px; background: var(--vp-c-default-3); }
.sv-sw.head { background: var(--vp-c-brand-1); }
.sv-sw.box { width: 18px; background: transparent; border: 1px dashed var(--vp-c-text-3); }
</style>
