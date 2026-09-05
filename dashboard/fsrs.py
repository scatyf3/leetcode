#!/usr/bin/env python3
"""
FSRS-6 调度器 —— 纯标准库, 零依赖.

逐函数移植自官方参考实现 py-fsrs:
  https://github.com/open-spaced-repetition/py-fsrs  (fsrs/scheduler.py)
私有函数名和上游保持一致, 方便日后对照升级. **公式和权重都是从上游抄的, 不是凭记忆写的** ——
改动这里之前先去看上游那份, 数值算错了不会报错, 只会让复习节奏悄悄变得没有意义.

和上游的两点差异(都是刻意的):
  1. 时间粒度是"天"(YYYY-MM-DD 本地日期), 不是 datetime。看板一天最多复习一轮, 不需要更细。
  2. learning_steps / relearning_steps 都是空的 —— 也就是不做 Anki 那种"10 分钟后再问一次"。
     上游在这两个列表为空时, 状态机会直接塌缩成"永远 Review + _next_interval", 所以这份移植
     只需要实现那一条路径, 且结果和上游 Scheduler(learning_steps=(), relearning_steps=()) 一致。
     评 Again 时 FSRS 给的间隔仍然至少 1 天; "今天再问一遍"是前端把它排回本次队尾做的, 不改 due。

自测:
    python dashboard/fsrs.py --selftest
"""
import json
import math
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARAMS_FILE = HERE / "fsrs_params.json"    # 可选覆盖; 以后跑优化器把结果丢这里就行

# --- 上游 DEFAULT_PARAMETERS, 逐个抄下来 ---------------------------------------
# 前 20 个是权重, 第 21 个(w[20])是 FSRS_DEFAULT_DECAY。
FSRS_DEFAULT_DECAY = 0.1542
DEFAULT_W = [
    0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001,
    1.8722, 0.1666, 0.796, 1.4835, 0.0614, 0.2629, 1.6483, 0.6014,
    1.8729, 0.5425, 0.0912, 0.0658,
    FSRS_DEFAULT_DECAY,
]
DEFAULT_RETENTION = 0.9        # desired_retention
MAXIMUM_INTERVAL = 36500

STABILITY_MIN = 0.001
MIN_DIFFICULTY = 1.0
MAX_DIFFICULTY = 10.0

RATINGS = (1, 2, 3, 4)         # 1=Again 2=Hard 3=Good 4=Easy


# ------------------------------------------------------------------ params ----
_CACHE = {"mtime": None, "params": None}


def load_params() -> dict:
    """{"w": [...], "retention": 0.9}. fsrs_params.json 存在就用它, 按 mtime 缓存。"""
    if not PARAMS_FILE.exists():
        return {"w": list(DEFAULT_W), "retention": DEFAULT_RETENTION}
    mt = PARAMS_FILE.stat().st_mtime
    if _CACHE["mtime"] != mt:
        try:
            raw = json.loads(PARAMS_FILE.read_text(encoding="utf-8"))
            w = [float(x) for x in raw.get("w") or DEFAULT_W]
            _CACHE["params"] = {"w": w,
                                "retention": float(raw.get("retention") or DEFAULT_RETENTION)}
            _CACHE["mtime"] = mt
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return {"w": list(DEFAULT_W), "retention": DEFAULT_RETENTION}
    return _CACHE["params"]


def _decay_factor(w):
    """上游: self._DECAY = -w[20]; self._FACTOR = 0.9 ** (1 / _DECAY) - 1 (这里的 0.9 是写死的)。"""
    decay = -(w[20] if len(w) > 20 else 0.5)     # 19 权重的 FSRS-5 参数也能加载
    factor = 0.9 ** (1 / decay) - 1
    return decay, factor


# ------------------------------------------------------------------ 公式 ------
def _clamp_difficulty(difficulty: float) -> float:
    return min(max(difficulty, MIN_DIFFICULTY), MAX_DIFFICULTY)


