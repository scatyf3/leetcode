'use strict';
const $ = (s) => document.querySelector(s);
const api = (u, opt) => fetch(u, opt).then((r) => r.json());
// 空安全绑定。底下有 40 多条顶层 addEventListener, 最后一行才是 reload() ——
// 只要有一个元素不存在(典型场景: 浏览器拿了缓存的旧 index.html 配新 app.js),
// 一个 TypeError 就会掐断整个顶层脚本, 连 reload() 都跑不到, 表现是**整页卡死**。
// 宁可少绑一个按钮 + 在 console 上喊一声, 也不能让页面起不来。
const on = (sel, ev, fn, opt) => {
  const el = $(sel);
  if (el) el.addEventListener(ev, fn, opt);
  else console.warn(`[wire] 找不到 ${sel} —— 该按钮不会响应。多半是 index.html 是旧的, 强刷一下`);
};

let PROBLEMS = [];
let SYNTAX = [];           // 语法牌组的全部卡片(/api/syntax), 见 dashboard/syntax.py
let CURRENT = null; // detail object

// ---- familiarity (熟练度): 0 最熟(英语讲得清) → 4 完全不会; null = 还没评 ----
// 未评**不是** 0 —— 0 是阶梯顶端。缺键在 meta.json 里就是缺键, 一路 null 到底,
// 千万别写成 `Number(x) || 0`: 那会把没评过的题静默变成最熟的一档。
// 半档 1.5 是故意的: 阶梯的语义是"排序", 不是"计数"。在 L1 和 L2 中间塞一档
// 如果靠重新编号(2 让给新档, 老 2/3/4 各 +1), 就得迁移每个 meta.json,
// 而且从此 `familiarity: 3` 读起来不等于 L3 —— 这文件是手写手读的, 不值当。
// 直接存 1.5, 磁盘上写什么就是什么, 排序照样用数值比较。
const FAM = {
  0: { short: 'L0', label: '英语讲得清' },
  1: { short: 'L1', label: '已经熟悉' },
  1.5: { short: 'L1.5', label: '写得对 · 但不是最优解' },
  2: { short: 'L2', label: '思路会 · 细节易写错' },
  3: { short: 'L3', label: '思路大概知道 · 不熟' },
  3.5: { short: 'L3.5', label: '方向对 · 但只是直觉' },
  4: { short: 'L4', label: '思路都不知道' },
};
const FAM_NONE = { short: '—', label: '未评' };
const FAM_LEVELS = [0, 1, 1.5, 2, 3, 3.5, 4, null];   // 最熟 -> 最生 -> 未评
let FAM_FILTER = new Set();          // empty = 不过滤
const famOf = (p) => {
  const v = p.familiarity;
  return v === null || v === undefined || v === '' ? null : Number(v);
};
const famInfo = (f) => (f === null || f === undefined ? FAM_NONE : FAM[f]);
const famKey = (f) => (f === null || f === undefined ? 'none' : String(f));
// CSS 类名里不能直接放小数点(`.f1.5` 会被当成两个类), 所以类名用下划线: f1_5。
// 只有类名走这个, 对象键 / data 属性一律还是 famKey。
const famCls = (f) => 'f' + famKey(f).replace('.', '_');

// ---- board: cluster by 结构 or 范式, cards carry the other dimension + tricks ----
const NO_STRUCT = '未分类';
let GROUP_BY = 'structures';                       // 'structures' | 'paradigms'
const otherDim = () => (GROUP_BY === 'structures' ? 'paradigms' : 'structures');

function buildPanel() {
  buildFamFilter();
  const shown = FAM_FILTER.size
    ? PROBLEMS.filter((p) => FAM_FILTER.has(famOf(p)))
    : PROBLEMS;
  const groups = new Map();            // structure -> [problems]
  for (const p of shown) {
    const keys = p[GROUP_BY].length ? p[GROUP_BY] : [NO_STRUCT];
    for (const k of keys) (groups.get(k) || groups.set(k, []).get(k)).push(p);
  }
  const nStruct = [...groups.keys()].filter((k) => k !== NO_STRUCT).length;
  $('#sub').textContent = GROUP_BY === 'structures' ? '按数据结构分组' : '按算法范式分组';
  $('#count').textContent = FAM_FILTER.size
    ? `${shown.length}/${PROBLEMS.length} 题 · ${nStruct} 类`
    : `${PROBLEMS.length} 题 · ${nStruct} 类`;

  // sort columns alphabetically, 未分类 always last
  const order = [...groups.keys()].sort((a, b) =>
    a === NO_STRUCT ? 1 : b === NO_STRUCT ? -1 : a.localeCompare(b));

  if (!PROBLEMS.length) {
    $('#panel').innerHTML = `<p class="empty-hint">还没有题目。建一个「编号. 标题」文件夹后点 ↻ Sync。</p>`;
    return;
  }
  if (!shown.length) {
    $('#panel').innerHTML = `<p class="empty-hint">这几档熟练度下没有题 — 再点一下上面的按钮取消过滤。</p>`;
    return;
  }

  let h = `<div class="fam-legend">${[0, 1, 1.5, 2, 3, 3.5, 4]
    .map((f) => `<span class="fam ${famCls(f)}">${FAM[f].short}</span>${esc(FAM[f].label)}`)
    .join('<span class="sep">·</span>')}</div>`;
  h += '<div class="groups">';
  for (const g of order) {
    const items = groups.get(g).slice().sort((a, b) => a.id - b.id);
    const openable = g !== NO_STRUCT;
    h += `<div class="group">
      <div class="group-label${openable ? ' openable' : ''}"${openable ? ` data-struct="${esc(g)}" title="打开 ${esc(g)} 通用 trick 文档"` : ''}>
        <span class="group-name">${esc(g)}</span>
        <span class="group-count">${items.length} 题</span>
        <span class="group-bar">${famBar(items)}</span>
        ${openable ? '<span class="group-open">通用 trick →</span>' : ''}</div>
      <div class="group-rows">${items.map(rowHTML).join('')}</div>
    </div>`;
  }
  h += '</div>';
  $('#panel').innerHTML = h;
  wireCards();
}

function buildFamFilter() {
  const counts = new Map(FAM_LEVELS.map((f) => [f, 0]));
  for (const p of PROBLEMS) counts.set(famOf(p), (counts.get(famOf(p)) || 0) + 1);
  $('#fam-filter').innerHTML = FAM_LEVELS
    .filter((f) => counts.get(f))                   // hide buckets nobody is in
    .map((f) => `<button class="fam-btn ${famCls(f)}${FAM_FILTER.has(f) ? ' on' : ''}"
        data-fam="${famKey(f)}" title="${esc(famInfo(f).label)}">${famInfo(f).short}
        <span class="fam-n">${counts.get(f)}</span></button>`)
    .join('');
  document.querySelectorAll('.fam-btn').forEach((b) =>
    b.addEventListener('click', () => {
      const f = b.dataset.fam === 'none' ? null : +b.dataset.fam;
      FAM_FILTER.has(f) ? FAM_FILTER.delete(f) : FAM_FILTER.add(f);
      buildPanel();
    })
  );
}

// 组标签上的熟练度分布: 一条按 L0→L4 排的堆叠条。分母是这一组, 不是全库 ——
// 想知道的是"这个结构我握得怎么样", 不是"它占全库多少"。
function famBar(items) {
  return FAM_LEVELS
    .map((f) => [f, items.filter((p) => famOf(p) === f).length])
    .filter(([, n]) => n)
    .map(([f, n]) => `<i class="${famCls(f)}" style="flex:${n}"
      title="${esc(famInfo(f).short)} ${esc(famInfo(f).label)} — ${n} 题"></i>`)
    .join('');
}

function rowHTML(p) {
  const diff = p.difficulty || 'none';
  const todo = p.status === 'todo' ? ' todo' : '';
  // 另一个维度(按结构分组时是范式, 反之是结构)单独占一列 —— 这一列是"× 范式"里的
  // 那个乘号, 竖着能扫才有意义, 所以别和 trick 混在同一个右对齐的口袋里。
  const paras = p[otherDim()].map((x) => `<span class="tag para">${esc(x)}</span>`).join('');
  // trick 是这道题的注脚, 不是维度: 压到最后一格, 颜色也调轻
  const tricks = p.techniques.map((x) => `<span class="tag trick">${esc(x)}</span>`).join('');
  const f = famOf(p);
  return `<div class="row${todo}" data-id="${p.id}">
    <span class="dot ${diff}" title="${diff}"></span>
    <span class="fam ${famCls(f)}" data-id="${p.id}" title="点击改熟练度 (当前: ${esc(famInfo(f).label)})">${famInfo(f).short}</span>
    <span class="row-id">#${p.id}</span>
    <span class="row-title">${esc(p.title)}</span>
    <span class="row-para">${paras || '<span class="tag-none" title="还没标范式">—</span>'}</span>
    <span class="row-trick">${tricks}</span>
  </div>`;
}

function wireCards() {
  document.querySelectorAll('.row').forEach((el) =>
    el.addEventListener('click', () => openDetail(+el.dataset.id))
  );
  document.querySelectorAll('.row .fam').forEach((el) =>
    el.addEventListener('click', (e) => {
      e.stopPropagation();          // 别让点击冒泡去开详情页
      openFamMenu(el);
    })
  );
  document.querySelectorAll('.group-label.openable').forEach((el) =>
    el.addEventListener('click', () => openDoc(GROUP_BY, el.dataset.struct))
  );
}

// ---- 总览里就地改熟练度 ----
function closeFamMenu() {
  const m = document.querySelector('.fam-menu');
  if (m) m.remove();
}

function openFamMenu(badge) {
  const open = document.querySelector('.fam-menu');
  closeFamMenu();
  if (open && +open.dataset.id === +badge.dataset.id) return;   // 再点一次 = 关掉

  const id = +badge.dataset.id;
  const cur = famOf(PROBLEMS.find((x) => x.id === id) || {});
  const menu = document.createElement('div');
  menu.className = 'fam-menu';
  menu.dataset.id = id;
  menu.innerHTML = FAM_LEVELS
    .map((f) => `<button class="fam-opt${f === cur ? ' on' : ''}" data-f="${famKey(f)}">
        <span class="fam ${famCls(f)}">${famInfo(f).short}</span>${esc(famInfo(f).label)}</button>`)
    .join('');
  document.body.appendChild(menu);

  const r = badge.getBoundingClientRect();
  menu.style.left = `${Math.min(r.left, innerWidth - menu.offsetWidth - 10)}px`;
  menu.style.top = `${r.bottom + 4 + menu.offsetHeight > innerHeight
    ? r.top - menu.offsetHeight - 4 : r.bottom + 4}px`;   // 贴着窗口下沿时朝上开

  menu.querySelectorAll('.fam-opt').forEach((b) =>
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      setFam(id, b.dataset.f === 'none' ? null : +b.dataset.f);
    })
  );
}

async function setFam(id, f) {
  closeFamMenu();
  await putMeta(id, { familiarity: f });           // 只发这一个字段, 其它标签原样保留
  const p = PROBLEMS.find((x) => x.id === id);
  if (p) p.familiarity = f;
  buildPanel();                                    // 正在按熟练度过滤时, 改完会自动移出/移入
}

// ---- detail ----
async function openDetail(id) {
  CURRENT = await api(`/api/problems/${id}`);
  const d = CURRENT;
  $('#d-id').textContent = '#' + d.id;
  $('#d-title').textContent = d.title;
  TAGS = {
    structures: d.structures.slice(),
    paradigms: d.paradigms.slice(),
    techniques: d.techniques.slice(),
  };
  renderChips();
  $('#e-difficulty').value = d.difficulty || '';
  $('#e-status').value = d.status || 'solved';
  $('#e-familiarity').value = famOf(d) === null ? '' : String(famOf(d));
  $('#note-file').textContent = d.note_file;
  $('#note-edit').value = d.note;
  $('#note-msg').textContent = '';
  $('#meta-msg').textContent = '改动自动保存';
  exitEdit();                 // always open in rendered (preview) mode
  buildSolTabs(d);
  $('#overlay').classList.remove('hidden');
}

// ---- editable tag chips (structures / paradigms / techniques) ----
let TAGS = { structures: [], paradigms: [], techniques: [] };

// 三个字段都给 <datalist> 建议。理由各不相同但都成立:
//   trick  自由文本, 同一个手法容易写出三种说法("快慢指针"/"快慢双指针"/"龟兔");
//   结构/范式  是闭集, 就那么十几个 —— 正因为闭, 打错一个字(paradim / two-pointers)
//              就凭空多出一个只有一道题的分组, 板面上再也聚不到一起。
const SUGGEST = new Set(['structures', 'paradigms', 'techniques']);

// 建议全部来自 PROBLEMS(前端已有的数据), 不走后端。排序:
//   1. 亲缘度 —— 用过这个 trick 的题里, 和当前题共享的结构/范式最多的那个的重合个数。
//      用个数而不是布尔: array 这种标签半个库都有, 一律算"同类"等于没排序;
//      重合 2 个(比如同时 array + hash)才是真的邻居。
//   2. 其次按被用次数, 用得多的通常是已经提炼过的说法;
//   3. 最后按字典序稳定收尾。
// 已经挂在这题上的不再列出来。
function suggestFor(field) {
  const have = new Set(TAGS[field]);
  const kin = new Set([...TAGS.structures, ...TAGS.paradigms]);
  const freq = new Map(), akin = new Map();
  for (const p of PROBLEMS) {
    if (CURRENT && p.id === CURRENT.id) continue;
    const shared = [...p.structures, ...p.paradigms].filter((t) => kin.has(t)).length;
    for (const t of p[field] || []) {
      if (have.has(t)) continue;
      freq.set(t, (freq.get(t) || 0) + 1);
      akin.set(t, Math.max(akin.get(t) || 0, shared));
    }
  }
  return [...freq.keys()]
    .sort((a, b) =>
      (akin.get(b) - akin.get(a)) ||
      (freq.get(b) - freq.get(a)) ||
      a.localeCompare(b, 'zh'))
    .map((t) => ({ t, n: freq.get(t), near: akin.get(t) > 0 }));
}

function renderChips() {
  for (const field of ['structures', 'paradigms', 'techniques']) {
    const box = document.querySelector(`.chipfield[data-field="${field}"]`);
    const sug = SUGGEST.has(field) ? suggestFor(field) : null;
    box.innerHTML =
      TAGS[field].map((t, i) =>
        `<span class="ce-chip ${field}">${esc(t)}<button class="ce-x" data-i="${i}" title="删除">×</button></span>`
      ).join('') +
      // 给建议的字段换个 placeholder: <datalist> 在页面上没有任何视觉痕迹,
      // 不说一声就没人知道这个框能点开选(Safari 还要先按 ↓ 才弹)。
      `<input class="ce-input" data-field="${field}" placeholder="${sug ? '+ tag · ↓ 选已有' : '+ tag'}"` +
        `${sug ? ` list="ce-sug-${field}" title="点开或按 ↓ 从全库已有的 trick 里选，同类的排前面"` : ''}>` +
      (sug
        ? `<datalist id="ce-sug-${field}">${sug.map((s) =>
            `<option value="${esc(s.t)}" label="${s.near ? '同类 · ' : ''}${s.n} 题在用">`).join('')}</datalist>`
        : '');
  }
}

function addTag(field, raw) {
  let added = false;
  for (const t of raw.split(/[,，]/).map((s) => s.trim()).filter(Boolean)) {
    if (!TAGS[field].includes(t)) { TAGS[field].push(t); added = true; }
  }
  if (added) { renderChips(); autoSaveMeta(); }
  document.querySelector(`.ce-input[data-field="${field}"]`).focus();
}

function removeTag(field, i) {
  TAGS[field].splice(i, 1);
  renderChips(); autoSaveMeta();
}

async function autoSaveMeta() {
  const body = {
    structures: TAGS.structures, paradigms: TAGS.paradigms, techniques: TAGS.techniques,
    difficulty: $('#e-difficulty').value, status: $('#e-status').value,
    familiarity: $('#e-familiarity').value === '' ? null : +$('#e-familiarity').value,
  };
  await putMeta(CURRENT.id, body);
  $('#meta-msg').textContent = '已保存 ✓';
  await reloadKeepOpen();
}

// reload the board data without disturbing the open detail modal
async function reloadKeepOpen() {
  PROBLEMS = await api('/api/problems');
  buildPanel();
  if (VIEW === 'grid') buildGrid();   // 从坐标系点进来的, 格子和 #count/#sub 都要还回去
}

