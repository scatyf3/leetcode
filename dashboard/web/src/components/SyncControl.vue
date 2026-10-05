<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { DATA_REPO } from '@/lib/github'
import { DATA_BRANCH_URL, connectGitHub, disconnectGitHub, syncNow, syncState } from '@/sync'

/**
 * 只读站顶栏上的 ☁: 同步状态 + 设置面板(连 / 断 GitHub、立即同步)。
 * 照着 ai-infra-inferview 的 SyncControl.vue; 同步逻辑在 ../sync.ts。本地 server.py 那份看板不挂它。
 */

const open = ref(false)
const token = ref('')
const busy = ref(false)
const formError = ref('')
const now = ref(Date.now())
let ticker: number | undefined

const label = computed(() => {
  if (syncState.mode === 'off') return '只读'
  if (syncState.status === 'syncing') return '同步中'
  if (syncState.status === 'offline') return syncState.pending ? '离线·待同步' : '离线'
  if (syncState.status === 'error') return '同步失败'
  if (syncState.pending) return '待同步'
  return '已同步'
})
const tone = computed(() => {
  if (syncState.mode === 'off') return 'muted'
  if (syncState.status === 'error') return 'danger'
  if (syncState.status === 'syncing' || syncState.pending || syncState.status === 'offline') return 'warn'
  return 'ok'
})

function ago(t: number): string {
  if (!t) return '还没有'
  const s = Math.round((now.value - t) / 1000)
  if (s < 10) return '刚刚'
  if (s < 60) return `${s} 秒前`
  if (s < 3600) return `${Math.round(s / 60)} 分钟前`
  return new Date(t).toLocaleString()
}

// GitHub 支持用 URL 参数预填 fine-grained token 的表单; 不认的参数会被忽略, 下面也写了手动步骤
const tokenUrl =
  'https://github.com/settings/personal-access-tokens/new?' +
  new URLSearchParams({
    name: 'leetcode 复习同步',
    description: '只读站上的闪卡复习记录推到 data 分支',
    target_name: DATA_REPO.owner,
    contents: 'write',
  })

async function save() {
  if (!token.value.trim()) return
  busy.value = true
  formError.value = ''
  try {
    await connectGitHub(token.value)
    token.value = ''
  } catch (e) {
    formError.value = (e as Error).message
  } finally {
    busy.value = false
  }
}

function disconnect() {
  if (confirm('断开后这台设备不再记录复习(已经记下、还没推上去的留在本机, 重新连上再推)。确定？')) disconnectGitHub()
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && open.value) {
    open.value = false
    e.stopPropagation()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey, true)
  ticker = window.setInterval(() => (now.value = Date.now()), 15_000)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey, true)
  clearInterval(ticker)
})
</script>

