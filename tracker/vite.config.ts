import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

// 前端源码在 dashboard/web/, 产物在 dashboard/web/dist/ —— server.py 和 export_static.py 都从那儿读。
// 开发时 `npm run dev` 起 Vite(热更新), /api 代理给另开的 `python dashboard/server.py`。
export default defineConfig({
  root: fileURLToPath(new URL('./dashboard/web', import.meta.url)),
  // 相对路径: 同一份产物既挂在本地根路径, 也挂在 GitHub Pages 的 /leetcode/ 子路径下
  base: './',
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./dashboard/web/src', import.meta.url)) },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:8765' },
  },
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
})