def _clamp_stability(stability: float) -> float:
    return max(stability, STABILITY_MIN)


def _initial_stability(w, rating: int) -> float:
    return _clamp_stability(w[rating - 1])


def _initial_difficulty(w, rating: int, clamp: bool = True) -> float:
    d = w[4] - (math.e ** (w[5] * (rating - 1))) + 1
    return _clamp_difficulty(d) if clamp else d


def _linear_damping(delta_difficulty: float, difficulty: float) -> float:
    return (10.0 - difficulty) * delta_difficulty / 9.0


def _mean_reversion(w, arg_1: float, arg_2: float) -> float:
    return w[7] * arg_1 + (1 - w[7]) * arg_2


def _next_difficulty(w, difficulty: float, rating: int) -> float:
    arg_1 = _initial_difficulty(w, 4, clamp=False)          # Easy, 不 clamp
    delta = -(w[6] * (rating - 3))
    arg_2 = difficulty + _linear_damping(delta, difficulty)
    return _clamp_difficulty(_mean_reversion(w, arg_1, arg_2))


def _short_term_stability(w, stability: float, rating: int) -> float:
    """同一天内再评一次走这条(elapsed_days < 1)。"""
    inc = (math.e ** (w[17] * (rating - 3 + w[18]))) * (stability ** -w[19])
    if rating in (2, 3, 4):
        inc = max(inc, 1.0)
    return _clamp_stability(stability * inc)


def _next_forget_stability(w, difficulty, stability, retrievability) -> float:
    long_term = (w[11]
                 * (difficulty ** -w[12])
                 * (((stability + 1) ** w[13]) - 1)
                 * (math.e ** ((1 - retrievability) * w[14])))
    short_term = stability / (math.e ** (w[17] * w[18]))
    return min(long_term, short_term)


def _next_recall_stability(w, difficulty, stability, retrievability, rating: int) -> float:
    hard_penalty = w[15] if rating == 2 else 1
    easy_bonus = w[16] if rating == 4 else 1
    return stability * (
        1
        + (math.e ** w[8])
        * (11 - difficulty)
        * (stability ** -w[9])
        * ((math.e ** ((1 - retrievability) * w[10])) - 1)
        * hard_penalty
        * easy_bonus
    )


def _next_stability(w, difficulty, stability, retrievability, rating: int) -> float:
    if rating == 1:
        s = _next_forget_stability(w, difficulty, stability, retrievability)
    else:
        s = _next_recall_stability(w, difficulty, stability, retrievability, rating)
    return _clamp_stability(s)


def _retrievability(w, stability: float, elapsed_days: int) -> float:
    decay, factor = _decay_factor(w)
    if not stability:
        return 0.0
    return (1 + factor * max(0, elapsed_days) / stability) ** decay


def _next_interval(w, stability: float, retention: float) -> int:
    decay, factor = _decay_factor(w)
    n = (stability / factor) * ((retention ** (1 / decay)) - 1)
    n = round(n)
    return max(1, min(n, MAXIMUM_INTERVAL))     # 至少 1 天, 最多 100 年


# ------------------------------------------------------------------ 对外 ------
def new_card() -> dict:
    return {"state": "new", "reps": 0, "lapses": 0}


def _parse(d: str):
    return date.fromisoformat(d) if d else None