// ---- note: render-by-default, double-click to edit source ----
let EDITING = false;

function enterEdit() {
  EDITING = true;
  $('#note-preview').classList.add('hidden');
  $('#note-edit').classList.remove('hidden');
  $('#save-note').classList.remove('hidden');
  $('#note-mode').textContent = '源码编辑中';
  $('#note-edit').focus();
}

function exitEdit(save) {
  // re-render from the (possibly edited) textarea; optionally persist first
  const changed = CURRENT && $('#note-edit').value !== CURRENT.note;
  if (save && changed) saveNote();
  EDITING = false;
  $('#note-preview').innerHTML = md($('#note-edit').value);
  $('#note-edit').classList.add('hidden');
  $('#save-note').classList.add('hidden');
  $('#note-preview').classList.remove('hidden');
  $('#note-mode').textContent = '双击渲染区编辑';
}

// ---- solutions: tab 列表 + 双击编辑 + 新建 .py (和 note 同一套交互) ----
let activeSol = 0, SOL_ITEMS = [], SOL_EDITING = false;

const EMPTY_SOL = {
  name: '', readonly: true,
  content: '(还没有 .py —— 点右上角「+ 新解法」新建；题面见 dashboard/fetch_desc.py)',
};

// item 能不能编辑: 题面(html)和占位提示不行, 真实 .py 文件才行
const editableSol = (it) => !!it && it.html === undefined && !it.readonly;

function buildSolTabs(d) {
  // 题面(如果抓过)排在解法前面, 当成第 0 个 tab
  SOL_ITEMS = d.description
    ? [{ name: '📄 题目', html: d.description }, ...d.solutions]
    : d.solutions.slice();
  SOL_EDITING = false;                       // 换题时不要把上一题的编辑态带过来
  $('#sol-msg').textContent = '';
  renderSolTabs(0);
}

function renderSolTabs(select) {
  const tabs = $('#sol-tabs');
  tabs.innerHTML =
    SOL_ITEMS.map((s, i) => `<span class="tab" data-i="${i}">${esc(s.name)}</span>`).join('') +
    `<span class="tab tab-new" title="在题目文件夹里新建一个 .py">+ 新解法</span>`;
  tabs.querySelectorAll('.tab[data-i]').forEach((t) =>
    t.addEventListener('click', () => selectSol(+t.dataset.i))
  );
  tabs.querySelector('.tab-new').addEventListener('click', newSolution);
  selectSol(select);
}

function selectSol(i) {
  exitSolEdit(true);                         // 切 tab 前先把改动落盘
  activeSol = i;
  $('#sol-tabs').querySelectorAll('.tab[data-i]')
    .forEach((t) => t.classList.toggle('active', +t.dataset.i === i));
  showItem(SOL_ITEMS[i] || EMPTY_SOL);
}

function showItem(item) {
  // 题面是 HTML, 得渲染; 代码是纯文本, 走高亮器塞进 <pre>
  const desc = $('#sol-desc'), code = $('#sol-code');
  $('#sol-edit').classList.add('hidden');
  if (item.html !== undefined) {
    desc.innerHTML = item.html;
    desc.scrollTop = 0;
    desc.classList.remove('hidden');
    code.classList.add('hidden');
    $('#sol-mode').textContent = '题面只读';
    return;
  }
  code.firstChild.innerHTML = item.name.endsWith('.py')
    ? highlightPython(item.content)
    : esc(item.content);
  code.scrollTop = 0;
  code.classList.remove('hidden');
  desc.classList.add('hidden');
  $('#sol-mode').textContent = item.readonly ? '' : '双击代码区编辑';
}

function enterSolEdit() {
  const item = SOL_ITEMS[activeSol];
  if (!editableSol(item)) return;            // 题面 / 占位提示不给编辑
  SOL_EDITING = true;
  $('#sol-edit').value = item.content;
  $('#sol-code').classList.add('hidden');
  $('#sol-desc').classList.add('hidden');
  $('#sol-edit').classList.remove('hidden');
  $('#sol-save').classList.remove('hidden');
  $('#sol-mode').textContent = '源码编辑中';
  $('#sol-edit').focus();
}

function exitSolEdit(save) {
  if (!SOL_EDITING) return;
  const item = SOL_ITEMS[activeSol];
  const v = $('#sol-edit').value;
  // saveSol 会同步更新 item.content, 所以下面的 showItem 渲染的是新内容
  if (save && editableSol(item) && v !== item.content) saveSol(v);
  SOL_EDITING = false;
  $('#sol-edit').classList.add('hidden');
  $('#sol-save').classList.add('hidden');
  if (item) showItem(item);
}

async function saveSol(content) {
  const item = SOL_ITEMS[activeSol];
  if (!editableSol(item)) return;
  const isNew = !CURRENT.solutions.some((x) => x.name === item.name);
  item.content = content;                    // 先同步改本地, 渲染不用等网络
  const r = await fetch(
    `/api/problems/${CURRENT.id}/solutions/${encodeURIComponent(item.name)}`,
    { method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }) }
  );
  if (!(await r.json()).ok) { flashSol('文件名不合法 ✗'); return; }
  if (isNew) CURRENT.solutions.push({ name: item.name, content });
  else CURRENT.solutions.find((x) => x.name === item.name).content = content;
  flashSol('已保存 ✓');
}

function flashSol(msg) {
  $('#sol-msg').textContent = msg;
  setTimeout(() => ($('#sol-msg').textContent = ''), 1500);
}

// 「+ 新解法」: 在 tab 条上就地开个输入框问文件名。
// 只在内存里建 tab, 存盘要等第一次保存 —— 名字打一半跑掉不会留下空文件。
function newSolution() {
  const tabs = $('#sol-tabs'), btn = tabs.querySelector('.tab-new');
  if (tabs.querySelector('.sol-new-in')) return;
  btn.classList.add('hidden');
  const inp = document.createElement('input');
  inp.className = 'sol-new-in';
  inp.placeholder = 'sol3.py  (Enter 确认 / Esc 取消)';
  inp.spellcheck = false;
  tabs.appendChild(inp);
  inp.focus();

  let closed = false;                        // Enter 之后移除元素会再触发 blur, 挡一下
  const close = () => { if (closed) return; closed = true; inp.remove(); btn.classList.remove('hidden'); };
  inp.addEventListener('blur', close);
  inp.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Enter') return;
    e.preventDefault();
    let name = inp.value.trim();
    if (!name) { close(); return; }
    if (!name.endsWith('.py')) name += '.py';
    close();
    // 和 server 的 SOL_NAME_RE 对齐: 挡在前面, 免得建完 tab 才发现存不上
    if (/[\/\\]/.test(name) || name === '.py') { flashSol('文件名不合法 ✗'); return; }
    const hit = SOL_ITEMS.findIndex((x) => x.name === name);
    if (hit >= 0) { selectSol(hit); flashSol('同名文件已存在，切过去了'); return; }
    SOL_ITEMS.push({ name, content: '' });
    renderSolTabs(SOL_ITEMS.length - 1);
    enterSolEdit();
  });
}

async function saveNote() {
  const content = $('#note-edit').value;
  await fetch(`/api/problems/${CURRENT.id}/note`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  CURRENT.note = content;
  $('#note-msg').textContent = '已保存 ✓';
  setTimeout(() => ($('#note-msg').textContent = ''), 1500);
}

function closeDetail() { $('#overlay').classList.add('hidden'); CURRENT = null; }

// ---- data-structure trick doc (render-by-default, double-click to edit) ----
let DOC = null, DOC_EDITING = false;

async function openDoc(kind, name) {
  DOC = await api(`/api/${kind}/` + encodeURIComponent(name));
  $('#doc-kind').textContent = kind === 'paradigms' ? '范式' : '结构';
  $('#doc-title').textContent = DOC.name || name;
  $('#doc-file').textContent = DOC.file || `${kind}/${name}.md`;
  $('#doc-edit').value = DOC.content || '';
  $('#doc-msg').textContent = '改动自动保存';
  exitDocEdit();
  $('#doc-overlay').classList.remove('hidden');
}

function enterDocEdit() {
  DOC_EDITING = true;
  $('#doc-preview').classList.add('hidden');
  $('#doc-edit').classList.remove('hidden');
  $('#doc-save').classList.remove('hidden');
  $('#doc-mode').textContent = '源码编辑中';
  $('#doc-edit').focus();
}

function exitDocEdit(save) {
  const changed = DOC && $('#doc-edit').value !== DOC.content;
  if (save && changed) saveDoc();
  DOC_EDITING = false;
  const v = $('#doc-edit').value;
  $('#doc-preview').innerHTML = v.trim() ? md(v)
    : `<p style="color:var(--dim)">（还没有内容 — 双击这里开始写 ${esc(DOC ? DOC.name : '')} 的通用 trick）</p>`;
  $('#doc-edit').classList.add('hidden');
  $('#doc-save').classList.add('hidden');
  $('#doc-preview').classList.remove('hidden');
  $('#doc-mode').textContent = '双击渲染区编辑';
}

async function saveDoc() {
  const content = $('#doc-edit').value;
  await fetch(`/api/${DOC.kind}/` + encodeURIComponent(DOC.name), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  DOC.content = content;
  $('#doc-msg').textContent = '已保存 ✓';
  setTimeout(() => { if ($('#doc-msg')) $('#doc-msg').textContent = '改动自动保存'; }, 1500);
}

function closeDoc() { $('#doc-overlay').classList.add('hidden'); DOC = null; }

// ---- cross-cutting notes: notes/*.md + 随想速记 ----
let NOTE = null, NOTE_EDITING = false;

async function openNotes(file) {
  const list = await api('/api/notes');
  $('#notes-list').innerHTML = list.length
    ? list.map((n) => `<div class="note-item" data-file="${esc(n.file)}">
         <span class="ni-file">${esc(n.file)}</span>
         <span class="ni-head">${esc(n.head || '(空)')}</span></div>`).join('')
    : '<p class="hint" style="padding:8px">还没有笔记 — 点下面新建，或在上面记条随想</p>';
  document.querySelectorAll('.note-item').forEach((el) =>
    el.addEventListener('click', () => loadNote(el.dataset.file))
  );
  $('#notes-overlay').classList.remove('hidden');
  const target = file || (list[0] && list[0].file);
  if (target) loadNote(target); else clearNotePane();
}

function markActive(file) {
  document.querySelectorAll('.note-item').forEach((el) =>
    el.classList.toggle('active', el.dataset.file === file));
}

async function loadNote(file) {
  NOTE = await api('/api/notes/' + encodeURIComponent(file));
  $('#nt-file').textContent = 'notes/' + NOTE.file;
  $('#nt-edit').value = NOTE.content;
  $('#nt-msg').textContent = '';
  markActive(NOTE.file);
  exitNoteEdit();
}

function clearNotePane() {
  NOTE = null;
  $('#nt-file').textContent = '';
  $('#nt-edit').value = '';
  $('#nt-preview').innerHTML = '';
}

function enterNoteEdit() {
  if (!NOTE) return;
  NOTE_EDITING = true;
  $('#nt-preview').classList.add('hidden');
  $('#nt-edit').classList.remove('hidden');
  $('#nt-save').classList.remove('hidden');
  $('#nt-mode').textContent = '源码编辑中';
  $('#nt-edit').focus();
}

function exitNoteEdit(save) {
  const changed = NOTE && $('#nt-edit').value !== NOTE.content;
  if (save && changed) saveNoteFile();
  NOTE_EDITING = false;
  const v = $('#nt-edit').value;
  $('#nt-preview').innerHTML = v.trim() ? md(v)
    : '<p style="color:var(--dim)">（空笔记 — 双击这里开始写）</p>';
  $('#nt-edit').classList.add('hidden');
  $('#nt-save').classList.add('hidden');
  $('#nt-preview').classList.remove('hidden');
  $('#nt-mode').textContent = '双击渲染区编辑';
}

async function saveNoteFile() {
  if (!NOTE) return;
  const content = $('#nt-edit').value;
  const r = await fetch('/api/notes/' + encodeURIComponent(NOTE.file), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  }).then((x) => x.json());
  if (!r.ok) { $('#nt-msg').textContent = '文件名不合法'; return; }
  NOTE.content = content;
  $('#nt-msg').textContent = '已保存 ✓';
  setTimeout(() => ($('#nt-msg').textContent = ''), 1500);
}

async function newNote() {
  let name = (prompt('新笔记文件名（.md 可省略）', '') || '').trim();
  if (!name) return;
  if (!name.endsWith('.md')) name += '.md';
  const r = await fetch('/api/notes/' + encodeURIComponent(name), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: `# ${name.replace(/\.md$/, '')}\n\n` }),
  }).then((x) => x.json());
  if (!r.ok) { alert('文件名不合法（只允许中英文、数字、- . 空格，且以 .md 结尾）'); return; }
  openNotes(name);
}

async function addScratch() {
  const inp = $('#scratch-in');
  const text = inp.value.trim();
  if (!text) return;
  const r = await fetch('/api/scratch', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  }).then((x) => x.json());
  if (!r.ok) return;
  inp.value = '';
  $('#scratch-msg').textContent = '已记 ✓';
  setTimeout(() => ($('#scratch-msg').textContent = ''), 1500);
  openNotes(r.file);                 // 刷新列表并跳到 scratch.md
}

function closeNotes() { $('#notes-overlay').classList.add('hidden'); NOTE = null; }

// ---- python syntax highlighter (tokenizer, no external deps) ----
const PY_KW = new Set(['False','None','True','and','as','assert','async','await','break',
  'class','continue','def','del','elif','else','except','finally','for','from','global',
  'if','import','in','is','lambda','nonlocal','not','or','pass','raise','return','try',
  'while','with','yield','match','case']);
const PY_BUILTIN = new Set(['print','len','range','int','str','float','list','dict','set',
  'tuple','bool','sorted','sum','min','max','abs','enumerate','zip','map','filter','open',
  'input','type','isinstance','super','object','Exception','self','cls','None','True','False']);

function highlightPython(src) {
  let i = 0, n = src.length, out = '', prevWord = '';
  const push = (cls, txt) => (out += cls ? `<span class="t-${cls}">${esc(txt)}</span>` : esc(txt));
  while (i < n) {
    const c = src[i];
    if (c === '#') {                                   // comment
      let j = i; while (j < n && src[j] !== '\n') j++;
      push('com', src.slice(i, j)); i = j; continue;
    }
    if ((c === '"' || c === "'") && src.substr(i, 3) === c + c + c) {  // triple string
      const q = c + c + c; let j = i + 3;
      while (j < n && src.substr(j, 3) !== q) j++;
      j = Math.min(n, j + 3); push('str', src.slice(i, j)); i = j; continue;
    }
    if (c === '"' || c === "'") {                      // single/double string
      let j = i + 1; while (j < n && src[j] !== c) { if (src[j] === '\\') j++; j++; }
      j = Math.min(n, j + 1); push('str', src.slice(i, j)); i = j; continue;
    }
    if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1] || ''))) {  // number
      let j = i; while (j < n && /[0-9a-fA-FxXoObB._]/.test(src[j])) j++;
      push('num', src.slice(i, j)); i = j; continue;
    }
    if (c === '@') {                                   // decorator
      let j = i + 1; while (j < n && /[A-Za-z0-9_.]/.test(src[j])) j++;
      push('dec', src.slice(i, j)); i = j; continue;
    }
    if (/[A-Za-z_]/.test(c)) {                         // identifier / keyword
      let j = i; while (j < n && /[A-Za-z0-9_]/.test(src[j])) j++;
      const w = src.slice(i, j);
      const cls = PY_KW.has(w) ? 'kw'
        : (prevWord === 'def' || prevWord === 'class') ? 'fn'
        : PY_BUILTIN.has(w) ? 'bi' : null;
      push(cls, w); prevWord = w; i = j; continue;
    }
    if (!/\s/.test(c)) prevWord = '';                  // reset on real punctuation
    push(null, c); i++;
  }
  return out;
}

