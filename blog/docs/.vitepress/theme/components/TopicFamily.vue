<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import { data as topics } from '../../data/topics.data'

// 挂在正文前面：子套路页写「属于 X」，父页列出它的子套路。关系来自 frontmatter 的 parent（见 nest.ts）。
const { page } = useData()
const fam = computed(() => {
  const [dir, slug] = page.value.relativePath.replace(/\.md$/, '').split('/')
  const self = topics.find((t) => t.dir === dir && t.slug === slug)
  if (!self) return null
  const parent = self.parent ? topics.find((t) => t.dir === dir && t.slug === self.parent) : undefined
  const children = topics.filter((t) => t.dir === dir && t.parent === slug)
  return parent || children.length ? { parent, children } : null
})
</script>

<template>
  <p v-if="fam" class="tf">
    <template v-if="fam.parent">
      <a :href="withBase(fam.parent.url)">{{ fam.parent.title }}</a> 的子套路
    </template>
    <template v-else>
      子套路：<template v-for="(c, i) in fam.children" :key="c.url"
        ><span v-if="i" class="tf-sep"> · </span><a :href="withBase(c.url)">{{ c.title }}</a></template>
    </template>
  </p>
</template>

<style scoped>
.tf { font-size: 13px; color: var(--vp-c-text-2); margin: 0 0 8px; }
.tf-sep { color: var(--vp-c-text-3); }
</style>
