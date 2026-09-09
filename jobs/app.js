'use strict';
// 求职看板前端。无构建, Vue 从 vendor/ 本地加载(和 dashboard 一样 —— 断网也要能用)。
//
// 唯一真相在后端两个文件: plan.json(方法论, 可公开) + data/applications.json(状态, 私密)。
// 这里所有统计都是**现算**的, 没有第二份状态 —— 改一格状态, 时间线和漏斗立刻跟着变。

const { createApp } = Vue;

const VIEWS = [
  { k: 'timeline', t: '时间线' },
  { k: 'board', t: '公司' },
  { k: 'jds', t: '岗位' },
  { k: 'funnel', t: '漏斗' },
];
// 岗位的资历档。和 scan_board.py / watch_boards.py 的分桶用同一套词, 免得两处对不上。
const LV = { '': '—', ng: 'entry/NG', mid: '中级', sr: '资深' };
const SIZE = { large: '大厂', mid: '中型', small: '小' };
// 主视图是只读的, 所以枚举值要有给人看的中文label
const REF = { none: '—', asked: '已请求', got: '已到位' };
const ST = { pool: '池子', todo: '未投递', applied: '已投', oa: 'OA', screen: '电面', onsite: 'onsite' };
const OC = { '': '在跑', offer: 'offer', rejected: '被拒', closed: '没招', withdrawn: '撤回' };
const CONTACT = ['oa', 'screen', 'onsite'];      // 「首次真人接触 / OA」以上的阶段

const iso = (d) => d.toISOString().slice(0, 10);
const addDays = (s, n) => {
  const d = new Date(s + 'T00:00:00');
  d.setDate(d.getDate() + n);
  return iso(d);
};
const daysBetween = (a, b) =>
  Math.round((new Date(b + 'T00:00:00') - new Date(a + 'T00:00:00')) / 864e5);

