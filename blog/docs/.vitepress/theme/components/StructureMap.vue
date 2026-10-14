<script setup lang="ts">
import { withBase } from 'vitepress'

// 概念数据结构的「推导图」：从内存布局出发，每多维护一种信息就长出一种结构。
// 框里上面一行是概念名（点进 /structures/），下面一行是 Python 里落地用的东西（L1 那层）。
interface Node {
  x: number; y: number; w: number; h: number
  name: string; link: string; py: string; pyLink: string
}
const nodes: Node[] = [
  { x: 20, y: 170, w: 190, h: 70, name: '栈 / 队列', link: '/structures/stack-queue', py: 'list · deque', pyLink: '/python/deque' },
  { x: 285, y: 40, w: 190, h: 70, name: '哈希表', link: '/structures/hash-table', py: 'dict · set', pyLink: '/python/dict-set' },
  { x: 550, y: 40, w: 190, h: 70, name: '堆', link: '/structures/heap', py: 'heapq', pyLink: '/python/heapq' },
  { x: 550, y: 200, w: 190, h: 70, name: '有序集合', link: '/structures/ordered-set', py: 'SortedList · bisect', pyLink: '/python/bisect-sorted' },
]
</script>

<template>
  <figure class="sm">
    <svg viewBox="0 0 760 400" role="img" aria-label="数据结构推导图">
      <defs>
        <marker id="sm-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" class="sm-arrhead" />
        </marker>
      </defs>

      <!-- 边：内存布局 → 栈/队列、哈希表；哈希表 → 堆 → 有序集合 -->
      <path d="M380,318 V285 H115 V244" class="sm-edge" marker-end="url(#sm-arr)" />
      <text x="200" y="277" class="sm-elabel">+ 插入时间</text>
      <path d="M380,285 V114" class="sm-edge" marker-end="url(#sm-arr)" />
      <text x="390" y="205" class="sm-elabel">+ 唯一性（只问相等）</text>
      <path d="M475,75 H546" class="sm-edge" marker-end="url(#sm-arr)" />
      <text x="482" y="64" class="sm-elabel">+ 值</text>
      <text x="482" y="98" class="sm-elabel sm-sub">偏序</text>
      <path d="M645,110 V196" class="sm-edge" marker-end="url(#sm-arr)" />
      <text x="655" y="158" class="sm-elabel">+ 全序</text>

      <g v-for="n in nodes" :key="n.name">
        <rect :x="n.x" :y="n.y" :width="n.w" :height="n.h" rx="8" class="sm-box" />
        <a :href="withBase(n.link)">
          <text :x="n.x + n.w / 2" :y="n.y + 30" class="sm-name">{{ n.name }}</text>
        </a>
        <a :href="withBase(n.pyLink)">
          <text :x="n.x + n.w / 2" :y="n.y + 54" class="sm-py">{{ n.py }}</text>
        </a>
      </g>

      <!-- 底座：内存布局 -->
      <rect x="230" y="320" width="300" height="66" rx="8" class="sm-box sm-base" />
      <text x="248" y="358" class="sm-baselabel">内存布局</text>
      <a :href="withBase('/structures/array')"><text x="370" y="350" class="sm-name">数组</text></a>
      <a :href="withBase('/python/list')"><text x="370" y="374" class="sm-py">list</text></a>
      <a :href="withBase('/structures/linked-list')"><text x="465" y="350" class="sm-name">链表</text></a>
      <text x="465" y="374" class="sm-py sm-dim">ListNode 手写</text>
    </svg>
    <figcaption>
      往上每走一步就多维护一种信息：插入时间 → 栈 / 队列，唯一性 → 哈希，值的偏序 → 堆，全序 → 有序集合。
      理论上都能拿链表搭，实际上考虑内存开销和 cache 命中率，数组几乎总是更好。
    </figcaption>
  </figure>
</template>

<style scoped>
.sm { margin: 24px 0; }
.sm svg { width: 100%; height: auto; max-width: 760px; display: block; }
.sm-box { fill: var(--vp-c-bg-soft); stroke: var(--vp-c-text-3); stroke-width: 1.2; }
.sm-base { fill: var(--vp-c-default-soft); }
.sm-edge { fill: none; stroke: var(--vp-c-text-2); stroke-width: 1.4; }
.sm-arrhead { fill: var(--vp-c-text-2); }
.sm-elabel { font-size: 14px; fill: var(--vp-c-text-1); }
.sm-sub { font-size: 12px; fill: var(--vp-c-text-2); }
.sm-name { font-size: 17px; font-weight: 600; text-anchor: middle; fill: var(--vp-c-brand-1); }
.sm-py { font-size: 12.5px; text-anchor: middle; fill: var(--vp-c-text-2); font-family: var(--vp-font-family-mono); }
.sm-dim { fill: var(--vp-c-text-3); }
.sm-baselabel { font-size: 13px; fill: var(--vp-c-text-2); writing-mode: horizontal-tb; }
.sm a:hover text { text-decoration: underline; }
figcaption { font-size: 13px; color: var(--vp-c-text-2); margin-top: 8px; }
</style>