// ---- 题号 -> 可点链接 ------------------------------------------------------
// 只认**显式标记**: "LC 42"、"LC42"、"#42"。一串连号共用一个标记 ——
// "LC 26, 27"、"LC 5/647"、"LC 3、76、209、424" 里每个数字都会各自去查,
// 库里没有的(76/209 这种还没做的)保持纯文本, 不生成死链。
//
// 为什么不猜裸数字: 试过一版启发式(值域/量词/左右边界一堆规则), 全库能跑对,
// 但规则不可预测 —— 写文档的时候没法一眼知道 "各 1 个标量" 的 1 会不会变成链接。
// 显式标记的代价只是多打三个字符, 换来的是渲染结果完全可预期。存量文档(structures/
// paradigms/notes 共 16 篇)的 182 处引用已经一次性迁移过, 迁移前后链接集合逐条对过。
//
// 只碰纯文本: <code> 里的 2i+1、<a href="../paradigms/1d-dp.md"> 里的路径、
// 标签属性里的数字都不能动, 所以先按「标签/代码/已有链接」切段, 只改偶数段。
const PID_SEG = /(<code[\s\S]*?<\/code>|<a\b[\s\S]*?<\/a>|<[^>]*>)/;
// 标记 + 一串用 / , 、 和 与 连起来的题号
// 末尾的否定环视: "每天 LC 1-1.5 小时" 里 LC 是网站名, 1 是时长不是题号
const PID_RUN = /(?:LC\s*|#)\d{1,4}(?:\s*(?:[\/,、]|和|与)\s*\d{1,4})*(?![\w.%\-–—])/gi;
const PID_ONE = /\d{1,4}/g;

function linkifyPids(html) {
  const rec = byId();
  if (!rec.size) return html;
  return html.split(PID_SEG).map((seg, k) => {
    if (k % 2) return seg;                       // 捕获组 = 标签/代码/已有链接, 原样放回
    return seg.replace(PID_RUN, (run) =>
      run.replace(PID_ONE, (num) => {
        const p = rec.get(+num);
        return p
          ? `<a class="pid" data-pid="${p.id}" title="${esc(p.id + '. ' + p.title)}">${num}</a>`
          : num;                                 // 还没做的题: 留字, 不留链
      }));
  }).join('');
}

// ---- markdown 渲染: marked(存在仓库里) + 两层后处理 ------------------------
// 这里以前是 60 行手写渲染器, 换掉的直接原因是**嵌套列表渲染不出来**: 它按行匹配
// `^\s*[-*+]\s+` 就把所有层级拍平进同一个 <ul>, structures/array.md 的 feature
// 那种三层缩进全塌成一层。顺带修掉的还有:
//   - 行内 `|OPT'| = |OPT|` 长得像表头但下一行不是分隔行, 老渲染器要靠一句
//     "第一行无条件吃掉" 的兜底才不死循环(见 git history, 435 的 note.md 触发过);
//   - 引用块套列表、列表里的代码块、任务列表 `- [ ]` 这些一概不认。
//
// marked 是 vendored 的(vendor/marked.min.js, MIT), 不走 CDN、不需要构建步骤 ——
// 和 vue.global.prod.js 同一条规矩, 见 README「没有构建步骤」。
const MD_OPT = { gfm: true, breaks: false };

function md(src) {
  if (typeof marked === 'undefined') {          // vendor 文件掉了也别让整页炸
    console.warn('[md] marked 没加载 —— 退化成纯文本。检查 vendor/marked.min.js');
    return `<pre>${esc(String(src))}</pre>`;
  }
  const html = marked.parse(String(src), MD_OPT);
  // 1) 文档里的链接指向仓库文件, 一律新标签打开(和老渲染器行为一致)
  // 2) 题号 -> 可点链接。放在最后, 因为它的跳过依据正是上面生成的 <code>/<a>
  return linkifyPids(html.replace(/<a href=/g, '<a target="_blank" href='));
}

// ---- 🧠 FSRS 复习: 看题面 -> 心里过思路 -> 揭晓 -> 1-4 自评 --------------------
// 调度状态在各题 meta.json 的 fsrs 字段里, 算法在 dashboard/fsrs.py。
// 和 familiarity(L1-L4) 是**两套独立的东西**: 这里只管"什么时候再问一次",
// familiarity 仍然是手工维护的掌握档位, 复习不会去改它。
//
// 这一节的 UI 是**唯一用 Vue 的地方**(模板在 index.html 的 #review-app 里),
// 其余看板还是手写 DOM。下面这些排队/调度的纯函数不属于 UI, 📈 进度那节也在用。
const isReadOnly = () => document.documentElement.classList.contains('ro');

const todayStr = () => new Date().toLocaleDateString('sv');   // 本地 YYYY-MM-DD
const isCard = (p) => !!p.due;
const isDue = (p) => isCard(p) && p.due <= todayStr();
const rvEligible = (p) => p.status === 'solved' || p.status === 'review';
const FAM_ORDER = { 4: 0, 3.5: 1, 3: 2, 2: 3, none: 4, 1.5: 5, 1: 6, 0: 7 };   // 越生的越先进队列

// 队列**范围**三种模式都一样(到期的卡 + 还没进过复习的题), 模式只决定**顺序**:
//   fsrs   到期优先 + 生的优先(默认)
//   order  题号升序
//   random 随机
const RV_MODES = ['fsrs', 'order', 'random'];

function savedMode() {
  try {
    const m = localStorage.getItem('rv-mode');
    if (RV_MODES.includes(m)) return m;
  } catch { /* 隐私模式 */ }
  return 'fsrs';
}

// ---- 两个牌组 ---------------------------------------------------------------
// problems 题目(真相在各题 meta.json) / syntax 语法卡(真相在 syntax/*.md)。
// 两边**只共用调度器和历史**, 排队规则各写各的 —— 语法卡没有 status 也没有 familiarity,
// 硬套题目那套会得到一个"全 undefined 参与排序"的随机顺序。
const DECKS = ['problems', 'syntax'];
const DECK_LABEL = { problems: '题目', syntax: '语法' };
const deckRows = (deck) => (deck === 'syntax' ? SYNTAX : PROBLEMS);

function savedDeck() {
  try {
    const d = localStorage.getItem('rv-deck');
    if (DECKS.includes(d)) return d;
  } catch { /* 隐私模式 */ }
  return 'problems';
}

// 队列范围: 到期的卡 + 还没进过复习的。题目那边"还没进过"要先够格(status 是 solved/review,
// 没想出来过的思路谈不上复习); 语法卡只要写在 syntax/*.md 里就算数, 没有这一层。
function queuePool(deck = 'problems') {
  const rows = deckRows(deck);
  const fresh = deck === 'syntax' ? rows : rows.filter(rvEligible);
  return [...rows.filter(isDue), ...fresh.filter((p) => !isCard(p))];
}

function orderQueue(pool, mode = 'fsrs', deck = 'problems') {
  // 组内的稳定兜底顺序。题目按题号; 语法卡按 ord(= /api/syntax 的下标, 也就是
  // 文件名 -> 文件内的书写顺序)。**别拿 a.id - b.id 排语法卡** —— id 是字符串,
  // 相减得 NaN, 比较器全返回 NaN 等于没排序, 表现是顺序每次都不一样。
  const tie = deck === 'syntax'
    ? (a, b) => (a.ord || 0) - (b.ord || 0)
    : (a, b) => a.id - b.id;
  if (mode === 'random') return shuffle(pool.map((p) => p.id));
  if (mode === 'order') return [...pool].sort(tie).map((p) => p.id);
  const due = pool.filter(isDue).sort((a, b) =>
    (a.status === 'review' ? 0 : 1) - (b.status === 'review' ? 0 : 1) ||
    a.due.localeCompare(b.due) || tie(a, b));
  // 还没成为卡片的题, 按熟练度从生到熟排 —— 只是**读** familiarity 定顺序, 不写它。
  // 语法卡没有这个字段, 就按书写顺序来(同一个文件里相关的卡挨着问, 正好对照)。
  const fresh = pool.filter((p) => !isCard(p)).sort(deck === 'syntax' ? tie
    : (a, b) => FAM_ORDER[famKey(famOf(a))] - FAM_ORDER[famKey(famOf(b))] || tie(a, b));
  return [...due, ...fresh].map((p) => p.id);
}

// 三种模式的**范围完全一样**, 所以徽章和 📈 里的数字跟模式无关
const buildQueue = (mode = 'fsrs', deck = 'problems') => orderQueue(queuePool(deck), mode, deck);
const deckDue = (deck) => queuePool(deck).length;

function updateReviewBadge() {
  const n = { problems: deckDue('problems'), syntax: deckDue('syntax') };
  const total = n.problems + n.syntax;
  $('#review-n').textContent = total;
  $('#review-n').classList.toggle('hidden', !total);
  const btn = $('#open-review');
  if (btn) btn.title = `题目 ${n.problems} 道 · 语法 ${n.syntax} 张`;
  return n;
}

function fmtInterval(days) {
  if (days <= 0) return '今天';
  if (days === 1) return '明天';
  if (days < 30) return `${days} 天`;
  if (days < 365) return `${(days / 30).toFixed(1)} 个月`;
  return `${(days / 365).toFixed(1)} 年`;
}

const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const cxText = (c) => (c && c.time ? `${c.time} / ${c.space || '?'}` : '');

// 复杂度的干扰项从全库出现过的复杂度里抽, 并且**优先抽常见的** ——
// 抽到 O(n^(T/min)) 那种独一份的等于送分, 抽到 O(n)/O(n) 才是真的容易混。
function cxPool(correct) {
  const freq = new Map();
  for (const p of PROBLEMS) {
    const t = cxText(p.complexity);
    if (t && t !== correct) freq.set(t, (freq.get(t) || 0) + 1);
  }
  return [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map((x) => x[0]);
}

// 复杂度那道先关掉: 思路还没稳的时候先问思路, 复杂度等思路熟了再开。
// 改成 true 就能把「时间/空间复杂度？」那道题恢复出来, 其余逻辑都还在。
const QUIZ_CX = false;

function buildQuiz(d) {
  const q = d.quiz || {};
  const cx = cxText(d.complexity);
  const mk = (correct, wrongs) => {
    if (!correct || wrongs.length < 1) return null;
    const opts = shuffle([correct, ...wrongs.slice(0, 3)]);
    return { opts, correct: opts.indexOf(correct), pick: -1 };
  };
  return {
    idea: q.idea ? mk(q.idea, q.wrong || []) : null,
    cx: QUIZ_CX && cx ? mk(cx, shuffle(cxPool(cx)).slice(0, 3)) : null,
  };
}

// ---- 复习面板(Vue)。模板是 index.html 里的 #review-app -----------------------
// 迁移到 Vue 的理由: 这一屏状态最多(队列 / 揭晓与否 / 选择题 / 就地编辑 / tab),
// 以前全靠手工 classList.toggle + innerHTML 对齐, 加一个元素就容易漏一处。
// 现在 DOM 一律从下面这些 data/computed 推导出来, app.js 里不再有 $('#rv-*')。
const RV = Vue.createApp({
  data() {
    return {
      open: false,
      queue: [], done: 0, total: 0,
      d: null,                       // 当前这道的详情; null = 队列空了(显示收尾屏)
      loading: false,                // 拉详情中。不加这个会先闪一下"没有到期的题"
      revealed: false,
      quiz: { idea: null, cx: null },
      items: [], active: 0,          // 揭晓后的 note / 各解法 tab
      editing: false, draft: '', amsg: '',
      note: '',                      // 顶部那行临时提示(写失败 / 已经是队尾)
      busy: false,                   // 评分->取下一题这一整段在飞。见 rate() 上面那段注释
      failMsg: '',                   // 拉下一题失败时的收尾屏文案(替掉"复习完了")
      deferred: [],                  // 这一轮按过「押到队尾」的题, 按发生顺序, 可重复
      mode: savedMode(),
      deck: savedDeck(),             // 'problems' | 'syntax'
      counts: { problems: 0, syntax: 0 },   // 标在牌组按钮上的到期数
      readOnly: isReadOnly(),
      MODES: [{ k: 'fsrs', label: '到期优先' }, { k: 'order', label: '顺序' }, { k: 'random', label: '随机' }],
      DECKS: [{ k: 'problems', label: '题目' }, { k: 'syntax', label: '语法' }],
      KEYS: 'ABCD',
      RATE: { 1: ['忘了', '想不起来'], 2: ['勉强', '想了很久'], 3: ['想起来了', '正常'], 4: ['很熟', '秒答'] },
    };
  },

  computed: {
    isSyntax() { return this.deck === 'syntax'; },
    // 左上角那个胶囊: 题目是题号, 语法卡是主题(= 文件名), 都是"这是哪一类"的定位信息
    pillText() { return this.d ? (this.isSyntax ? this.d.topic : this.d.id) : ''; },
    metaLine() {
      if (!this.d) return '';
      const reps = this.d.fsrs && this.d.fsrs.reps ? `第 ${this.d.fsrs.reps + 1} 次复习` : '第一次进复习';
      return `${this.isSyntax ? this.d.file : (this.d.difficulty || '?')} · ${reps}`;
    },
    // v-html: 两句提示里都有加粗。内容是写死的常量, 没有外部输入
    askText() {
      return this.isSyntax
        ? '先<b>在心里把答案说出来</b>, 再揭晓 —— 说不出口就是不会, 别停在"感觉知道"。'
        : '先在心里说清三件事 —— <b>用什么结构 · 什么范式 · 触发条件是什么</b>。不写代码。';
    },
    // 只渲染题面 / 卡片正面。绝不碰 d.note / d.solutions / d.back —— 剧透了这个功能就没意义了
    descHtml() {
      if (!this.d) return '';
      if (this.isSyntax) {
        // 正面可以是空的: 那种卡的问题**就是标题**(「想判断字符是字母或数字, 用哪个方法」),
        // 标题已经在上面大字显示了, 这里不用再补一句废话
        return this.d.front ? md(this.d.front) : '';
      }
      return this.d.description
        || '<p class="hint">这题没有抓到题面(problem.html 是空的)。只能靠标题回忆 —— 或者跑 dashboard/fetch_desc.py 补抓。</p>';
    },
    // 拉详情的空档不能显示收尾屏 —— 会闪一下"今天没有到期的题"
    showEmpty() { return !this.d && !this.loading; },
    // 选择题只有题目牌组有 —— 它测的是"该用哪个模板"的辨别力, 语法卡没有这个维度
    hasQuiz() { return !this.isSyntax && !!(this.quiz.idea || this.quiz.cx); },
    quizBlocks() {
      const b = [{ key: 'idea', label: '思路是哪个？', state: this.quiz.idea }];
      if (this.quiz.cx) b.push({ key: 'cx', label: '时间 / 空间复杂度？', state: this.quiz.cx });
      return b;                                    // cx 关掉时整块不占位
    },
    verdict() {
      if (!this.revealed) return { cls: '', text: '' };
      const v = (st) => (!st || st.pick < 0 ? '' : st.pick === st.correct ? 'ok' : 'no');
      const vs = [v(this.quiz.idea), v(this.quiz.cx)].filter(Boolean);
      if (!vs.length) return { cls: '', text: '' };
      const allOk = vs.every((x) => x === 'ok');
      return {
        cls: allOk ? 'ok' : 'no',
        text: allOk ? '选择题全对' : `选择题错了 ${vs.filter((x) => x === 'no').length} 项`,
      };
    },
    // 标签就是答案的一部分 —— 「用什么结构 / 什么范式」正是揭晓时该对照的东西
    tagline() {
      const tag = (label, arr) => (arr && arr.length ? `${label} <b>${esc(arr.join(' · '))}</b>` : '');
      return [tag('结构', this.d.structures), tag('范式', this.d.paradigms)].filter(Boolean).join('　　')
        || '<span class="rv-none">(还没打标签)</span>';
    },
    cxLine() {
      const cx = (this.d && this.d.complexity) || {};
      return [cx.time, cx.space].filter(Boolean).join('  /  ');
    },
    ideaHtml() {
      if (this.isSyntax) {
        return this.d.back
          ? md(this.d.back)
          : '<span class="rv-none">这张卡还没写背面 —— 点右边「改一下」补上</span>';
      }
      return this.d.answer
        ? md(this.d.answer)
        : '<span class="rv-none">还没写答案卡 —— 点右边「改一下」把刚才想的那套写进去</span>';
    },
    bodyHtml() {
      const item = this.items[this.active];
      if (!item) return '';
      return item.code !== undefined ? `<pre><code>${highlightPython(item.code)}</code></pre>` : md(item.md);
    },
    preview() { return (this.d && this.d.fsrs_preview) || {}; },
    emptyMsg() {
      if (this.failMsg) return this.failMsg;
      const unit = this.isSyntax ? '张' : '道';
      const other = this.isSyntax ? 'problems' : 'syntax';
      const rest = this.counts[other]
        ? `<br><span class="hint">另一组「${DECK_LABEL[other]}」还有 ${this.counts[other]} ${other === 'syntax' ? '张' : '道'}到期 —— 点上面切过去</span>`
        : '';
      if (this.done) {
        return `这一轮复习完了 —— 共 ${this.done} ${unit} 🎉`
          + `<br><span class="hint">下次到期时间已经按 FSRS 排好, 徽章上的数字会自己变</span>${rest}`;
      }
      return (this.isSyntax
        ? '今天没有到期的语法卡 🎉<br><span class="hint">卡片写在 syntax/*.md 里, 一个 ## 一张 —— 加一张就会进队列</span>'
        : '今天没有到期的题 🎉<br><span class="hint">status 是 solved / review 的题才会进复习队列</span>') + rest;
    },
  },

  methods: {
    fmtInterval,                                   // 模板里要用

    // 把当前队列快照发给后端存成 dashboard/session.json。**单向**: 只写不读,
    // 前端从不拿它做决定 —— 队列仍然是每次开面板现算的。存它只是为了在浏览器外面
    // 也能看见"现在队列长什么样 / 哪几道被押到队尾了"。失败了不影响复习。
    syncSession() {
      if (this.readOnly) return;                   // 只读站没有写接口
      api('/api/review/session', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          open: this.open, deck: this.deck, mode: this.mode, done: this.done, total: this.total,
          current: this.d ? this.d.id : null, queue: this.queue, deferred: this.deferred,
        }),
      }).catch(() => { /* 存不上就算了, 这不是数据源 */ });
    },

    start() {
      this.counts = updateReviewBadge();
      this.queue = buildQueue(this.mode, this.deck);
      this.done = 0;
      this.total = this.queue.length;
      this.deferred = [];
      this.open = true;
      this.next();
    },

    // 换牌组 = **重开一轮**, 不是重排队列: 两组的 id 空间都不一样(整数 vs 字符串),
    // 混在一个 queue 里 next() 会拿着题号去语法卡里找。所以 done/total 一起清零。
    setDeck(k) {
      if (!DECKS.includes(k) || k === this.deck) return;
      this.deck = k;
      try { localStorage.setItem('rv-deck', k); } catch { /* 隐私模式 */ }
      this.start();
    },
    close() {
      this.open = false;
      this.d = null;
      this.editing = false;
      this.syncSession();
    },
    toStats() { this.close(); openStats(); },

    // 拉详情要是失败, 绝不能让 this.d / revealed 停在**上一道**题上 —— 那样卡面纹丝不动,
    // 看着像前端卡死, 而 1-4 还照样响应, 于是每按一次就给上一道重复记一次复习。
    // (真发生过: reviews.jsonl 里 #1 在 4 秒内被记了 6 次, #206 记了 4 次, stability
    //  一路 8→60 天。) 所以: 先落下 revealed, 失败就把题号放回队头 + 走收尾屏说明白。
    async next() {
      this.note = '';
      this.failMsg = '';
      this.editing = false;
      this.amsg = '';
      this.revealed = false;                             // 先落下答案, 再去拉
      const id = this.queue.shift();
      if (id === undefined) { this.d = null; return; }   // 队列空了 -> 收尾屏
      // 语法卡整组在 /api/syntax 里一次拉完(几十张而已), 不需要逐张再请求一次 ——
      // 所以这条路没有"拉详情失败"这种状态, 直接从内存里取。
      let d = null;
      if (this.isSyntax) {
        d = SYNTAX.find((c) => c.id === id) || null;
      } else {
        this.loading = true;
        try {
          d = await api(`/api/problems/${id}`);
        } catch (e) {
          console.error('[review] 拉题详情失败', id, e);
        } finally {
          this.loading = false;
        }
      }
      if (!d || d.id === undefined) {                    // 没拿到: id 放回队头, 不丢
        this.queue.unshift(id);
        this.d = null;
        this.failMsg = this.isSyntax
          ? `⚠ 队列里的「${esc(String(id))}」在 syntax/*.md 里找不到了<br>`
            + `<span class="hint">多半是刚改了卡标题(改标题 = 换 id)。关掉重开就好</span>`
          : `⚠ 拉 #${id} 的详情失败(服务没起? 看 console)<br>`
            + `<span class="hint">这道题还在队列里 —— 关掉重开就接着问它</span>`;
        this.syncSession();
        return;
      }
      this.d = d;
      this.quiz = buildQuiz(this.isSyntax ? {} : this.d);
      this.active = 0;
      this.$nextTick(() => { if (this.$refs.card) this.$refs.card.scrollTop = 0; });
      this.syncSession();
    },
    // 只读站用: 没有评分按钮, 空格 = 下一题。busy 同 rate() —— 连按两下空格
    // 会在上一道还没拉回来的时候再 shift 一个题号, 那道就被静默跳过了。
    async skip() {
      if (this.busy) return;
      this.busy = true;
      this.done++;
      try { await this.next(); } finally { this.busy = false; }
    },

    // 换模式: 只重排**剩下**的题, 当前这道不动, done/total 也不重来
    setMode(m) {
      if (!RV_MODES.includes(m)) return;
      this.mode = m;
      try { localStorage.setItem('rv-mode', m); } catch { /* 隐私模式 */ }
      const byId = new Map(deckRows(this.deck).map((p) => [p.id, p]));
      this.queue = orderQueue(this.queue.map((id) => byId.get(id)).filter(Boolean), m, this.deck);
      this.syncSession();
    },

    pick(state, i) {
      if (this.revealed) return;                       // 揭晓后不能再改答案
      state.pick = state.pick === i ? -1 : i;          // 再点一下取消
    },
    optClass(state, i) {
      if (!this.revealed) return { picked: state.pick === i };
      return { done: true, right: i === state.correct, wrong: i !== state.correct && i === state.pick };
    },

    reveal() {
      if (!this.d || this.revealed || this.busy) return;
      this.revealed = true;
      // 语法卡的背面就是全部, 没有次要 tab —— items 留空, 模板里那一块整个不占位
      this.items = this.isSyntax ? []
        : [{ name: '📝 笔记', md: this.d.note || '_(还没写笔记)_' },
           ...this.d.solutions.map((x) => ({ name: x.name, code: x.content }))];
      this.active = 0;
    },

    // 就地改答案卡: 复习时脑子正热, 这时候压缩成一句话最准
    startEdit() {
      if (!this.revealed || this.readOnly) return;
      this.draft = (this.isSyntax ? this.d.back : this.d.answer) || '';
      this.editing = true;
      this.$nextTick(() => this.$refs.aedit && this.$refs.aedit.focus());
    },
    cancelEdit() { this.editing = false; },
    async saveAnswer() {
      if (!this.editing) return;
      const content = this.draft;
      // 语法卡的背面存回 syntax/<主题>.md 的对应行区间(见 syntax.save_back), 题目的存 answer.md
      const req = this.isSyntax
        ? ['/api/syntax/card', { id: this.d.id, content }]
        : [`/api/problems/${this.d.id}/answer`, { content }];
      let r;
      try {
        r = await api(req[0], {
          method: 'PUT', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(req[1]),
        });
      } catch { r = null; }
      if (!r || !r.ok) { this.amsg = '没存上(只读站?)'; return; }
      if (this.isSyntax) this.d.back = content; else this.d.answer = content;
      this.editing = false;
      this.amsg = '已存 ✓';
      setTimeout(() => { this.amsg = ''; }, 1500);
    },

    // 押到队尾: 不评分 / 不写 FSRS / 不算进度, 只把这道题挪到本次会话的最后再问一遍。
    // 和评 1 的区别 —— 评 1 是**真的记一次复习**(写 reviews.jsonl, due 会变);
    // 这里表达的是"现在没空细看", 不该污染调度数据。
    defer() {
      if (!this.d || this.busy) return;
      if (!this.queue.length) {                        // 后面没题了, 挪了还是它
        this.note = '⚠ 已经是本轮最后一道了 —— 队尾就在这儿';
        return;
      }
      this.queue.push(this.d.id);                      // done/total 都不动: 这道题还欠着
      this.deferred.push(this.d.id);
      this.next();                                     // next() 里会同步给后端
    },

    // busy 是**去重闸**, 不是转圈动画: 一次评分要走 POST -> 刷看板 -> 再 GET 下一题,
    // 这中间卡面还停在当前这道且 revealed=true, 手快按第二下就会给同一道题再记一次复习。
    // 服务端每条都照单全收(reviews.jsonl 里 #1 连记 6 次那次就是这么来的), 只能前端拦。
    async rate(r) {
      if (!this.revealed || this.busy) return;
      const id = this.d.id;
      this.busy = true;
      // 语法卡的 id 是 "主题/标题"(带中文和空格), 塞不进 URL 路径, 所以走 body
      const req = this.isSyntax
        ? ['/api/syntax/review', { id, rating: r }]
        : [`/api/review/${id}`, { rating: r }];
      let res;
      try {
        res = await api(req[0], {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(req[1]),
        });
      } catch { res = null; }
      if (!res || !res.ok) {
        this.busy = false;
        // 只读站的 403 也走这里(static-shim 是 resolve 不是 reject)。写失败就**不推进**——
        // 假装评过了会让这道题的调度悄悄丢一次, 比停下来更糟。
        this.note = '⚠ 没记录下来(只读站或服务没起) —— 按「下一题」继续自测';
        return;
      }
      // 就地更新内存里那一行, 免得为了一个 due 重拉整组。两个牌组的行是同形状的
      // (语法卡的调度字段在 /api/syntax 里就摊平到顶层了), 所以这段不用分叉。
      const p = deckRows(this.deck).find((x) => x.id === id);
      if (p) {
        p.due = res.card.due; p.reps = res.card.reps; p.stability = res.card.stability;
        p.last_review = res.card.last_review; p.fsrs_state = res.card.state;
        p.fsrs = res.card; p.fsrs_preview = res.preview;
      }
      if (r === 1) { this.queue.push(id); this.total++; }   // 忘了 -> 本次会话末尾再问一遍
      REVIEWS = null;        // 历史多了一行, 让 📈 进度下次打开重新拉
      this.done++;
      // 看板重绘是**旁支**: 它抛了顶多是背后那屏没刷新, 不能连累复习推进 ——
      // 以前这两行在 this.next() 前面裸调, 一抛就停在当前这道题上, 表现同上。
      try {
        buildPanel();
        this.counts = updateReviewBadge();
      } catch (e) { console.error('[review] 刷新看板失败', e); }
      try { await this.next(); } finally { this.busy = false; }
    },

    // 键盘由 app.js 末尾那个全局 handler 转进来 —— 保持和其它 overlay 同一套分发顺序
    onKey(e) {
      if (this.editing && (e.ctrlKey || e.metaKey) && e.key === 's') { this.saveAnswer(); return true; }
      if (e.ctrlKey || e.metaKey || e.altKey || e.isComposing || e.keyCode === 229) return false;
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return false;
      if (e.key === ' ') {
        if (!this.revealed) this.reveal();
        else if (this.readOnly) this.skip();     // 只读站没有评分按钮, 空格 = 下一题
        // 本地站揭晓后不响应空格: 必须按 1-4, 防止手滑跳过一道没评分
        return true;
      }
      if (e.key === '0') { this.defer(); return true; }
      if (this.revealed && !this.readOnly && '1234'.includes(e.key)) { this.rate(+e.key); return true; }
      return false;
    },
    onEsc() {
      if (this.editing) this.cancelEdit();
      else this.close();
    },
  },
}).mount('#review-app');