<template>
  <div class="sc">
    <button class="ghost sc-btn" :title="`复习记录同步: ${label}`" @click="open = !open; now = Date.now()">
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
        <path d="M7 18a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 18 8.5a4 4 0 0 1-.5 9.5H7z"
              fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" />
      </svg>
      <i class="sc-dot" :class="[tone, { spin: syncState.status === 'syncing' }]" />
      <span class="sc-label">{{ label }}</span>
    </button>

    <Teleport to="body">
      <div v-if="open" class="sc-mask" @click.self="open = false">
        <section class="sc-panel" role="dialog" aria-label="复习记录同步">
          <div class="sc-head">
            <b>复习记录同步</b>
            <button class="sc-x" aria-label="关闭" @click="open = false">×</button>
          </div>

          <p class="sc-muted">
            连上 GitHub 之后, 这里的 🧠 复习可以评分 / 暂停 / 批注: 先存在这台设备上, 再推到仓库的
            <code>{{ DATA_REPO.branch }}</code> 分支。电脑上跑 <code>server.py</code>(启动时、点 ↻ Sync 时)会拉下来,
            落进各题的 <code>meta.json</code> 和 <code>reviews.jsonl</code>, commit 之后这边就看到了。
          </p>

          <template v-if="syncState.mode === 'github'">
            <dl class="sc-kv">
              <dt>账号</dt>
              <dd>{{ syncState.login || '—' }}</dd>
              <dt>状态</dt>
              <dd :class="tone">{{ label }}</dd>
              <dt>上次同步</dt>
              <dd>{{ ago(syncState.lastSync) }}</dd>
              <dt>等电脑落盘</dt>
              <dd>{{ syncState.waiting ? `${syncState.waiting} 条` : '没有' }}</dd>
              <dt>存在</dt>
              <dd><a :href="DATA_BRANCH_URL" target="_blank" rel="noreferrer">{{ DATA_REPO.branch }} 分支的 sync-inbox.json</a></dd>
            </dl>
            <p v-if="syncState.error" class="sc-err">{{ syncState.error }}</p>
            <div class="sc-row">
              <button class="sc-primary" :disabled="syncState.status === 'syncing'" @click="syncNow">立即同步</button>
              <span class="sc-spacer" />
              <button class="ghost" @click="disconnect">断开</button>
            </div>
          </template>

          <template v-else>
            <p>现在: <b>只读</b>, 复习只能自测、不记录。</p>
            <p v-if="syncState.waiting" class="sc-muted">本机还有 {{ syncState.waiting }} 条没推上去的记录, 连上就推。</p>
            <ol class="sc-steps">
              <li>
                <a :href="tokenUrl" target="_blank" rel="noreferrer">新建一个 fine-grained token</a>:
                Repository access 选 <i>Only select repositories</i> → <code>{{ DATA_REPO.name }}</code>;
                Permissions 里 <i>Contents</i> 选 <i>Read and write</i>。
              </li>
              <li>粘贴到下面。它只存在这台设备的浏览器里; 手机丢了就去 GitHub 吊销它。</li>
            </ol>
            <form class="sc-row" @submit.prevent="save">
              <input v-model="token" type="password" autocomplete="off" placeholder="github_pat_…" class="sc-input" />
              <button class="sc-primary" type="submit" :disabled="busy || !token.trim()">{{ busy ? '验证中…' : '连接' }}</button>
            </form>
            <p v-if="formError" class="sc-err">{{ formError }}</p>
          </template>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.sc { display: flex; align-items: center; }
.sc-btn { position: relative; display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.sc-dot {
  position: absolute; left: 21px; top: 5px; width: 7px; height: 7px; border-radius: 50%;
  border: 1.5px solid var(--bg); box-sizing: content-box;
}
.sc-dot.ok { background: var(--easy); }
.sc-dot.warn { background: var(--medium); }
.sc-dot.danger { background: var(--hard); }
.sc-dot.muted { background: var(--dim); }
.sc-dot.spin { animation: sc-pulse 1s ease-in-out infinite; }
@keyframes sc-pulse { 50% { opacity: 0.3; } }
@media (max-width: 640px) { .sc-label { display: none; } }

.sc-mask {
  position: fixed; inset: 0; z-index: 200; display: flex; justify-content: center; align-items: flex-start;
  padding: 72px 16px 16px; background: var(--scrim);
}
.sc-panel {
  width: min(440px, 100%); max-height: calc(100vh - 96px); overflow-y: auto; padding: 16px;
  border: 1px solid var(--line); border-radius: 12px; background: var(--bg); color: var(--fg);
  box-shadow: var(--shadow-3); font-size: 14px; line-height: 1.6;
}
.sc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; font-size: 16px; }
.sc-x { font-size: 22px; line-height: 1; padding: 0 6px; background: none; color: var(--dim); }
.sc-panel p { margin: 8px 0; }
.sc-panel code { font-family: var(--font-mono); font-size: 12px; background: var(--soft); padding: 0 4px; border-radius: 4px; }
.sc-panel a { color: var(--accent); }
.sc-muted { color: var(--dim); font-size: 13px; }
.sc-err { color: var(--hard); font-size: 13px; word-break: break-word; }
.sc-kv { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin: 12px 0; }
.sc-kv dt { color: var(--dim); }
.sc-kv dd { margin: 0; }
.sc-kv .ok { color: var(--easy); }
.sc-kv .warn { color: var(--medium); }
.sc-kv .danger { color: var(--hard); }
.sc-steps { margin: 8px 0; padding-left: 20px; }
.sc-steps li { margin: 4px 0; }
.sc-row { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
.sc-spacer { flex: 1; }
.sc-input {
  flex: 1; min-width: 0; height: 38px; padding: 0 10px; border: 1px solid var(--line); border-radius: 8px;
  background: var(--panel); color: var(--fg);
  font-size: 16px;   /* 16px 以下 iOS 聚焦时会自动放大页面 */
}
.sc-primary { height: 38px; padding: 0 14px; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 500; }
.sc-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
