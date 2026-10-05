/**
 * 同步核心, 照搬 ai-infra-inferview 的 src/lib/sync.ts: 读远端 -> 和本地合并 -> 有变化就写回 -> 冲突就重来。
 * 只依赖一个抽象的 Remote, GitHub 的实现见 github.ts。
 *
 * 这边只有一份数据(复习事件, 见 inbox.ts), merge 是按 eid 取并集, 所以把一份旧的本地副本
 * 整份并进去永远安全。
 */

export interface DocSpec<T> {
  /** 仓库里的路径 */
  path: string
  /** 给人看的名字, 用在同步的 commit 信息里 */
  label: string
  empty: () => T
  validate: (v: unknown) => v is T
  /** 合并两份; 结果和参数顺序无关 */
  merge: (a: T, b: T) => T
  serialize: (v: T) => string
}

export interface RemoteFile {
  path: string
  text: string
}

export interface RemoteSnapshot {
  /** 路径 → 文件内容；文件不存在为 null */
  texts: Record<string, string | null>
  /** 读到的版本（GitHub 上是分支 head 的 commit）；写的时候带上，版本变了就拒绝 */
  version: string | null
}

export interface Remote {
  read(paths: string[]): Promise<RemoteSnapshot>
  /** 版本对不上时抛 StaleError */
  write(files: RemoteFile[], version: string | null, summary: string): Promise<void>
}

/** 写的时候远端已经被别人改过了：重读、重合并、再写 */
export class StaleError extends Error {
  constructor(message = '远端已经有更新的提交') {
    super(message)
    this.name = 'StaleError'
  }
}

/** 远端文件存在但格式不对：不要拿本地数据盖掉它，交给人处理 */
export class InvalidRemoteError extends Error {
  constructor(path: string) {
    super(`远端的 ${path} 格式不对，没有同步。请先修好这个文件`)
    this.name = 'InvalidRemoteError'
  }
}

export interface SyncTarget<T> {
  spec: DocSpec<T>
  get(): T
  /** 合并后的结果写回本地（内存 + 本地缓存） */
  set(v: T): void
}

export function parseRemote<T>(spec: DocSpec<T>, text: string | null): T {
  if (text === null) return spec.empty()
  let v: unknown
  try {
    v = JSON.parse(text)
  } catch {
    throw new InvalidRemoteError(spec.path)
  }
  if (!spec.validate(v)) throw new InvalidRemoteError(spec.path)
  return v
}

export interface SyncResult {
  /** 这次写回远端的文件 */
  written: string[]
  /** 因为冲突重试了几次 */
  retries: number
}

/**
 * 同步一轮。读和合并之间没有 await，所以合并时拿到的本地数据就是此刻最新的；
 * 写回期间用户又改了的话，那些改动留在本地，下一轮再同步。
 */
export async function syncDocs(remote: Remote, targets: SyncTarget<any>[], maxRetries = 4): Promise<SyncResult> {
  const paths = targets.map((t) => t.spec.path)
  for (let attempt = 0; ; attempt++) {
    const { texts, version } = await remote.read(paths)
    const changes: RemoteFile[] = []
    const labels: string[] = []
    for (const t of targets) {
      const text = texts[t.spec.path] ?? null
      const merged = t.spec.merge(parseRemote(t.spec, text), t.get())
      t.set(merged)
      const out = t.spec.serialize(merged)
      if (out !== text) {
        changes.push({ path: t.spec.path, text: out })
        labels.push(t.spec.label)
      }
    }
    if (!changes.length) return { written: [], retries: attempt }
    try {
      await remote.write(changes, version, labels.join('、'))
      return { written: changes.map((c) => c.path), retries: attempt }
    } catch (e) {
      if (!(e instanceof StaleError) || attempt >= maxRetries) throw e
    }
  }
}