// ---- 📈 复习进度: 到期预测 / 记忆强度 / 复习历史 -----------------------------
// 每个数字都从 /api/problems 的 fsrs 列 + /api/reviews(reviews.jsonl) **现算**,
// 不落第二份统计 —— 手改了某题的 meta.json 或者删掉 data.db 重建, 这里跟着变, 不会对不上。
let REVIEWS = null;                 // reviews.jsonl 的全部行; null = 还没拉过
let EDITS = null;                   // edits.jsonl 的全部行(标签/熟练度改动); null = 还没拉过

const RATE_LABEL = { 1: '忘了', 2: '勉强', 3: '想起来了', 4: '很熟' };
const FORECAST_DAYS = 30;           // 到期预测往前看多远
const HISTORY_DAYS = 30;            // 复习历史往回看多久

// 全部按**本地日期**算, 和 todayStr() / server.py 的 today_str() 是同一套口径
const dParse = (s) => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
const dAdd = (s, n) => { const t = dParse(s); t.setDate(t.getDate() + n); return t.toLocaleDateString('sv'); };
const mmdd = (s) => s.slice(5).replace('-', '/');

// stability(天)的分桶: [上界(不含), 标签]。最后一档兜底。
const SBUCKETS = [[1, '<1天'], [3, '1-3天'], [7, '3-7天'], [14, '1-2周'],
                  [30, '2-4周'], [90, '1-3月'], [180, '3-6月'], [Infinity, '>6月']];
const sBucket = (d) => SBUCKETS.findIndex(([hi]) => d < hi);

// 记忆强度和间隔都用它 —— fmtInterval 是给"下次什么时候"用的, 0 会说成"今天", 这里不合适
function fmtDays(d) {
  if (!d || d <= 0) return '—';
  if (d < 1) return '<1 天';
  if (d < 30) return `${d.toFixed(d < 10 ? 1 : 0)} 天`;
  if (d < 365) return `${(d / 30).toFixed(1)} 个月`;
  return `${(d / 365).toFixed(1)} 年`;
}

// 柱状图。cols: [{label, tip, on, n, parts:[{cls,n}]}]; 高度按全图最大值归一, 堆叠从下往上。
// 柱子顶上默认写这一列的合计; 给了 c.n 就写它 —— 时间轴那张图每列合计都是全库题数,
// 印一排一模一样的数字没有信息量。
function chartHTML(cols, h = 96) {
  const max = Math.max(1, ...cols.map((c) => c.parts.reduce((s, p) => s + p.n, 0)));
  const body = cols.map((c) => {
    const tot = c.parts.reduce((s, p) => s + p.n, 0);
    const bars = c.parts.filter((p) => p.n > 0)
      .map((p) => `<i class="${p.cls}" style="height:${(100 * p.n / max).toFixed(2)}%"></i>`).join('');
    return `<div class="col${c.on ? ' on' : ''}" title="${esc(c.tip)}">
        <div class="col-n">${esc(c.n !== undefined ? c.n : (tot || ''))}</div>
        <div class="col-bars">${bars}</div>
        <div class="col-x">${esc(c.label || '')}</div>
      </div>`;
  }).join('');
  return `<div class="chart" style="--ch:${h}px">${body}</div>`;
}

const stile = (v, label, sub) =>
  `<div class="stile"><b>${esc(v)}</b><span>${esc(label)}</span>${sub ? `<em>${esc(sub)}</em>` : ''}</div>`;

const sblock = (title, hint, body) => `<section class="sblock">
    <div class="sblock-head"><b>${esc(title)}</b>${hint ? `<span class="hint">${esc(hint)}</span>` : ''}</div>
    ${body}</section>`;

const slegend = (items) => `<div class="slegend">${items
  .map(([cls, label, n]) => `<span class="skey"><i class="${cls}"></i>${esc(label)}${
    n === undefined ? '' : ` <b>${n}</b>`}</span>`).join('')}</div>`;

// ---- 掌握度时间轴: 每天各档各有几道题 ----------------------------------------
// 和这一页其它数字一样**不落第二份统计**。最右边那一列直接来自 /api/problems, 是真相;
// 往左靠 edits.jsonl 里每条改动的 from 值一步步倒推, 再正推回来逐日取快照。
// 好处是"今天"永远和看板对得上 —— 日志漏记的手改(直接编辑 meta.json)只会让更早的
// 那几天偏一点, 不会让整条线整体漂掉。
//
// 分母是**题单 ∪ 仓库**: 没建文件夹的题也得占一格, 否则"未做"这一层就画不出来,
// 曲线会变成"总量凭空长大", 而不是"未做在被吃掉"。
const TL_MAX_DAYS = 120;      // 一列一天, 再长就挤不下了, 只画最近这些天
const TL_GONE = 'gone';       // 还没建文件夹 = 未做
let TL_MODE = 'L';            // 'L' 按熟练度档(原始的 L) | 'S' 按深度级(算出来的 S)

