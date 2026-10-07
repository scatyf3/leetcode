import type { Familiarity } from './types'

// ---- familiarity (熟练度): 0 最熟(英语讲得清) → 4 完全不会; null = 还没评 ----
// 未评**不是** 0 —— 0 是阶梯顶端。缺键在 meta.json 里就是缺键, 一路 null 到底,
// 千万别写成 `Number(x) || 0`: 那会把没评过的题静默变成最熟的一档。
// 半档 1.5 是故意的: 阶梯的语义是"排序", 不是"计数"。在 L1 和 L2 中间塞一档
// 如果靠重新编号(2 让给新档, 老 2/3/4 各 +1), 就得迁移每个 meta.json,
// 而且从此 `familiarity: 3` 读起来不等于 L3 —— 这文件是手写手读的, 不值当。
// 直接存 1.5, 磁盘上写什么就是什么, 排序照样用数值比较。
export const FAM: Record<number, { short: string; label: string }> = {
  0: { short: 'L0', label: '英语讲得清' },
  1: { short: 'L1', label: '已经熟悉' },
  1.5: { short: 'L1.5', label: '写得对 · 但不是最优解' },
  2: { short: 'L2', label: '思路会 · 细节易写错' },
  2.5: { short: 'L2.5', label: '默写得出 · 道理不熟' },
  3: { short: 'L3', label: '思路大概知道 · 不熟' },
  3.5: { short: 'L3.5', label: '方向对 · 但只是直觉' },
  4: { short: 'L4', label: '思路都不知道' },
}
export const FAM_NONE = { short: '—', label: '未评' }
export const FAM_LEVELS: Familiarity[] = [0, 1, 1.5, 2, 2.5, 3, 3.5, 4, null] // 最熟 -> 最生 -> 未评

export const famOf = (p: { familiarity?: unknown }): Familiarity => {
  const v = p.familiarity
  return v === null || v === undefined || v === '' ? null : Number(v)
}
export const famInfo = (f: Familiarity | undefined) =>
  f === null || f === undefined ? FAM_NONE : FAM[f]
export const famKey = (f: Familiarity | undefined | -1): string =>
  f === null || f === undefined ? 'none' : String(f)
// CSS 类名里不能直接放小数点(`.f1.5` 会被当成两个类), 所以类名用下划线: f1_5。
// 只有类名走这个, 对象键 / data 属性一律还是 famKey。
export const famCls = (f: Familiarity | undefined | -1) => 'f' + famKey(f).replace('.', '_')

// 还没成为卡片的题进复习队列的顺序: 越生的越先
export const FAM_ORDER: Record<string, number> = { 4: 0, 3.5: 1, 3: 2, 2.5: 3, 2: 4, none: 5, 1.5: 6, 1: 7, 0: 8 }

// 坐标系上点方块: 顺着"越来越熟"的方向走, 走到顶再回到未评
export const L_NEXT: Record<string, Familiarity> = { none: 4, 4: 3.5, 3.5: 3, 3: 2.5, 2.5: 2, 2: 1.5, 1.5: 1, 1: 0, 0: null }

// 深度不另存: 由每题 meta.json 的 familiarity 算出来。一个字段, 一条阶梯:
//   L0 英语讲得清                      -> S3 讲得清 (面试门槛)
//   L1 已经熟悉 / L2 思路会·细节易写错  -> S2 写得对 (OA 门槛)
//   L2.5 默写得出·道理不熟             -> S2 (写得对就够 OA; 但离 L0 比 L2 远, 所以排在 L2 后面)
//   L3 思路大概知道·不熟               -> S1 思路清楚
//   L4 思路都不知道 / 未评 / 没建文件夹  -> 还没到 S1
// 阶梯是有序的, 所以 S3 ⊂ S2 ⊂ S1 由构造保证 —— 讲得清的题必然也写得对,
// 不会出现"讲得出但写不对"的题混进 S2 那一列(而 S2 正是判断能不能做 OA 的那列)。
export function depthOf(rec: { familiarity?: unknown } | null | undefined): 0 | 1 | 2 | 3 {
  if (!rec) return 0
  const L = famOf(rec)
  if (L === null) return 0 // 未评 —— 不能落进下面任何区间
  if (L <= 0) return 3 // L0 讲得清
  if (L <= 2.5) return 2 // L1 / L1.5 / L2 / L2.5 —— 都是"跑得过", 够 OA 门槛
  if (L <= 3) return 1 // L3 思路大概知道 —— S1 的下界就划在这儿
  return 0 // L3.5 / L4 —— 方向感不算"思路清楚", 够不着 S1
}

// ---- 账本: 四档互斥的覆盖 / 掌握分解 --------------------------------------
//   没建 ──▶ 见过 ──▶ 摸过 ┬─▶ S2 达标
//                          └─▶ 欠账(摸过但没到 L2)
// 会员题单独摘出来, 不算进"该做还没做"。口径跟 dashboard/progress.py 一字不差。
export interface LedgerRow { id: number; rec?: { familiarity?: unknown } | null }
export function ledgerOf(rows: LedgerRow[], premium: Set<number>) {
  const t = { n: rows.length, seen: 0, touched: 0, s2: 0, debt: 0, absent: 0, prem: 0 }
  for (const p of rows) {
    if (!p.rec) {
      if (premium.has(p.id)) t.prem++
      else t.absent++
      continue
    }
    t.seen++ // 见过 = 建了文件夹, 含已经摸过的
    const L = famOf(p.rec)
    if (L === null) continue // 建了但没评 —— 停在地板上
    t.touched++
    if (L <= 2.5) t.s2++
    else t.debt++
  }
  return t
}
