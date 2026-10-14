<script setup lang="ts">
import { withBase } from 'vitepress'
import { data as topics } from '../../data/topics.data'
import { data as problems } from '../../data/problems.data'
import { layerByDir } from '../../layers'
import { problemsOf } from '../problems'
import { nest } from '../../nest'

// 每层 index.md 里的目录：一篇一行，带状态和挂的题数；子套路缩进列在父页下面
const props = defineProps<{ dir: string }>()
const layer = layerByDir[props.dir]
const items = nest(
  topics.filter((t) => t.dir === props.dir).map((t) => ({ ...t, n: problemsOf(problems, layer, t).length })),
  props.dir,
)
const label = { todo: '占位', draft: '草稿', reviewed: '已过' } as const
</script>

<template>
  <ul class="li">
    <template v-for="t in items" :key="t.url">
      <li v-for="(c, i) in [t, ...t.children]" :key="c.url" :class="{ sub: i > 0 }">
        <a :href="withBase(c.url)">{{ c.title }}</a>
        <span class="li-st" :class="c.status">{{ label[c.status] }}</span>
        <span v-if="c.n" class="li-n">{{ c.n }} 题</span>
      </li>
    </template>
  </ul>
</template>

<style scoped>
.li { list-style: none; padding: 0 !important; }
.li li { display: flex; gap: 10px; align-items: baseline; }
.li li.sub { padding-left: 1.5em; }
.li li.sub::before { content: '└'; color: var(--vp-c-text-3); margin-right: -4px; }
.li-st { font-size: 11px; padding: 0 6px; border-radius: 4px; background: var(--vp-c-default-soft); color: var(--vp-c-text-2); }
.li-st.draft { background: var(--vp-c-brand-soft); color: var(--vp-c-brand-1); }
.li-st.reviewed { background: color-mix(in srgb, #22c55e 18%, transparent); color: #16a34a; }
.li-n { font-size: 12px; color: var(--vp-c-text-3); }
</style>