// 每档 [key, cls, label]。数组顺序 = 堆叠顺序, 第一项在**最底下**(见 .col-bars 的 column-reverse)。
const TL_ROWS = {
  L: FAM_LEVELS.map((f) => [famKey(f), famCls(f), f === null ? '未评' : FAM[f].short])
      .concat([[TL_GONE, 'fgone', '未做']]),
  // 「还没到 S1」用灰(和 L 那边的"未评"同色), 不用坐标系里的 .s0 —— .s0 是 --chip,
  // 和下面"未做"那一段一个颜色, 堆在一起就分不出来了
  S: [['3', 's3', 'S3 讲得清'], ['2', 's2', 'S2 写得对'], ['1', 's1', 'S1 思路清楚'],
      ['0', 'fnone', '还没到 S1'], [TL_GONE, 'fgone', '未做']],
};
const tlKey = (s) => (!s.exists ? TL_GONE
  : TL_MODE === 'L' ? famKey(s.fam) : String(depthOf({ familiarity: s.fam })));

// opts.ids   = 只**统计**这些题(其余照样跟着回放状态, 只是不计数) —— 配速图要的是某一层
// opts.keyOf = 怎么把一道题的状态归档; 默认跟着 L/S 那个开关走
function buildTimeline(opts = {}) {
  const keyOf = opts.keyOf || tlKey;
  const only = opts.ids || null;
  const st = new Map();                       // id -> {fam, exists}, 先铺现状
  for (const g of (PLAN?.groups || [])) for (const p of g.problems) st.set(p[0], { fam: null, exists: false });
  for (const p of PROBLEMS) st.set(p.id, { fam: famOf(p), exists: true });

  const evs = (EDITS || [])
    .filter((e) => e.date && st.has(e.id) && (e.field === 'familiarity' || e.field === 'exists'))
    .sort((a, b) => (a.ts || 0) - (b.ts || 0));
  if (!evs.length) return null;

  const set = (e, v) => {
    const s = st.get(e.id);
    if (e.field === 'exists') s.exists = !!v;
    else s.fam = (v === null || v === undefined || v === '') ? null : Number(v);
  };
  for (let i = evs.length - 1; i >= 0; i--) set(evs[i], evs[i].from);   // 倒推到第一条事件之前

  const today = todayStr();
  const floor = dAdd(today, -(TL_MAX_DAYS - 1));
  let start = dAdd(evs[0].date, -1);          // 多留一列: 什么都还没发生的样子
  let i = 0;
  if (start < floor) {                        // 太久远的那段直接快进掉, 只留最近的窗口
    start = floor;
    while (i < evs.length && evs[i].date < start) { set(evs[i], evs[i].to); i++; }
  }
  const days = [];
  for (let d = start; d <= today; d = dAdd(d, 1)) {
    while (i < evs.length && evs[i].date <= d) { set(evs[i], evs[i].to); i++; }
    const c = {};
    for (const [id, s] of st) {
      if (only && !only.has(id)) continue;
      const k = keyOf(s); c[k] = (c[k] || 0) + 1;
    }
    days.push({ date: d, c });
  }
  // 日志里全是未来日期(手改过时间戳之类)的话一天都取不到, 别让下面拿 days[-1]
  return days.length ? { days, total: only ? only.size : st.size } : null;
}

// 按算出来的深度归档(不受 TL_MODE 那个开关影响) —— 配速图固定按 S 读
const depthKey = (s) => (!s.exists ? TL_GONE : String(depthOf({ familiarity: s.fam })));

function timelineHTML() {
  const tl = buildTimeline();
  if (!tl) {
    return sblock('掌握度时间轴', '还没有可用的历史',
      `<p class="empty-hint">dashboard/edits.jsonl 还是空的。<br>
       <span class="hint">改一次标签或熟练度就会开始记;
       想把开写之前的历史补回来, 跑 <code>python dashboard/backfill_edits.py --write</code>
       —— 它从 git 里每个碰过 meta.json 的 commit 反推。</span></p>`);
  }
  const rows = TL_ROWS[TL_MODE];
  const last = tl.days.length - 1;
  const cols = tl.days.map((day, k) => ({
    label: k === last ? '今天' : (k % 5 === 0 ? mmdd(day.date) : ''),
    on: k === last,
    n: '',                                    // 每列合计恒等于全库题数, 印一排一样的数没意义
    tip: `${day.date}${k === last ? ' (今天)' : ''} · ` + rows.filter(([key]) => day.c[key])
      .map(([key, , label]) => `${label} ${day.c[key]}`).join(' · '),
    parts: rows.map(([key, cls]) => ({ cls, n: day.c[key] || 0 })),
  }));
  const cur = tl.days[last].c;
  return `<section class="sblock">
    <div class="sblock-head"><b>掌握度时间轴</b>
      <span class="hint">${esc(tl.days[0].date)} 起 · 每列一天 · 分母 ${tl.total} 题(题单 ∪ 仓库)</span>
      <span class="tl-mode" id="tl-mode">${['L', 'S']
        .map((m) => `<button class="tab${m === TL_MODE ? ' on' : ''}" data-mode="${m}">按 ${m}</button>`)
        .join('')}</span></div>
    ${chartHTML(cols, 120)}
    ${slegend(rows.map(([key, cls, label]) => [cls, label, cur[key] || 0]))}</section>`;
}

function renderStats() {
  const box = $('#stats-body');
  const today = todayStr();
  const cards = PROBLEMS.filter(isCard);
  const eligible = PROBLEMS.filter(rvEligible);
  // ⚠️ reviews.jsonl 现在是**两个牌组共用**的一份历史, 靠 deck 字段区分(老行没这个字段
  // = 题目)。这一页所有图表的单位都是"题", 不过滤的话语法卡会混进留存率和复习历史里,
  // 数字看着涨了其实是另一个牌组的。语法牌组只在下面那块概览里出现。
  const rvs = (REVIEWS || []).filter((e) => (e.deck || 'problems') === 'problems');

  const synCards = SYNTAX.filter(isCard);
  const synRvs = (REVIEWS || []).filter((e) => e.deck === 'syntax');
  if (!cards.length && !rvs.length) {
    box.innerHTML = `<p class="empty-hint">还没有任何复习记录。<br>
      <span class="hint">去 🧠 复习 评第一道题, 这里就有东西了 ——
      现在有 <b>${eligible.length}</b> 道题(status 是 solved / review)在等第一次入队。</span></p>`
      + timelineHTML();       // 一次都没复习过, 时间轴照样有东西看(它读的是标签, 不是评分)
    bindTimeline(box);
    return;
  }

  // --- 复习历史按天归并, 顺带算连续天数 ---
  const byDay = new Map();                        // date -> [_, r1, r2, r3, r4]
  for (const e of rvs) {
    const a = byDay.get(e.date) || [0, 0, 0, 0, 0];
    if (a[e.rating] !== undefined) a[e.rating]++;
    byDay.set(e.date, a);
  }
  // 今天还没复习不该把昨天开始的连胜清零, 所以从今天或昨天起算
  let streak = 0;
  for (let d = byDay.has(today) ? today : dAdd(today, -1); byDay.has(d); d = dAdd(d, -1)) streak++;

  // --- 概览 ---
  const overdue = cards.filter((p) => p.due < today).length;
  const dueToday = cards.filter((p) => p.due === today).length;
  const fresh = eligible.filter((p) => !isCard(p)).length;
  const stabs = cards.map((p) => +p.stability || 0).filter((x) => x > 0).sort((a, b) => a - b);
  const median = stabs.length ? stabs[Math.floor(stabs.length / 2)] : 0;
  const mean = stabs.length ? stabs.reduce((a, b) => a + b, 0) / stabs.length : 0;
  // 留存率只算**老卡**: 新卡的第一次评分测的是"做过没有", 不是"记没记住", 混进来会虚高
  const real = rvs.filter((e) => e.state && e.state !== 'new');
  const recalled = real.filter((e) => e.rating >= 2).length;

  let h = `<div class="stiles">
    ${stile(buildQueue().length, '今天要复习', `到期 ${overdue + dueToday} · 新卡 ${fresh}`)}
    ${stile(`${cards.length}/${eligible.length}`, '已入队 / 可复习', fresh ? `还有 ${fresh} 道没进过队列` : '全部进过队列')}
    ${stile(fmtDays(median), '记忆强度中位数', `平均 ${fmtDays(mean)}`)}
    ${stile(real.length ? `${(100 * recalled / real.length).toFixed(0)}%` : '—', '留存率',
            real.length ? `${real.length} 次老卡回忆` : '还没有老卡复习过')}
    ${stile(rvs.length, '累计复习', `${byDay.size} 天 · 连续 ${streak} 天`)}
    ${stile(SYNTAX.length ? `${synCards.length}/${SYNTAX.length}` : '—', '语法卡 已入队 / 总数',
            SYNTAX.length ? `今天要复习 ${deckDue('syntax')} 张 · 累计 ${synRvs.length} 次` : '还没写语法卡')}
  </div>`;

  // --- 未来到期 ---
  const dueBy = new Map();
  for (const p of cards) dueBy.set(p.due, (dueBy.get(p.due) || 0) + 1);
  let ahead = 0;
  const fc = [];
  for (let i = 0; i < FORECAST_DAYS; i++) {
    const d = dAdd(today, i);
    const n = dueBy.get(d) || 0;
    ahead += n;
    const parts = [{ cls: 'b-due', n }];
    if (i === 0 && overdue) parts.unshift({ cls: 'b-over', n: overdue });   // 逾期堆在今天这根的底下
    fc.push({
      label: i === 0 ? '今天' : (i % 5 === 0 ? mmdd(d) : ''),
      on: i === 0,
      tip: `${d}${i === 0 ? ' (今天)' : ''} · 到期 ${n} 道${i === 0 && overdue ? ` · 另有逾期 ${overdue} 道` : ''}`,
      parts,
    });
  }
  h += sblock('未来到期', `接下来 ${FORECAST_DAYS} 天共 ${ahead + overdue} 道 · 鼠标停在柱子上看当天`,
    chartHTML(fc) + slegend([['b-due', '到期', ahead]].concat(overdue ? [['b-over', '逾期', overdue]] : [])));

  // --- 记忆强度分布 ---
  const sc = SBUCKETS.map(() => 0);
  for (const p of cards) { const s = +p.stability || 0; if (s > 0) sc[sBucket(s)]++; }
  h += sblock('记忆强度分布', 'stability = 回忆概率掉到 90% 需要的天数, 越靠右这题记得越牢',
    chartHTML(SBUCKETS.map(([, label], i) => ({
      label, tip: `记忆强度 ${label}: ${sc[i]} 道`, parts: [{ cls: `b-s${i}`, n: sc[i] }],
    })), 84));

  // --- 复习历史 ---
  const hist = [];
  for (let i = HISTORY_DAYS - 1; i >= 0; i--) {
    const d = dAdd(today, -i);
    const a = byDay.get(d) || [0, 0, 0, 0, 0];
    const tot = a[1] + a[2] + a[3] + a[4];
    hist.push({
      label: i === 0 ? '今天' : (i % 5 === 0 ? mmdd(d) : ''),
      on: i === 0,
      tip: `${d} · 共 ${tot} 次${tot ? ' · ' + [1, 2, 3, 4].filter((r) => a[r])
        .map((r) => `${RATE_LABEL[r]} ${a[r]}`).join(' / ') : ''}`,
      parts: [1, 2, 3, 4].map((r) => ({ cls: `b-r${r}`, n: a[r] })),
    });
  }
  const rc = { 1: 0, 2: 0, 3: 0, 4: 0 };
  for (const e of rvs) if (rc[e.rating] !== undefined) rc[e.rating]++;
  h += sblock('复习历史', `最近 ${HISTORY_DAYS} 天 · 按评分堆叠`,
    chartHTML(hist) + slegend([1, 2, 3, 4].map((r) => [`b-r${r}`, RATE_LABEL[r], rc[r]])));

  h += timelineHTML();

  box.innerHTML = h;
  bindTimeline(box);
}

const bindTimeline = (box) => box.querySelectorAll('#tl-mode .tab').forEach((el) =>
  el.addEventListener('click', () => { TL_MODE = el.dataset.mode; renderStats(); }));

async function openStats() {
  $('#stats-overlay').classList.remove('hidden');
  $('#stats-body').innerHTML = '<p class="empty-hint">读取中…</p>';
  if (REVIEWS === null) {
    // 只读站没有这个文件时 shim 会回一个空壳; 拿不到历史也要能画出到期预测那部分
    try { REVIEWS = (await api('/api/reviews')).reviews || []; } catch { REVIEWS = []; }
  }
  if (EDITS === null) {
    try { EDITS = (await api('/api/edits')).edits || []; } catch { EDITS = []; }
  }
  // 时间轴的分母要算上"题单里有、仓库里还没有"的题, 所以这里也得有 plan
  if (!PLAN) { try { PLAN = await api('/api/plan'); } catch { PLAN = null; } }
  renderStats();
}

function closeStats() { $('#stats-overlay').classList.add('hidden'); }
const statsOpen = () => !$('#stats-overlay').classList.contains('hidden');

// ---- 📊 题单覆盖率: dashboard/lists.json 是定义, 进度拿 PROBLEMS 现算 -------
// 定义里有仓库还没有的题(那才是缺口的意义), 所以不能只靠 meta.json 反推。
let LISTS = null;          // {lists: {名字: {source, note, categories}}, premium: [id]}
let LIST_CUR = null;       // 当前看的是哪个题单

// 一题在题单里的档位: 0..4 = 熟练度, null = 建了但没评, -1 = 仓库里压根没有
const listFam = (id) => {
  const p = PROBLEMS.find((x) => x.id === id);
  return p ? famOf(p) : -1;
};
const LBUCKETS = FAM_LEVELS;                      // 进度条从"最熟"到"最生", 未做是剩下的空白

function barHTML(items) {
  const n = items.length || 1;
  const c = Object.fromEntries([...LBUCKETS.map(famKey), '-1'].map((k) => [k, 0]));
  for (const [id] of items) c[famKey(listFam(id))]++;
  const tip = LBUCKETS.map((f) => `${famInfo(f).short} ${c[famKey(f)]}`).join(' · ')
    + ` · 未做 ${c['-1']} · 共 ${items.length}`;
  // 这里以前写的是 c[f]: f 为 null 时取到 c[null] = undefined, 于是"未评"那段
  // 永远画不出来 —— 明明计进了 done, 进度条却少一块。统一走 famKey 就对上了。
  const seg = LBUCKETS
    .filter((f) => c[famKey(f)])
    .map((f) => `<i class="${famCls(f)}" style="width:${(100 * c[famKey(f)] / n).toFixed(2)}%"></i>`)
    .join('');
  return { counts: c, done: items.length - c['-1'], html: `<div class="lbar" title="${esc(tip)}">${seg}</div>` };
}

function renderLists() {
  const names = Object.keys(LISTS?.lists || {});
  if (!names.length) {
    $('#lists-body').innerHTML = '<p class="empty-hint">dashboard/lists.json 里还没有题单定义。</p>';
    return;
  }
  if (!LIST_CUR || !names.includes(LIST_CUR)) LIST_CUR = names[0];

  $('#lists-tabs').innerHTML = names
    .map((n) => `<button class="tab${n === LIST_CUR ? ' on' : ''}" data-list="${esc(n)}">${esc(n)}</button>`)
    .join('');
  $('#lists-tabs').querySelectorAll('.tab').forEach((el) =>
    el.addEventListener('click', () => { LIST_CUR = el.dataset.list; renderLists(); }));

  const def = LISTS.lists[LIST_CUR];
  const premium = new Set(LISTS.premium || []);
  const all = Object.values(def.categories).flat();
  const top = barHTML(all);

  const legend = [...LBUCKETS, -1].map((f) => {
    const label = f === -1 ? '未做' : famInfo(f).label;
    const short = f === -1 ? '·' : famInfo(f).short;
    return `<span class="lkey ${famCls(f)}"><i></i>${esc(short)} ${esc(label)} <b>${top.counts[famKey(f)]}</b></span>`;
  }).join('');

  let h = `<div class="lsum">
      <div class="lsum-head"><b>${top.done} / ${all.length}</b> 已建
        <span class="hint">进度条按熟练度: 越绿越熟, 空白 = 还没建</span></div>
      ${top.html}
      <div class="lkeys">${legend}</div>
      ${def.note ? `<div class="hint lnote">${esc(def.note)}</div>` : ''}
    </div><div class="lcats">`;

  for (const [cat, items] of Object.entries(def.categories)) {
    const b = barHTML(items);
    h += `<div class="lcat">
      <div class="lcat-head">
        <span class="lcat-name">${esc(cat)}</span>
        <span class="lcat-n">${b.done}/${items.length}</span>
      </div>
      ${b.html}
      <div class="lchips">${items.map(([id, title]) => {
        const f = listFam(id);
        const star = premium.has(id) ? '<span class="lprem" title="LeetCode 会员题">*</span>' : '';
        const badge = f !== -1 && f !== null ? `<i class="lfam ${famCls(f)}">${famInfo(f).short}</i>` : '';
        const act = f === -1
          ? ` data-add="${id}" title="点一下建文件夹并抓题面"`
          : ` data-open="${id}" title="${esc(title)} · ${esc(famInfo(f).label)}"`;
        return `<span class="lchip ${famCls(f)}"${act}>${badge}${id}${star} <em>${esc(title)}</em></span>`;
      }).join('')}</div>
    </div>`;
  }
  h += '</div>';
  $('#lists-body').innerHTML = h;

  $('#lists-body').querySelectorAll('[data-open]').forEach((el) =>
    el.addEventListener('click', () => { closeLists(); openDetail(+el.dataset.open); }));
  $('#lists-body').querySelectorAll('[data-add]').forEach((el) =>
    el.addEventListener('click', () => addFromList(el, +el.dataset.add)));
}

