<script setup lang="ts">
import { withBase } from 'vitepress'
import { data as topics } from '../../data/topics.data'
import { data as problems } from '../../data/problems.data'
import { layers } from '../../layers'
import { problemsOf } from '../problems'

// 首页分层图：L3 套路在最上，L1 Python 内置在最下 —— 读法是「套路靠结构撑着，结构靠 Python 容器落地」。
// 格子 = 一篇文章；虚线格 = status: todo 的占位；右上角数字 = tracker 里打了这个标签的题数。
const rows = [...layers].reverse().map((l) => ({
  ...l,
  items: topics
    .filter((t) => t.dir === l.dir)
    .map((t) => ({ ...t, n: problemsOf(problems, l, t).length })),
}))
</script>

<template>
  <figure class="lf">
    <div v-for="l in rows" :key="l.id" class="lf-row" :style="{ '--lc': l.color }">
      <a class="lf-label" :href="withBase(`/${l.dir}/`)">
        <span class="lf-id">L{{ l.id }}</span>
        <span class="lf-text">
          <span class="lf-en">{{ l.en }}</span>
          <span class="lf-zh">{{ l.name }}</span>
        </span>
      </a>
      <div class="lf-boxes">
        <a
          v-for="t in l.items"
          :key="t.url"
          class="lf-box"
          :class="{ ph: t.status === 'todo' }"
          :href="withBase(t.url)"
          :title="t.status === 'todo' ? '还没写，只有题目列表' : t.title"
        >{{ t.title }}<sup v-if="t.n">{{ t.n }}</sup></a>
      </div>
      <div class="lf-scope">{{ l.scope }}</div>
    </div>
  </figure>
</template>

<style scoped>
.lf { margin: 24px 0; display: flex; flex-direction: column; gap: 10px; }
.lf-row {
  display: grid; grid-template-columns: 150px 1fr; grid-template-rows: auto auto; column-gap: 12px;
  border: 1px solid var(--vp-c-divider); border-left: 4px solid var(--lc); border-radius: 8px; padding: 10px 12px;
  background: color-mix(in srgb, var(--lc) 5%, var(--vp-c-bg));
}
.lf-label { grid-row: span 2; display: flex; gap: 8px; align-items: center; text-decoration: none; color: inherit; }
.lf-id { font-weight: 700; color: var(--lc); font-size: 18px; }
.lf-text { display: flex; flex-direction: column; line-height: 1.25; }
.lf-en { font-size: 11px; color: var(--vp-c-text-2); text-transform: uppercase; letter-spacing: .04em; }
.lf-zh { font-weight: 600; }
.lf-boxes { display: flex; flex-wrap: wrap; gap: 6px; }
.lf-box {
  font-size: 13px; padding: 3px 9px; border-radius: 6px; text-decoration: none; color: var(--vp-c-text-1);
  border: 1px solid color-mix(in srgb, var(--lc) 55%, transparent); background: var(--vp-c-bg);
}
.lf-box:hover { border-color: var(--lc); color: var(--lc); }
.lf-box.ph { border-style: dashed; color: var(--vp-c-text-2); }
.lf-box sup { margin-left: 3px; font-size: 10px; color: var(--vp-c-text-2); }
.lf-scope { font-size: 12px; color: var(--vp-c-text-2); margin-top: 6px; }
@media (max-width: 640px) {
  .lf-row { grid-template-columns: 1fr; }
  .lf-label { grid-row: auto; margin-bottom: 6px; }
}
</style>