createApp({
  data() {
    return {
      VIEWS, REF, ST, OC, LV,
      plan: {},
      apps: [],
      view: localStorage.getItem('jb-view') || 'timeline',
      tierF: 'all',
      liveOnly: false,
      bridgeOnly: false,
      ngOnly: false,
      newName: '',
      newTier: 'C',
      jdTierF: 'all',
      jdLvF: 'all',
      jdQ: '',
      jdOpen: null,        // 详情里正在展开编辑的那条 jd
      cur: null,
      bulkOpen: false,
      bulkText: '',
      msg: '',
      // 只读静态站(GitHub Pages)由 static-shim.js 挂上 .ro —— 那边没有写接口
      ro: document.documentElement.classList.contains('ro'),
    };
  },

  computed: {
    anchor() { return this.plan.anchor || iso(new Date()); },
    today() { return iso(new Date()); },

    weekNow() { return Math.max(0, Math.floor(daysBetween(this.anchor, this.today) / 7)); },

    anchorLine() {
      return `W0 = ${this.anchor} · 今天 ${this.today} · 第 W${this.weekNow} 周`;
    },

    budgetTotal() { return (this.plan.tiers || []).reduce((s, t) => s + t.budget, 0); },

    /** 本周该主攻哪一组 —— 按时间线的窗口, 落在窗口之后就一直算最后那组 */
    tierNow() {
      const ts = this.plan.tiers || [];
      const hit = ts.find((t) => this.weekNow >= t.weeks[0] && this.weekNow <= t.weeks[1]);
      if (hit) return hit.k;
      const started = ts.filter((t) => this.weekNow > t.weeks[1]);
      return started.length ? started[started.length - 1].k : (ts[0] || {}).k;
    },

    /** 每周实际投了几家, 按 tier 分桶。key = 'W|tier' */
    actualByWeek() {
      const m = {};
      for (const a of this.apps) {
        if (!a.applied || a.status === 'pool' || a.status === 'todo') continue;
        const w = Math.max(0, Math.floor(daysBetween(this.anchor, a.applied) / 7));
        m[w + '|' + a.tier] = (m[w + '|' + a.tier] || 0) + 1;
        m[w] = (m[w] || 0) + 1;
      }
      return m;
    },

    weeks() {
      return (this.plan.weeks || []).map((w) => {
        const planArr = Object.entries(w.apply || {}).map(([tier, n]) => {
          const actual = this.actualByWeek[w.w + '|' + tier] || 0;
          return { tier, n, actual, pct: Math.min(100, (actual * 100) / n) };
        });
        return {
          ...w,
          date: addDays(this.anchor, w.w * 7),
          plan: planArr,
          plannedTotal: planArr.reduce((s, p) => s + p.n, 0),
          actualTotal: this.actualByWeek[w.w] || 0,
        };
      });
    },

    /** 三层转化率 —— 每一层诊断不同的问题, 所以分开看而不是只看一个总数 */
    rate() {
      const A = this.st(), C = this.st('C');
      return {
        all1: this.div(A.contact, A.applied),
        all2: this.div(A.onsite, A.contact),
        all3: this.div(A.offer, A.onsite),
        C1: this.div(C.contact, C.applied),
      };
    },

    funnelRows() {
      const A = this.st();
      const nums = [
        { num: A.contact, den: A.applied, r: this.rate.all1 },
        { num: A.onsite, den: A.contact, r: this.rate.all2 },
        { num: A.offer, den: A.onsite, r: this.rate.all3 },
      ];
      return (this.plan.funnel || []).map((f, i) => {
        const n = nums[i];
        // 样本太少时不判色 —— 3 家投出去算出的 0% 什么也说明不了
        const cls = n.den < 10 ? 'thin' : n.r >= f.prior ? 'good' : n.r >= f.prior * 0.5 ? 'warn' : 'bad';
        return { ...f, ...n, cls };
      });
    },

    /** W3 校准点: 拿 C 实测首响率去查 plan.rules.w3_gate */
    gate() {
      const rules = (this.plan.rules || {}).w3_gate || [];
      const C = this.st('C');
      if (C.applied < 10) {
        return { cls: 'thin', verdict: '样本不足', action: `C 已投 ${C.applied} 家 —— 至少投满 10 家再看这个数, 否则只是噪音。` };
      }
      return rules.find((r) => this.rate.C1 >= r.min) || rules[rules.length - 1] || {};
    },

    groups() {
      return (this.plan.tiers || [])
        .filter((t) => this.tierF === 'all' || this.tierF === t.k)
        .map((t) => {
          let rows = this.apps.filter((a) => a.tier === t.k);
          if (this.liveOnly) rows = rows.filter((a) => !a.outcome || a.outcome === 'offer');
          if (this.bridgeOnly) rows = rows.filter((a) => a.bridge);
          if (this.ngOnly) rows = rows.filter((a) => a.ng);
          rows.sort((x, y) =>
            ((y.ng || 0) - (x.ng || 0)) ||
            (y.bridge - x.bridge) ||
            (this.rank(y) - this.rank(x)) ||
            x.n.localeCompare(y.n));
          return { k: t.k, t: t.t, d: t.d, role: t.role, budget: t.budget, rows, b: this.bucket(this.apps.filter((a) => a.tier === t.k)) };
        });
    },

    bulkCount() { return this.bulkText.split('\n').filter((x) => x.trim()).length; },

    // 岗位视图: 把每家的 jds 摊平成一张表。公司仍是漏斗的分母 —— 这里只是明细,
    // 所以每行带的是**所属公司的**阶段/结局, 岗位本身不单独记状态。
    jdRows() {
      const order = (this.plan.tiers || []).map((t) => t.k);
      const q = this.jdQ.trim().toLowerCase();
      const out = [];
      for (const a of this.apps) {
        if (this.jdTierF !== 'all' && a.tier !== this.jdTierF) continue;
        if (this.liveOnly && a.outcome && a.outcome !== 'offer') continue;
        for (const j of a.jds || []) {
          if (this.jdLvF !== 'all' && (j.lv || '') !== this.jdLvF) continue;
          if (q && !(`${a.n} ${j.role} ${j.loc} ${j.note}`.toLowerCase().includes(q))) continue;
          out.push({ a, j });
        }
      }
      out.sort((x, y) =>
        (order.indexOf(x.a.tier) - order.indexOf(y.a.tier)) ||
        x.a.n.localeCompare(y.a.n) ||
        (y.j.pick - x.j.pick));
      return out;
    },

    // 摊平后有多少家公司还一条岗位都没记 —— 这个数就是「还没查 JD」的欠账
    jdGap() { return this.apps.filter((a) => !(a.jds || []).length).length; },

    headline() {
      const A = this.st();
      return `已投 ${A.applied}/${this.budgetTotal} · 首响 ${A.contact} · onsite ${A.onsite} · offer ${A.offer}`;
    },
  },

  methods: {
    setView(k) { this.view = k; localStorage.setItem('jb-view', k); },
    edit(a) { this.cur = a; },

    scanTip(a) {
      if (!a.scan_at) return '还没扫过 —— python3 jobs/scan_board.py ' + a.id;
      return `${a.scan_at} 扫: 在招 ${a.scan_n} 个, 工程岗里 entry ${a.scan_ng} · `
        + `中级 ${a.scan_mid} · 资深 ${a.scan_sr}`;
    },

    /** plan.json 里的散文带 **强调** —— 先转义再只认这一个记号, 不引第二个 markdown 库。
        转义在前, 所以 plan.json 里就算写了 <script> 也只会当字面量显示。 */
    md(s) {
      return String(s == null ? '' : s)
        .replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]))
        .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
    },
    sizeT(s) { return SIZE[s] || s; },
    div(a, b) { return b ? a / b : 0; },
    pct(r) { return (r * 100).toFixed(0) + '%'; },
    rank(a) { return ['pool', 'todo', 'applied', 'oa', 'screen', 'onsite'].indexOf(a.status); },

    bucket(rows) {
      // pool 和 todo 都还没投出去 —— 漏斗的分母从 applied 才开始
      const applied = rows.filter((a) => a.status !== 'pool' && a.status !== 'todo');
      return {
        pool: rows.length,
        applied: applied.length,
        contact: applied.filter((a) => CONTACT.includes(a.status)).length,
        onsite: applied.filter((a) => a.status === 'onsite').length,
        offer: applied.filter((a) => a.outcome === 'offer').length,
      };
    },
    st(tier) { return this.bucket(tier ? this.apps.filter((a) => a.tier === tier) : this.apps); },

    dueCls(a) {
      if (!a.due || a.outcome) return '';
      const d = daysBetween(this.today, a.due);
      return d < 0 ? 'due-bad' : d <= 3 ? 'due-warn' : '';
    },

    flash(t) { this.msg = t; setTimeout(() => (this.msg = ''), 1600); },

    async set(a, field, value) {
      if (this.ro) return;
      const old = a[field];
      a[field] = value;                                  // 乐观更新: 统计立刻跟着动
      const r = await fetch('/api/apps/' + a.id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [field]: value }),
      }).catch(() => null);
      if (!r || !r.ok) { a[field] = old; return this.flash('保存失败'); }
      Object.assign(a, await r.json());                  // 后端可能顺手补了 applied 日期
      this.flash('已保存');
    },

    // ── 岗位 ──────────────────────────────────────────────────────────
    // 全部走 /api/apps/<id>/jds, 后端回整条公司记录 —— 主岗同步(role/url)在那边做,
    // 前端直接整条替换, 不自己拼状态。
    async jdCall(a, url, opt) {
      if (this.ro) return null;
      const r = await fetch(url, opt).catch(() => null);
      if (!r || !r.ok) { this.flash('保存失败'); return null; }
      const fresh = await r.json();
      Object.assign(a, fresh);
      if (this.cur && this.cur.id === a.id) Object.assign(this.cur, fresh);
      const i = this.apps.findIndex((x) => x.id === a.id);
      if (i >= 0) Object.assign(this.apps[i], fresh);
      this.flash('已保存');
      return fresh;
    },

    addJd(a) {
      return this.jdCall(a, `/api/apps/${a.id}/jds`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: '', url: '' }),
      }).then((f) => { if (f) this.jdOpen = f.jds[f.jds.length - 1].id; });
    },

    setJd(a, j, field, value) {
      if (j[field] === value) return;
      j[field] = value;                                  // 乐观更新
      return this.jdCall(a, `/api/apps/${a.id}/jds/${j.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [field]: value }),
      });
    },

    pickJd(a, j) {
      return this.jdCall(a, `/api/apps/${a.id}/jds/${j.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pick: 1 }),
      });
    },

    delJd(a, j) {
      if (this.ro || !confirm(`删掉这条岗位?\n${j.role || j.url || '(空)'}`)) return;
      return this.jdCall(a, `/api/apps/${a.id}/jds/${j.id}`, { method: 'DELETE' });
    },

    // 岗位视图里点一行 -> 跳回公司详情, 并把这条岗位展开
    openFrom(row) {
      this.jdOpen = row.j.id;
      this.view = 'board';
      this.edit(row.a);
    },

    async del(a) {
      if (this.ro || !confirm(`删掉 ${a.n}?`)) return;
      const r = await fetch('/api/apps/' + a.id, { method: 'DELETE' }).catch(() => null);
      if (!r || !r.ok) return this.flash('删除失败');
      // 后端把 id 记进 dropped, 所以下次启动不会被 plan.json 的 pool 种回来
      this.apps = this.apps.filter((x) => x.id !== a.id);
      this.cur = null;
      this.flash('已删除');
    },

    async addBulk() {
      const names = this.bulkText.split('\n').map((x) => x.trim()).filter(Boolean);
      if (!names.length || this.ro) return;
      const r = await fetch('/api/apps/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ names, tier: this.newTier }),
      });
      if (!r.ok) return this.flash('添加失败');
      const { added } = await r.json();
      this.apps.push(...added);
      this.bulkText = '';
      this.bulkOpen = false;
      this.flash(`加了 ${added.length} 家`);
    },

    async add() {
      const n = this.newName.trim();
      if (!n || this.ro) return;
      const r = await fetch('/api/apps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n, tier: this.newTier }),
      });
      if (!r.ok) return this.flash('添加失败');
      this.apps.push(await r.json());
      this.newName = '';
      this.flash('已添加');
    },

    async load() {
      const [p, a] = await Promise.all([
        fetch('/api/plan').then((r) => r.json()),
        fetch('/api/apps').then((r) => r.json()),
      ]);
      this.plan = p;
      this.apps = a.apps || [];
    },
  },

  mounted() { this.load(); },
}).mount('#app');