// 复用 TODO 那条路: POST /api/problems -> scaffold 建文件夹 + 抓题面 + 进索引
async function addFromList(el, id) {
  if (el.classList.contains('busy')) return;
  el.classList.add('busy');
  const old = el.innerHTML;
  el.innerHTML = `${id} <em>建中…</em>`;
  let r;
  try {
    r = await postProblem(id);
  } catch { r = null; }
  if (!r || !r.ok) {
    el.innerHTML = old;
    el.classList.remove('busy');
    el.title = (r && r.error) || '建不了(会员题或离线?)';
    el.classList.add('failed');
    return;
  }
  PROBLEMS = await api('/api/problems');
  buildPanel();
  renderLists();                      // 重画, 那一格会变成"已建待做"
}

async function openLists() {
  if (!LISTS) LISTS = await api('/api/lists');
  $('#lists-overlay').classList.remove('hidden');
  renderLists();
}
function closeLists() { $('#lists-overlay').classList.add('hidden'); }

// ---- TODO: notes/todo.md 就是唯一数据源 ------------------------------------
// server 早有 GET/PUT /api/notes/<file>, 所以这块纯前端, 后端一行没改。
// 非 checkbox 行(标题、说明文字)原样保留, 方便在 VSCode 里直接编辑同一个文件。
const TODO_FILE = 'todo.md';
const TODO_RE = /^(\s*[-*]\s*\[)([ xX])(\]\s*)(.*)$/;
let TODO_LINES = [];     // 文件的全部行
let TODO_VIEW = [];      // 渲染出来的条目, 带 orig 原始行文本(用来定位, 不用下标)

async function loadTodo(render = true) {
  const n = await api('/api/notes/' + TODO_FILE);
  TODO_LINES = (n.content || '').split('\n');
  if (render) renderTodo();
}

function todoItems() {
  const out = [];
  TODO_LINES.forEach((line, i) => {
    const m = TODO_RE.exec(line);
    if (m) out.push({ i, done: m[2].toLowerCase() === 'x', text: m[4].trim() });
  });
  return out;
}

let TODO_MSG_T = null;
function flashTodo(msg, ms = 1500) {
  clearTimeout(TODO_MSG_T);                        // 别让上一条的定时器把这条提前清掉
  $('#todo-msg').textContent = msg;
  TODO_MSG_T = setTimeout(() => ($('#todo-msg').textContent = ''), ms);
}

async function putTodo() {
  await fetch('/api/notes/' + TODO_FILE, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: TODO_LINES.join('\n') }),
  });
}

// 改之前先重读一遍文件: 我可能刚在 VSCode / CLI 那边改过, 别拿旧内容覆盖掉。
// 定位用"原始行文本"而不是下标, 因为重读之后下标可能整体错位。
async function todoMutate(orig, fn) {
  await loadTodo(false);
  const i = TODO_LINES.indexOf(orig);
  if (i < 0) { renderTodo(); flashTodo('文件已变, 已刷新'); return false; }
  fn(i);
  await putTodo();
  renderTodo();
  flashTodo('已存 ✓');
  return true;
}

// 勾上 = 做完了, 直接从 todo.md 删掉(留一次撤销), 别攒一堆 [x] 在文件里。
// 手写在文件里的 [x] 行取消勾选还是还原成 [ ]。
let TODO_UNDO = null;                              // 最近一次勾掉的 {line, at}

function toggleTodo(orig) {
  const m = TODO_RE.exec(orig);
  if (m && m[2].toLowerCase() === 'x') {           // [x] -> [ ]
    return todoMutate(orig, (i) => {
      const mm = TODO_RE.exec(TODO_LINES[i]);
      TODO_LINES[i] = mm[1] + ' ' + mm[3] + mm[4];
    });
  }
  return doneTodo(orig);
}

async function doneTodo(orig) {
  const ok = await todoMutate(orig, (i) => {
    TODO_UNDO = { line: TODO_LINES[i], at: i };
    TODO_LINES.splice(i, 1);
  });
  if (ok) flashUndo();
}

function flashUndo() {
  clearTimeout(TODO_MSG_T);
  const el = $('#todo-msg');
  el.innerHTML = '已完成 ✓ <span class="todo-undo">撤销</span>';
  TODO_MSG_T = setTimeout(() => (el.textContent = ''), 6000);
  el.querySelector('.todo-undo').addEventListener('click', async () => {
    const u = TODO_UNDO;
    if (!u) return;
    TODO_UNDO = null;
    await loadTodo(false);                         // 重读, 别覆盖我在别处的改动
    TODO_LINES.splice(Math.min(u.at, TODO_LINES.length), 0, u.line);
    await putTodo();
    renderTodo();
    flashTodo('已撤销 ✓');
  });
}

function removeTodo(orig) { todoMutate(orig, (i) => TODO_LINES.splice(i, 1)); }

// 输入 "34" -> 有文件夹就补上标题, 没有就只记编号; 也允许 "34 自定义文字" 或直接写题名
async function addTodo() {
  const raw = $('#todo-in').value.trim();
  if (!raw) return;
  const m = /^(\d+)\s*(.*)$/.exec(raw);
  let text = raw;
  if (m) {
    const p = PROBLEMS.find((x) => x.id === +m[1]);
    text = m[2] ? `${m[1]} ${m[2]}` : p ? `${m[1]} ${p.title}` : m[1];
  }
  await loadTodo(false);
  if (m && todoItems().some((t) => !t.done && /^(\d+)/.exec(t.text)?.[1] === m[1])) {
    $('#todo-in').value = '';
    renderTodo();
    return flashTodo('已经在列表里了');
  }
  const items = todoItems();                       // 插在最后一条之后, 保持标题/说明在最上面
  const at = items.length ? items[items.length - 1].i + 1 : TODO_LINES.length;
  const line = `- [ ] ${text}`;
  TODO_LINES.splice(at, 0, line);
  await putTodo();
  $('#todo-in').value = '';
  renderTodo();
  flashTodo('已加 ✓');
  // 纯题号 / 纯题名的才去建文件夹; "34 自定义文字" 是随手记, 别乱猜
  scaffoldForTodo(m ? m[1] : raw, line, !m || !m[2]);
}

// 还没有文件夹的题 -> 让后端拉题面 + 建空 sol.py/note.md + 进索引表, 建完刷新看板。
// 不 await: 加 todo 这个动作已经落盘了, 网络慢不该卡住输入框。
async function scaffoldForTodo(query, line, canon) {
  const id = /^\d+$/.test(query) ? +query : null;
  if (id ? PROBLEMS.some((p) => p.id === id)
         : PROBLEMS.some((p) => p.title.toLowerCase() === query.toLowerCase())) return;
  flashTodo('拉题中…');
  let r;
  try {
    r = await postProblem(query);
  } catch {
    return flashTodo('拉题失败(离线?)');
  }
  if (!r || !r.ok) return flashTodo(r?.error || '拉题失败');
  PROBLEMS = await api('/api/problems');
  buildPanel();
  await loadTodo(false);                           // 重读, 别覆盖我在别处的改动
  const i = TODO_LINES.indexOf(line);              // 题名/裸题号那条补成 "编号 标题"
  if (canon && i >= 0 && TODO_LINES[i] !== `- [ ] ${r.id} ${r.title}`) {
    TODO_LINES[i] = `- [ ] ${r.id} ${r.title}`;
    await putTodo();
  }
  renderTodo();
  flashTodo(r.created ? (r.note ? `已建, ${r.note}` : `已建 ${r.folder} ✓`) : '看板里已经有了');
}

function renderTodo() {
  const items = todoItems();
  TODO_VIEW = items.map((t) => ({ ...t, orig: TODO_LINES[t.i] }));
  const open = items.filter((t) => !t.done).length;
  $('#todo-n').textContent = open;
  $('#todo-n').classList.toggle('hidden', !open);

  $('#todo-list').innerHTML = TODO_VIEW.length
    ? TODO_VIEW.map((t, k) => {
        const id = (/^(\d+)/.exec(t.text) || [])[1];
        const p = id ? PROBLEMS.find((x) => x.id === +id) : null;
        const diff = p ? p.difficulty || 'none' : '';
        return `<div class="todo-item${t.done ? ' done' : ''}">
          <input type="checkbox" class="todo-cb" data-k="${k}" ${t.done ? 'checked' : ''}>
          ${p ? `<span class="dot ${diff}" title="${diff}"></span>` : '<span class="dot none ghosted"></span>'}
          <span class="todo-text${p ? ' openable' : ''}"${p ? ` data-open="${p.id}" title="打开 #${p.id}"` : ''}>${esc(t.text)}</span>
          <span class="todo-x" data-k="${k}" title="从列表删掉">✕</span>
        </div>`;
      }).join('')
    : '<div class="todo-empty">还没有 todo。上面输入题号回车添加。</div>';

  $('#todo-list').querySelectorAll('.todo-cb').forEach((el) =>
    el.addEventListener('change', () => toggleTodo(TODO_VIEW[+el.dataset.k].orig)));
  $('#todo-list').querySelectorAll('.todo-x').forEach((el) =>
    el.addEventListener('click', () => removeTodo(TODO_VIEW[+el.dataset.k].orig)));
  $('#todo-list').querySelectorAll('.todo-text.openable').forEach((el) =>
    el.addEventListener('click', () => { closeTodoPop(); openDetail(+el.dataset.open); }));
}

function closeTodoPop() { $('#todo-pop').classList.add('hidden'); }

async function toggleTodoPop() {
  const pop = $('#todo-pop');
  if (!pop.classList.contains('hidden')) return closeTodoPop();
  await loadTodo();                   // 每次打开都重读, 拿到我在别处的改动
  pop.classList.remove('hidden');
  $('#todo-in').focus();
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

// ---- 坐标系 view: coverage (tier) × depth (stage) ----
// tier  = how far the题单 is spread (75 / 110 / 135)
// stage = how well each problem is held (S1 思路 / S2 写得对 / S3 讲得清)
// a cell counts problems at that stage *or deeper*, so S3 also feeds S1 and S2.
let PLAN = null;   // dashboard/plan.json — the curriculum, hand-edited
const tierName = (t) => (PLAN.tiers.find((x) => x.t === t) || {}).name || `第 ${t} 层`;
const stageName = (sv) => (PLAN.stages.find((x) => x.s === sv) || {}).t || `S${sv}`;
let VIEW = 'board';

// 深度不另存: 由每题 meta.json 的 familiarity 算出来。一个字段, 一条阶梯:
//   L0 英语讲得清                      -> S3 讲得清 (面试门槛)
//   L1 已经熟悉 / L2 思路会·细节易写错  -> S2 写得对 (OA 门槛)
//   L3 思路大概知道·不熟               -> S1 思路清楚
//   L4 思路都不知道 / 未评 / 没建文件夹  -> 还没到 S1
// 阶梯是有序的, 所以 S3 ⊂ S2 ⊂ S1 由构造保证 —— 讲得清的题必然也写得对,
// 不会出现"讲得出但写不对"的题混进 S2 那一列(而 S2 正是判断能不能做 OA 的那列)。
const byId = () => new Map(PROBLEMS.map((p) => [p.id, p]));
function depthOf(rec) {
  if (!rec) return 0;
  const L = famOf(rec);
  if (L === null) return 0;       // 未评 —— 不能落进下面任何区间
  if (L <= 0) return 3;           // L0 讲得清
  if (L <= 2) return 2;           // L1 / L1.5 / L2 —— 都是"跑得过", 够 OA 门槛
  if (L <= 3) return 1;           // L3 思路大概知道 —— S1 的下界就划在这儿
  return 0;                       // L3.5 / L4 —— 方向感不算"思路清楚", 够不着 S1
}


const parseDay = (s) => { const a = s.split('-').map(Number); return new Date(a[0], a[1] - 1, a[2]); };
const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

// tag every phase past/active/future against today, and pick the live one
function datePhases() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const ps = PLAN.phases;
  for (const ph of ps) {
    const from = parseDay(ph.from);
    const to = ph.to ? parseDay(ph.to) : null;
    ph.state = today < from ? 'future' : (to && today >= to) ? 'past' : 'active';
  }
  const live = ps.find((p) => p.state === 'active')
    || (today < parseDay(ps[0].from) ? ps[0] : ps[ps.length - 1]);
  return { today, live };
}

function planProblems() {
  const rec = byId();
  const out = [];
  for (const g of PLAN.groups)
    for (const p of g.problems)
      out.push({ id: p[0], tier: g.tier, rec: rec.get(p[0]), depth: depthOf(rec.get(p[0])) });
  return out;
}