def review(card: dict, rating: int, today: str, params: dict | None = None):
    """评一次分。返回 (新 card, 间隔天数)。card 不会被就地修改。

    today 是本地日期字符串 'YYYY-MM-DD'。新卡走 _initial_*, 老卡按距上次复习的天数走
    短期(同一天)或长期(跨天)路径 —— 和上游 learning/relearning steps 为空时的行为一致。
    """
    if rating not in RATINGS:
        raise ValueError(f"rating 必须是 1..4, 收到 {rating!r}")
    p = params or load_params()
    w, retention = p["w"], p["retention"]

    c = dict(card or {})
    last = _parse(c.get("last_review", ""))
    now = date.fromisoformat(today)
    elapsed = (now - last).days if last else None

    is_new = c.get("state", "new") == "new" or not c.get("stability")
    if is_new:
        stability = _initial_stability(w, rating)
        difficulty = _initial_difficulty(w, rating)
    else:
        s0, d0 = float(c["stability"]), float(c["difficulty"])
        if elapsed is not None and elapsed < 1:          # 同一天内再评
            stability = _short_term_stability(w, s0, rating)
        else:
            r = _retrievability(w, s0, elapsed or 0)
            stability = _next_stability(w, d0, s0, r, rating)
        difficulty = _next_difficulty(w, d0, rating)

    interval = _next_interval(w, stability, retention)
    out = {
        "state": "review",
        "due": (now + timedelta(days=interval)).isoformat(),
        "last_review": today,
        # 不四舍五入: 下一次复习是从这个值接着算的, 存成 4 位小数会一路复利式地漂,
        # 和上游 py-fsrs 对不上数(间隔本身不受影响, 但对拍会一直红)。显示时再截。
        "stability": stability,
        "difficulty": difficulty,
        "reps": int(c.get("reps") or 0) + 1,
        "lapses": int(c.get("lapses") or 0) + (1 if rating == 1 and not is_new else 0),
        "last_rating": rating,
    }
    return out, interval


def preview(card: dict, today: str, params: dict | None = None) -> dict:
    """四个按钮各自会排到几天后 —— 只算不写, 用来标在按钮上。"""
    p = params or load_params()
    return {str(r): review(card, r, today, p)[1] for r in RATINGS}


def retrievability(card: dict, today: str, params: dict | None = None) -> float:
    """今天还记得住的概率(0-1)。新卡返回 0。"""
    p = params or load_params()
    last = _parse((card or {}).get("last_review", ""))
    s = float((card or {}).get("stability") or 0)
    if not last or not s:
        return 0.0
    return _retrievability(p["w"], s, (date.fromisoformat(today) - last).days)


# ------------------------------------------------------------------ 自测 ------
def _selftest():
    today = "2026-01-01"
    print("参数:", len(load_params()["w"]), "个权重, retention =", load_params()["retention"])
    decay, factor = _decay_factor(load_params()["w"])
    print(f"DECAY = {decay}   FACTOR = {factor:.10f}")

    print("\n新卡, 四个按钮各自的间隔(天):", preview(new_card(), today))

    print("\n连续评 Good(3):")
    c, d = new_card(), date.fromisoformat(today)
    for i in range(6):
        c, iv = review(c, 3, d.isoformat())
        print(f"  第{i+1}次  间隔 {iv:>5} 天   S={c['stability']:>9.4f}  D={c['difficulty']:.4f}  due={c['due']}")
        d = date.fromisoformat(c["due"])

    print("\n先 Good 三次再 Again(1):")
    c, d = new_card(), date.fromisoformat(today)
    for _ in range(3):
        c, iv = review(c, 3, d.isoformat()); d = date.fromisoformat(c["due"])
    c2, iv = review(c, 1, d.isoformat())
    print(f"  Again -> 间隔 {iv} 天, S {c['stability']:.4f} -> {c2['stability']:.4f}, lapses={c2['lapses']}")

    print("\n同一天内连评两次 Good(走 short_term 路径):")
    c, _ = review(new_card(), 3, today)
    c2, iv = review(c, 3, today)
    print(f"  S {c['stability']:.4f} -> {c2['stability']:.4f}, 间隔 {iv} 天")

    print("\n保留率(stability=10 的卡, 距上次复习 n 天):")
    w = load_params()["w"]
    for n in (0, 1, 5, 10, 20, 50):
        print(f"  {n:>3} 天 -> {_retrievability(w, 10.0, n):.4f}")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__.strip().split("\n")[0])
        print("用法: python dashboard/fsrs.py --selftest")
