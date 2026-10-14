<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'
import { data as problems } from '../../data/problems.data'
import { layerByDir } from '../../layers'
import { problemsOf } from '../problems'

// 挂在每篇正文后面：tracker 里打了这个标签的题，最生的排前面（熟练度 4 → 0，未评垫底）。
const { page, frontmatter } = useData()
const list = computed(() => {
  const [dir, slug] = page.value.relativePath.replace(/\.md$/, '').split('/')
  const layer = layerByDir[dir]
  if (!layer || !slug || slug === 'index') return []
  return problemsOf(problems, layer, { slug, alias: frontmatter.value.alias ?? [] }).sort(
    (a, b) => (b.familiarity ?? -1) - (a.familiarity ?? -1) || a.id - b.id,
  )
})
const famText = (f: number | null) => (f === null ? '未评' : `L${f}`)
const famCls = (f: number | null) => (f === null ? 'na' : f >= 3 ? 'weak' : f >= 2 ? 'mid' : 'ok')
</script>

<template>
  <section v-if="list.length" class="pl">
    <h2>挂在这里的题 <span class="pl-n">{{ list.length }}</span></h2>
    <p class="pl-hint">从 tracker 的 meta.json 现读，按熟练度从生到熟排。</p>
    <ul>
      <li v-for="p in list" :key="p.id">
        <span class="pl-fam" :class="famCls(p.familiarity)">{{ famText(p.familiarity) }}</span>
        <a :href="p.url" target="_blank" rel="noreferrer">{{ p.id }}. {{ p.title }}</a>
        <span class="pl-diff" :class="p.difficulty">{{ p.difficulty }}</span>
        <span v-if="p.status === 'todo'" class="pl-todo">todo</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.pl { margin-top: 48px; border-top: 1px solid var(--vp-c-divider); padding-top: 8px; }
.pl h2 { border-top: none !important; margin-top: 8px !important; }
.pl-n { font-size: 14px; color: var(--vp-c-text-2); font-weight: 400; }
.pl-hint { font-size: 13px; color: var(--vp-c-text-2); }
.pl ul { list-style: none; padding: 0 !important; columns: 2 280px; }
.pl li { display: flex; gap: 8px; align-items: baseline; margin: 2px 0 !important; break-inside: avoid; font-size: 14px; }
.pl-fam { font-size: 11px; font-weight: 600; padding: 0 5px; border-radius: 4px; min-width: 34px; text-align: center; }
.pl-fam.weak { background: color-mix(in srgb, #ef4444 20%, transparent); color: #dc2626; }
.pl-fam.mid { background: color-mix(in srgb, #f59e0b 20%, transparent); color: #b45309; }
.pl-fam.ok { background: color-mix(in srgb, #22c55e 20%, transparent); color: #15803d; }
.pl-fam.na { background: var(--vp-c-default-soft); color: var(--vp-c-text-2); }
.pl-diff, .pl-todo { font-size: 11px; color: var(--vp-c-text-3); }
.pl-diff.hard { color: #dc2626; }
.dark .pl-fam.weak { color: #f87171; }
.dark .pl-fam.mid { color: #fbbf24; }
.dark .pl-fam.ok { color: #4ade80; }
</style>