function buildGrid() {
  if (!PLAN) return;
  if (PLAN.error) { $('#grid-view').innerHTML = `<p class="empty-hint">${esc(PLAN.error)}</p>`; return; }

  const { today, live } = datePhases();
  const all = planProblems();
  const size = (t) => all.filter((p) => p.tier === t).length;
  const reached = (t, s) => all.filter((p) => p.tier === t && p.depth >= s).length;

  const md_ = (d) => `${d.getMonth() + 1}/${d.getDate()}`;
  const spanOf = (ph) => md_(parseDay(ph.from)) + (ph.to ? ' – ' + md_(parseDay(ph.to)) : ' 起');
  const daysLeft = (ph) => (ph.to ? Math.max(0, Math.round((parseDay(ph.to) - today) / 864e5)) : null);

  $('#sub').textContent = '覆盖 × 深度 · NeetCode 150';
  $('#count').textContent =
    `${all.filter((p) => p.rec).length}/${all.length} 有文件夹 · 阶段 ${live.n}`;

  // --- 概览条: 首屏第一眼只需要回答两件事 —— 我在哪个阶段, 这阶段要把哪几格推到底。
  // 下面的矩阵/时间线/题目都是它的展开, 所以这里只放数字和差额, 不重复解释。
  const goals = PLAN.targets.filter((x) => x.phase === live.n).map((x) => {
    const N = size(x.tier), n = reached(x.tier, x.stage), pct = N ? Math.round((n / N) * 100) : 0;
    return `<div class="gr-hg">
      <div class="gr-hg-t">${esc(tierName(x.tier))}<span
        class="gr-hg-ar">→</span>${esc(stageName(x.stage))}</div>
      <div class="gr-hg-bar"><i class="s${x.stage}" style="width:${pct}%"></i></div>
      <div class="gr-hg-n"><b>${n}</b><small>/${N}</small><span class="gr-hg-gap${n >= N ? ' met' : ''}">${
        n >= N ? '已达标 ✓' : '还差 ' + (N - n) + ' 题'}</span></div></div>`;
  }).join('');
  // 底下这排是**跨层**的总计 —— 上面的矩阵只按层拆, 全局这三个数在那儿看不到。
  const built = all.filter((p) => p.rec).length;
  const stat = (label, n, cls) => {
    const pct = Math.round((n / all.length) * 100);
    return `<div class="gr-st4">
      <div class="gr-st4-t">${esc(label)}</div>
      <div class="gr-st4-n"><b>${n}</b><small>/${all.length}</small></div>
      <div class="gr-st4-bar"><i class="${cls}" style="width:${pct}%"></i></div></div>`;
  };
  const stats = stat('已建文件夹', built, 'built')
    + PLAN.stages.map((st) => stat(`S${st.s} 及以上`, all.filter((x) => x.depth >= st.s).length, `s${st.s}`)).join('');
  const dl = daysLeft(live);
  const hero = `<section class="gr-hero">
    <div class="gr-hero-l">
      <div class="gr-hero-k">现在</div>
      <h2 class="gr-hero-ph"><span class="gr-hero-n">阶段 ${live.n}</span>${esc(live.name)}</h2>
      <div class="gr-hero-when">${spanOf(live)}　·　${esc(live.hrs)}${
        dl !== null ? `<b class="gr-hero-left">剩 ${dl} 天</b>` : ''}</div>
      <div class="gr-hero-goal">${esc(live.adds)}</div>
      <div class="gr-hero-serves">${esc(live.serves)}</div>
    </div>
    <div class="gr-hero-r">
      <div class="gr-hero-k">这阶段要推到底的格子</div>
      <div class="gr-hero-goals">${goals || '<span class="gr-hg-gap">这阶段没设目标格</span>'}</div>
      <div class="gr-hero-cov">${stats}</div>
    </div>
  </section>`;

  // --- the grid itself: tiers down, stages across ---
  let m = '<div class="gr-matrix"><div></div>';
  for (const st of PLAN.stages)
    m += `<div class="gr-colh" data-s="${st.s}"><span class="gr-colh-t">${esc(st.t)}</span><span class="gr-colh-d">${esc(st.d)}</span></div>`;
  for (const tr of PLAN.tiers) {
    const N = size(tr.t);
    m += `<div class="gr-rowh">
      <button class="gr-rowh-t" data-jump="${tr.t}" title="跳到下面「题目」里这一层的第一组">
        <b class="gr-tno">${tr.t}</b>
        <span class="gr-rowh-nm">${esc(tr.name)}<span class="gr-jump-x">▾</span></span>
        <span class="gr-rowh-n">本层 ${N} 题 · 做完题单累计 ${esc(tr.cum)}</span></button>
      <span class="gr-rowh-d">${esc(tr.desc)}</span></div>`;
    for (const st of PLAN.stages) {
      const n = reached(tr.t, st.s);
      const pct = N ? Math.round((n / N) * 100) : 0;
      const tg = PLAN.targets.filter((x) => x.tier === tr.t && x.stage === st.s);
      const isNow = tg.some((x) => x.phase === live.n);
      const badges = tg
        .map((x) => `<span class="gr-badge${x.phase < live.n ? ' met' : ''}">阶段 ${x.phase} 目标</span>`)
        .join('');
      m += `<div class="gr-cell${isNow ? ' target' : ''}${n ? '' : ' zero'}">
        ${isNow ? '<span class="gr-now">现在</span>' : ''}
        <div class="gr-cell-top"><span class="gr-frac">${n}<small>/${N}</small></span><span class="gr-pct">${pct}%</span></div>
        <div class="gr-bar"><i class="s${st.s}" style="width:${pct}%"></i></div>
        <div class="gr-cell-foot">${badges || '&nbsp;'}</div></div>`;
    }
  }
  m += '</div>';

  // --- timeline: the four phases are a real sequence, so they're numbered ---
  let t = '<div class="gr-tl">';
  for (const ph of PLAN.phases) {
    const range = spanOf(ph);
    const left = daysLeft(ph);
    t += `<div class="gr-ph ${ph.state}">
      <div class="gr-ph-n"><span>阶段 ${ph.n}</span>${
        ph.state === 'active' ? `<span class="gr-live">进行中${left !== null ? ' · 剩 ' + left + ' 天' : ''}</span>` : ''}</div>
      <h3>${esc(ph.name)}</h3>
      <div class="gr-ph-when">${range}　·　${esc(ph.hrs)}</div>
      <div class="gr-goal">${esc(ph.goal)}</div>
      <div class="gr-adds">${esc(ph.adds)}</div>
      <div class="gr-serves">${esc(ph.serves)}</div></div>`;
  }
  t += '</div>';

  // --- the problems, by pattern group; click a chip to cycle its stage ---
  const recs = byId();
  const famTip = {};
  for (const f of (PLAN.familiarity || [])) {
    const d = depthOf({ familiarity: f.l });
    famTip[f.l] = `${f.t} ${f.d} → ${d ? 'S' + d : '还没到 S1'}`;
  }
  const depths = new Map(all.map((p) => [p.id, p.depth]));
  const seenTier = new Set();          // 每层第一组挂锚点, 给上面的行标签跳
  let g = '';
  for (const grp of PLAN.groups) {
    const started = grp.problems.filter((p) => (depths.get(p[0]) || 0) >= 1).length;
    const label = `第 ${grp.tier} 层${grp.low ? ' · 低优先' : ''}`;
    const chips = grp.problems.map((p) => {
      const rec = recs.get(p[0]);
      const L = rec ? famOf(rec) : undefined;        // undefined = 还没建文件夹
      const d = depthOf(rec);
      const badge = rec === undefined ? '+' : famInfo(L).short;
      const tip = rec === undefined ? '还没建文件夹 — 点击建（去 LeetCode 抓题面）'
        : L === null ? '还没评熟练度 — 点击标 L4' : famTip[L];
      // 两个点击区: 左边徽章翻熟练度(或建文件夹), 右边题名打开详情。
      // 内层 span 的 title 会盖住外层 button 的, 所以悬停提示也各说各的。
      return `<button class="gr-chip" data-id="${p[0]}" data-d="${d}" title="${esc(p[1])} — ${
        rec === undefined ? '还没建文件夹 — 点击建（去 LeetCode 抓题面）' : '点击打开题目'}">
          <span class="gr-st s${d}" title="${esc(p[1])} — ${esc(tip)}">${badge}</span>
          <span class="gr-id">${p[0]}</span>
          <span class="gr-nm">${esc(p[1])}</span>
          <span class="dot ${p[2]}"></span></button>`;
    }).join('');
    const anchor = seenTier.has(grp.tier) ? '' : ` id="gr-tier-${grp.tier}"`;
    seenTier.add(grp.tier);
    // 组标题 -> 这个 pattern 的通用 trick 文档, 和矩阵视图点组标签是同一个 overlay
    // 一个组可以跨多个概念(如 Arrays & Hashing), 所以 tag 支持数组。
    // 旧的单 tag 写法继续兼容 —— 只有一个 tag 时渲染成原样, 视觉零变化。
    const tags = grp.tags || (grp.tag ? [grp.tag] : []);
    const kindCN = (k) => (k === 'paradigms' ? '范式' : '结构');
    const docBtn = (t, label, extra) =>
      `<button class="gr-doc${extra || ''}" data-kind="${t.kind}" data-tag="${esc(t.name)}"
         title="打开${kindCN(t.kind)} ${esc(t.name)} 的通用 trick 文档">${label}</button>`;
    const head = tags.length === 1
      ? `<h3>${docBtn(tags[0],
           `${esc(grp.name)}<span class="gr-doc-x">通用 trick →</span>`)}</h3>`
      : tags.length
        ? `<h3><span class="gr-nm-plain">${esc(grp.name)}</span>${
             tags.map((t) => docBtn(t, `${esc(t.name)} →`, ' gr-doc-multi')).join('')}</h3>`
        : `<h3>${esc(grp.name)}</h3>`;
    g += `<div class="gr-grp${grp.low ? ' low' : ''}"${anchor}>
      <div class="gr-grp-h">${head}
        <span class="gr-tier${grp.low ? ' low' : ''}" data-t="${grp.tier}">${label}</span>
        ${grp.sub ? `<span class="gr-sub">${esc(grp.sub)}</span>` : ''}
        <span class="gr-grp-c"><b>${started}</b>/${grp.problems.length}<i class="gr-grp-bar"><u
          style="width:${Math.round((started / grp.problems.length) * 100)}%"></u></i></span></div>
      <div class="gr-chips">${chips}</div></div>`;
  }

  $('#grid-view').innerHTML = `
    ${hero}
    <section class="gr-sec">
      <div class="gr-sec-h"><h2><span class="gr-sec-n">1</span>格子</h2><p>每格 = 该层里达到<b>该深度及以上</b>的题数 —— 一道 S3 的题同时计进 S1、S2 三列。层之间<b>不</b>累计：每题只属于一层。琥珀格 = 当前阶段该站的位置。</p></div>
      ${m}
      <div class="gr-legend">
        <span class="gr-key"><i class="s0"></i>L4 / 未评 · 还没到 S1</span>
        <span class="gr-key"><i class="s1"></i>L3 → S1 思路清楚</span>
        <span class="gr-key"><i class="s2"></i>L1–L2 → S2 能写对</span>
        <span class="gr-key"><i class="s3"></i>L0 → S3 讲得清</span>
      </div>
      <p class="gr-note">S1→S2 是 OA 门槛，S2→S3 是面试门槛。S3 不是第三阶段才开始练 —— 阶段一就挑 15 题顺手讲，
      否则会攒下一整个月「做得出但讲不清」的题。</p>
    </section>
    <section class="gr-sec" id="gr-pace"><p class="empty-hint">读取历史…</p></section>
    <section class="gr-sec">
      <div class="gr-sec-h"><h2><span class="gr-sec-n">3</span>时间线</h2><p>四段是真序列：每段的目标格建立在前一段已达标的基础上。</p></div>
      ${t}
    </section>
    <section class="gr-sec">
      <div class="gr-sec-h"><h2><span class="gr-sec-n">4</span>题目</h2><p>点方块循环熟练度 <span class="mono">— → L4 → L3 → L2 → L1 → L0</span>，写回该题 meta.json，
      和详情页那个下拉是同一个字段。没建文件夹的显示 <span class="mono">+</span>，点一下抓题面建目录。
      <b>灰掉的组</b>低优先，时间不够先砍它们。</p></div>
      ${g}
    </section>`;
  renderPace();          // 异步: 要等 edits.jsonl
}

// 顺着"越来越熟"的方向走, 走到顶再回到未评
const L_NEXT = { none: 4, 4: 3.5, 3.5: 3, 3: 2, 2: 1.5, 1.5: 1, 1: 0, 0: null };

// 改标签的**唯一**出口(看板的熟练度菜单 / 详情页 / 坐标系上点方块都走这儿) ——
// 服务器每次都会往 edits.jsonl 追一行, 所以顺手把时间轴的缓存作废。
// 建题目文件夹的唯一出口(📋 TODO / 题单那格 / 坐标系上的 + 都走这儿) ——
// 服务器会记一行"未做 → 进了库", 时间轴的分子分母都跟着变, 同样作废缓存。
const postProblem = (query) => {
  EDITS = null;
  return api('/api/problems', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: String(query) }),
  });
};

const putMeta = (id, body) => {
  EDITS = null;
  return fetch(`/api/problems/${id}/meta`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
};

async function cycleL(id) {
  const rec = byId().get(id);
  if (!rec) return;                 // 没文件夹的走 startProblem, 不该到这儿
  await putMeta(id, { familiarity: L_NEXT[famKey(famOf(rec))] });
  await reload();
}

// 全局轻提示。flashTodo 写的是 📋 面板里的一行, 关着面板就看不见;
// 在坐标系上建题这类动作没有现成的地方写反馈, 给它一个。
let FLASH_T = null;
function flash(msg, ms = 5000) {
  let el = $('#flash');
  if (!el) { el = document.createElement('div'); el.id = 'flash'; document.body.appendChild(el); }
  el.textContent = msg;
  el.classList.add('on');
  clearTimeout(FLASH_T);
  FLASH_T = setTimeout(() => el.classList.remove('on'), ms);
}

// 没人接的报错一律亮出来。这一屏(复习)大量是 async: 一个 await 抛了, Vue 不会渲染任何
// 东西, 页面就那么定在原地 —— 只有 console 里有一行, 而复习的时候没人开着 console。
// 亮一条比什么都不说强: 至少知道该刷新, 而不是对着不动的卡面反复按键。
const bang = (what, err) => {
  console.error(what, err);
  flash(`⚠ 前端出错(${what}): ${(err && err.message) || err} —— 刷新一下, 详情看 console`);
};
window.addEventListener('unhandledrejection', (e) => bang('异步', e.reason));
window.addEventListener('error', (e) => { if (e.error) bang('脚本', e.error); });

// 还没建文件夹的题, 点一下 = "开始这道题": 抓题面 + 建目录, 和题单 / 📋 TODO 同一条路。
// 和题单那格(addFromList)对齐: 建中给个态, 失败留在原地并把原因写进 title ——
// 早先这里是裸 fetch 且不看返回值, 会员题(题面抓不到)和离线都静默失败, 看着像没反应。
async function startProblem(id, chip) {
  if (chip.classList.contains('busy')) return;
  chip.classList.add('busy');
  chip.classList.remove('failed');
  const badge = chip.querySelector('.gr-st');
  const old = badge.textContent;
  badge.textContent = '…';
  let r;
  try {
    r = await postProblem(id);
  } catch { r = null; }
  if (!r || !r.ok) {
    badge.textContent = old;
    chip.classList.remove('busy');
    chip.classList.add('failed');
    chip.title = (r && r.error) || '建不了(离线?) — 再点一下重试';
    return;
  }
  // 文件夹建了但题面没抓到(会员题) —— 不是失败, 但得说一声, 否则详情页一片空白没人知道为什么
  if (r.created && r.description === false) {
    flash(`#${id} 文件夹建好了, 但题面没抓到(会员题?) — 可跑 dashboard/fetch_desc.py ${id} 重试`);
  }
  await reload();                   // 重画后这个 chip 就换成新的了, busy 态跟着没
}



// ---- 配速: 把这一格剩下的题均摊到阶段的每一天, 看实际爬得比计划快还是慢 ------
// 数据和「掌握度时间轴」同一条路: edits.jsonl 逐日回放, 不落第二份统计。
//
// **计划线从阶段开始那天的实际值起步, 不是从 0 起步。** 阶段一开始时第一层已经有一批
// 题到了 S1(9/1 那次批量评级), 从 0 画会显示"领先十几题", 其实一天都没多做。
// 均摊的是**剩下的**: (总数 − 起点) / 阶段天数。
let PACE_SEL = null;                 // "tier:stage"; null = 还没选过, 取第一项

function paceOptions() {
  const { live } = datePhases();
  const out = [];
  for (const t of PLAN.targets.filter((x) => x.phase === live.n))
    for (let s = 1; s <= t.stage; s++) out.push({ tier: t.tier, stage: s, phase: live });
  return out;
}

const pcFmt = (n) => n.toFixed(1).replace(/\.0$/, '');

function paceHTML() {
  const head = (body) => `<div class="gr-sec-h"><h2><span class="gr-sec-n">2</span>配速</h2>
    <p>把目标格<b>剩下</b>的题均摊到阶段的每一天，和实际爬到的高度比 ——
    计划线的起点是<b>阶段开始那天的实际值</b>，不是 0，否则开局就凭空"领先"一大截。</p></div>${body}`;
  if (!PLAN || PLAN.error) return head('');
  const opts = paceOptions();
  const kOf = (o) => `${o.tier}:${o.stage}`;
  const sel = opts.find((o) => kOf(o) === PACE_SEL) || opts[0];
  if (!sel) return head('<p class="empty-hint">当前阶段没有设目标格，没有可对的计划。</p>');
  PACE_SEL = kOf(sel);
  const ph = sel.phase;
  const tabs = `<div class="groupby pc-tabs">${opts.map((o) =>
    `<button class="gb-btn${kOf(o) === PACE_SEL ? ' on' : ''}" data-pace="${kOf(o)}"
       >${esc(tierName(o.tier))} S${o.stage}</button>`).join('')}</div>`;
  if (!ph.to) return head(`${tabs}<p class="empty-hint">阶段 ${ph.n} 没有结束日，均摊无从谈起。</p>`);

  const ids = new Set();
  for (const g of PLAN.groups) if (g.tier === sel.tier) for (const p of g.problems) ids.add(p[0]);
  const tl = buildTimeline({ ids, keyOf: depthKey });
  if (!tl) {
    return head(`${tabs}<p class="empty-hint">dashboard/edits.jsonl 还没有可用的历史，画不出实际线。<br>
      <span class="hint">跑 <code>python dashboard/backfill_edits.py --write</code> 从 git 里把历史补回来。</span></p>`);
  }

  // 达到 sel.stage 及以上 = 深度桶 sel.stage..3 之和(和格子里那个"及以上"同一个口径)
  const reached = (c) => [1, 2, 3].reduce((n, s) => n + (s >= sel.stage ? (c[String(s)] || 0) : 0), 0);
  const hist = new Map(tl.days.map((d) => [d.date, reached(d.c)]));
  const firstDay = tl.days[0].date, lastDay = tl.days[tl.days.length - 1].date;
  const at = (date) => (hist.has(date) ? hist.get(date)
    : date < firstDay ? reached(tl.days[0].c) : reached(tl.days[tl.days.length - 1].c));

  const ix = (date) => Math.round((dParse(date) - dParse(ph.from)) / 864e5);
  const span = ix(ph.to);
  if (span <= 0) return head(`${tabs}<p class="empty-hint">阶段 ${ph.n} 的起止日期不合法。</p>`);
  const cur = Math.min(Math.max(ix(todayStr()), 0), span);
  const total = ids.size;
  const base = at(ph.from);
  const per = (total - base) / span;                   // 计划每天几题
  const planAt = (i) => base + per * i;
  const act = [];
  for (let i = 0; i <= cur; i++) act.push(at(dAdd(ph.from, i)));
  const now = act[cur];
  const delta = now - planAt(cur);
  const leftDays = Math.max(1, span - cur);
  const needPer = Math.max(0, (total - now) / leftDays);
  const aheadDays = per > 0 ? delta / per : 0;
  const ahead = delta >= 0;

  // --- SVG: 计划线(虚) vs 实际线(实), 今天那一列画出两者的差 ---
  const W = 760, H = 190, L = 42, R = 14, T = 12, B = 26;
  const x = (i) => L + (W - L - R) * (i / span);
  const y = (v) => T + (H - T - B) * (1 - v / (total || 1));
  const n2 = (v) => v.toFixed(1);
  const grid = [0, .25, .5, .75, 1].map((f) => {
    const v = total * f, yy = y(v);
    return `<line class="pc-grid" x1="${n2(L)}" y1="${n2(yy)}" x2="${n2(W - R)}" y2="${n2(yy)}"/>`
      + `<text class="pc-ylbl" x="${n2(L - 7)}" y="${n2(yy + 3.5)}">${Math.round(v)}</text>`;
  }).join('');
  const step = Math.max(1, Math.ceil(span / 7));
  const marks = [];
  for (let i = 0; i < span - step / 2; i += step) marks.push(i);
  marks.push(span);
  const xlbl = marks.map((i, k) => `<text class="pc-xlbl" x="${n2(x(i))}" y="${H - 8}"
    text-anchor="${i === 0 ? 'start' : i === span ? 'end' : 'middle'}"
    >${esc(mmdd(dAdd(ph.from, i)))}${i === span ? ' 截止' : ''}</text>`).join('');
  const pts = act.map((v, i) => `${n2(x(i))},${n2(y(v))}`).join(' ');
  const svg = `<svg class="pc-svg" viewBox="0 0 ${W} ${H}" role="img"
      aria-label="计划 vs 实际配速">
    ${grid}
    <line class="pc-base" x1="${n2(L)}" y1="${n2(y(base))}" x2="${n2(W - R)}" y2="${n2(y(base))}"/>
    <text class="pc-blbl" x="${n2(W - R - 5)}" y="${n2(y(base) - 5)}" text-anchor="end">起点 ${base}</text>
    <polygon class="pc-fill" points="${n2(x(0))},${n2(y(0))} ${pts} ${n2(x(cur))},${n2(y(0))}"/>
    <line class="pc-plan" x1="${n2(x(0))}" y1="${n2(y(base))}" x2="${n2(x(span))}" y2="${n2(y(total))}"/>
    <polyline class="pc-act" points="${pts}"/>
    <line class="pc-today" x1="${n2(x(cur))}" y1="${T}" x2="${n2(x(cur))}" y2="${H - B}"/>
    <line class="pc-gap ${ahead ? 'ahead' : 'behind'}" x1="${n2(x(cur))}" y1="${n2(y(planAt(cur)))}"
          x2="${n2(x(cur))}" y2="${n2(y(now))}"/>
    <circle class="pc-goal" cx="${n2(x(span))}" cy="${n2(y(total))}" r="3.5"/>
    <circle class="pc-dot ${ahead ? 'ahead' : 'behind'}" cx="${n2(x(cur))}" cy="${n2(y(now))}" r="4"/>
    ${xlbl}
  </svg>`;

  const tile = (v, label, sub, cls) => `<div class="pc-t${cls ? ' ' + cls : ''}">
    <b>${esc(v)}</b><span>${esc(label)}</span><em>${esc(sub)}</em></div>`;
  const tiles = `<div class="pc-tiles">
    ${tile(`${now}/${total}`, `实际已到 S${sel.stage}`, `阶段开始时 ${base} 题`)}
    ${tile(pcFmt(planAt(cur)), '今天应达', `计划 ${pcFmt(per)} 题/天`)}
    ${tile(`${ahead ? '+' : '−'}${pcFmt(Math.abs(delta))}`, ahead ? '超前' : '落后',
           `约 ${pcFmt(Math.abs(aheadDays))} 天`, ahead ? 'ahead' : 'behind')}
    ${tile(pcFmt(needPer), '剩下要的节奏 题/天', `还剩 ${leftDays} 天 · 还差 ${total - now} 题`)}
  </div>`;

  return head(`<div class="pc-head">${tabs}
      <span class="hint">阶段 ${ph.n}「${esc(ph.name)}」${esc(ph.from.slice(5))} – ${esc(ph.to.slice(5))}
        · 共 ${span} 天 · 历史自 ${esc(firstDay)}${lastDay < todayStr() ? '(日志最后一天 ' + esc(lastDay) + ')' : ''}</span></div>
    ${tiles}${svg}
    <div class="pc-legend">
      <span class="pc-key"><i class="k-plan"></i>计划（剩下的均摊到每天）</span>
      <span class="pc-key"><i class="k-act"></i>实际（edits.jsonl 逐日回放）</span>
      <span class="pc-key"><i class="k-gap ${ahead ? 'ahead' : 'behind'}"></i>今天的差额</span>
    </div>`);
}

// EDITS 是懒加载的(📈 进度那边也用它)。首屏先出格子, 历史拉回来再补这一段。
async function renderPace() {
  if (!$('#gr-pace')) return;
  if (EDITS === null) {
    try { EDITS = (await api('/api/edits')).edits || []; } catch { EDITS = []; }
  }
  const box = $('#gr-pace');            // 等待期间可能已经重画/切走了, 重新拿一次
  if (!box) return;
  box.innerHTML = paceHTML();
  box.querySelectorAll('[data-pace]').forEach((b) =>
    b.addEventListener('click', () => { PACE_SEL = b.dataset.pace; renderPace(); }));
}

async function switchView(v) {
  VIEW = v;
  document.querySelectorAll('.view-tab').forEach((b) => b.classList.toggle('active', b.dataset.view === v));
  $('#panel').classList.toggle('hidden', v !== 'board');
  $('#grid-view').classList.toggle('hidden', v !== 'grid');
  // 按结构/按范式、熟练度筛选只对矩阵视图有意义
  $('#groupby').classList.toggle('hidden', v !== 'board');
  $('#fam-filter').classList.toggle('hidden', v !== 'board');
  try { localStorage.setItem('lc-view2', v); } catch (e) { /* private mode */ }
  if (v === 'grid') {
    if (!PLAN) PLAN = await api('/api/plan');
    buildGrid();
  } else {
    buildPanel();
  }
}

async function reload() {
  PROBLEMS = await api('/api/problems');
  // 语法牌组拉失败不能连累看板(只读站没导出这个文件时就会走到这) —— 空数组即可,
  // 队列自然是 0, 徽章上只剩题目那边的数字。
  try {
    SYNTAX = (await api('/api/syntax')).cards || [];
  } catch { SYNTAX = []; }
  SYNTAX.forEach((c, i) => { c.ord = i; });   // 书写顺序, 给「题号」那档排序用
  buildPanel();
  if (VIEW === 'grid') buildGrid();   // buildPanel 占了 #count / #sub，还回来
  loadTodo();                          // 刷新 📋 TODO 上的角标
  updateReviewBadge();                 // 🧠 复习上的到期数
}

// 正文(trick 文档 / 笔记 / 题解)里的题号链接 —— 详情浮层直接盖在当前浮层上面,
// 关掉就回到原来读的地方, 不丢上下文。文档里的数字怎么变成链接见 linkifyPids。
document.addEventListener('click', (e) => {
  const a = e.target.closest('a.pid');
  if (!a) return;
  e.preventDefault();
  openDetail(+a.dataset.pid);
});

// ---- wire global controls ----
on('#sync', 'click', async () => { await fetch('/api/sync', { method: 'POST' }); reload(); });
document.querySelectorAll('.view-tab').forEach((b) =>
  b.addEventListener('click', () => switchView(b.dataset.view)));
on('#grid-view', 'click', (e) => {
  const doc = e.target.closest('.gr-doc');
  if (doc) return void openDoc(doc.dataset.kind, doc.dataset.tag);
  const jump = e.target.closest('[data-jump]');
  if (jump) {
    const el = document.getElementById(`gr-tier-${jump.dataset.jump}`);
    if (el) el.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' });
    return;
  }
  const chip = e.target.closest('.gr-chip');
  if (!chip) return;
  const id = +chip.dataset.id;
  // 还没建文件夹的题, 整个 chip 都是"开始这道题"; 建过的, 只有徽章翻熟练度。
  if (!byId().get(id)) return void startProblem(id, chip);
  if (e.target.closest('.gr-st')) return void cycleL(id);
  openDetail(id);
});
on('#close', 'click', closeDetail);
on('#save-note', 'click', () => { saveNote(); exitEdit(); });
on('#note-preview', 'dblclick', enterEdit);
on('#sol-code', 'dblclick', enterSolEdit);
on('#sol-save', 'click', () => exitSolEdit(true));
on('#sol-edit', 'blur', () => exitSolEdit(true));  // 点开 = 保存 + 回高亮
on('#note-edit', 'blur', () => exitEdit(true));   // click away = save + render
on('#e-difficulty', 'change', autoSaveMeta);
on('#e-status', 'change', autoSaveMeta);
on('#e-familiarity', 'change', autoSaveMeta);

// chip editor: remove on ✕, add on Enter/comma, delete-last on Backspace
document.addEventListener('click', (e) => {
  const x = e.target.closest('.ce-x');
  if (x) removeTag(x.closest('.chipfield').dataset.field, +x.dataset.i);
});
document.addEventListener('keydown', (e) => {
  // 复习面板的快捷键归 Vue 那边管(RV.onKey), 这里只负责把事件转过去 ——
  // 分发顺序留在这个全局 handler 里, 才能保证复习的 Ctrl+S 抢在下面通用 Ctrl+S 之前。
  if (RV.open && RV.onKey(e)) { e.preventDefault(); e.stopPropagation(); return; }
  const inp = e.target.closest('.ce-input');
  if (!inp) return;
  const field = inp.dataset.field;
  if (e.key === 'Enter' || e.key === ',' || e.key === '，') {
    e.preventDefault();
    if (inp.value.trim()) addTag(field, inp.value); inp.value = '';
  } else if (e.key === 'Backspace' && !inp.value && TAGS[field].length) {
    removeTag(field, TAGS[field].length - 1);
  }
});

// 从 datalist 里点中一项就直接成 chip, 不用再按一次 Enter。
// 浏览器给这种"替换式输入"打的 inputType 是 insertReplacementText(老版本给 undefined),
// 手打是 insertText —— 所以正常打字打到和某个建议一模一样时不会被抢走。
document.addEventListener('input', (e) => {
  const inp = e.target.closest('.ce-input');
  if (!inp || !SUGGEST.has(inp.dataset.field)) return;
  if (e.inputType && e.inputType !== 'insertReplacementText') return;
  const v = inp.value.trim();
  const dl = document.getElementById(`ce-sug-${inp.dataset.field}`);
  if (!v || !dl || ![...dl.options].some((o) => o.value === v)) return;
  inp.value = '';
  addTag(inp.dataset.field, v);
});

document.addEventListener('click', closeFamMenu);
addEventListener('resize', closeFamMenu);
addEventListener('scroll', closeFamMenu, true);

on('#overlay', 'click', (e) => { if (e.target.id === 'overlay') closeDetail(); });

// 分组维度切换: 结构 <-> 范式
document.querySelectorAll('.gb-btn').forEach((b) =>
  b.addEventListener('click', () => {
    GROUP_BY = b.dataset.by;
    document.querySelectorAll('.gb-btn').forEach((x) => x.classList.toggle('on', x === b));
    buildPanel();
  })
);

// todo popover controls
on('#open-todo', 'click', (e) => { e.stopPropagation(); toggleTodoPop(); });
on('#todo-pop', 'click', (e) => e.stopPropagation());
on('#todo-in', 'keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addTodo(); }
});
document.addEventListener('click', closeTodoPop);      // 点别处收起

// notes overlay controls
on('#open-review', 'click', () => RV.start());   // 面板内部的交互全在 Vue 模板里
on('#open-stats', 'click', openStats);
on('#stats-close', 'click', closeStats);
on('#stats-overlay', 'click', (e) => { if (e.target.id === 'stats-overlay') closeStats(); });
on('#open-lists', 'click', openLists);
on('#lists-close', 'click', closeLists);
on('#lists-overlay', 'click', (e) => { if (e.target.id === 'lists-overlay') closeLists(); });
on('#open-notes', 'click', () => openNotes());
on('#notes-close', 'click', closeNotes);
on('#note-new', 'click', newNote);
on('#nt-save', 'click', () => { saveNoteFile(); exitNoteEdit(); });
on('#nt-preview', 'dblclick', enterNoteEdit);
on('#nt-edit', 'blur', () => exitNoteEdit(true));
on('#scratch-in', 'keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addScratch(); }
});
on('#notes-overlay', 'click', (e) => {
  if (e.target.id === 'notes-overlay') closeNotes();
});

// structure-doc overlay controls
on('#doc-close', 'click', closeDoc);
on('#doc-save', 'click', () => { saveDoc(); exitDocEdit(); });
on('#doc-preview', 'dblclick', enterDocEdit);
on('#doc-edit', 'blur', () => exitDocEdit(true));
on('#doc-overlay', 'click', (e) => { if (e.target.id === 'doc-overlay') closeDoc(); });

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    if (NOTE) { e.preventDefault(); saveNoteFile(); return; }
    if (DOC) { e.preventDefault(); saveDoc(); return; }
    if (CURRENT) {
      e.preventDefault();
      // 光标在哪个 pane 就存哪个: 代码区编辑中优先, 否则还是存笔记
      if (SOL_EDITING) { saveSol($('#sol-edit').value); return; }
      saveNote();
      return;
    }
  }
  if (e.key === 'Escape') {
    if (!$('#todo-pop').classList.contains('hidden')) { closeTodoPop(); return; }
    if (document.querySelector('.fam-menu')) { closeFamMenu(); return; }
    if (RV.open) { RV.onEsc(); return; }
    if (statsOpen()) { closeStats(); return; }
    if (!$('#lists-overlay').classList.contains('hidden')) { closeLists(); return; }
    // 详情浮层永远在最上面(#overlay 的 z-index 比别的浮层高一档), 所以先退它 ——
    // 从 trick 文档里点题号进来的场景, Esc 一下回到文档, 再一下才关文档。
    if (CURRENT) {
      if (SOL_EDITING) { exitSolEdit(true); return; }
      EDITING ? exitEdit(true) : closeDetail();
      return;
    }
    if (NOTE) { NOTE_EDITING ? exitNoteEdit(true) : closeNotes(); return; }
    if (DOC) { DOC_EDITING ? exitDocEdit(true) : closeDoc(); return; }
  }
});

// 默认落在坐标系: 首页要先回答"我现在在哪、下一步练什么", 矩阵是查题的第二跳。
// 键从 lc-view 换成 lc-view2 是一次性迁移 —— 老浏览器里存着的 'board' 不该把
// 新默认值顶掉, 换个键等于所有人重新按新默认开一次, 之后再记各自的选择。
let startView = 'grid';
try { startView = localStorage.getItem('lc-view2') || 'grid'; } catch (e) { /* private mode */ }
reload().then(() => switchView(startView));
