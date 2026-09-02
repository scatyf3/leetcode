'use strict';
const $ = (s) => document.querySelector(s);
const api = (u, opt) => fetch(u, opt).then((r) => r.json());

let PROBLEMS = [];
let CURRENT = null; // detail object

// ---- familiarity (熟练度): 1 熟 → 4 完全不会, 0 = 未评 ----
const FAM = {
  0: { short: '—',  label: '未评' },
  1: { short: 'L1', label: '已经熟悉' },
  2: { short: 'L2', label: '思路会 · 细节易写错' },
  3: { short: 'L3', label: '思路大概知道 · 不熟' },
  4: { short: 'L4', label: '思路都不知道' },
};
let FAM_FILTER = new Set();          // empty = 不过滤
const famOf = (p) => Number(p.familiarity) || 0;

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

  let h = `<div class="fam-legend">${[1, 2, 3, 4]
    .map((f) => `<span class="fam f${f}">${FAM[f].short}</span>${esc(FAM[f].label)}`)
    .join('<span class="sep">·</span>')}</div>`;
  h += '<div class="groups">';
  for (const g of order) {
    const items = groups.get(g).slice().sort((a, b) => a.id - b.id);
    const openable = g !== NO_STRUCT;
    h += `<div class="group">
      <div class="group-label${openable ? ' openable' : ''}"${openable ? ` data-struct="${esc(g)}" title="打开 ${esc(g)} 通用 trick 文档"` : ''}>
        <span class="group-name">${esc(g)}</span>
        <span class="group-count">${items.length} 题</span>
        ${openable ? '<span class="group-open">通用 trick →</span>' : ''}</div>
      <div class="group-rows">${items.map(rowHTML).join('')}</div>
    </div>`;
  }
  h += '</div>';
  $('#panel').innerHTML = h;
  wireCards();
}

function buildFamFilter() {
  const counts = new Map([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]);
  for (const p of PROBLEMS) counts.set(famOf(p), (counts.get(famOf(p)) || 0) + 1);
  $('#fam-filter').innerHTML = [1, 2, 3, 4, 0]
    .filter((f) => counts.get(f))                   // hide buckets nobody is in
    .map((f) => `<button class="fam-btn f${f}${FAM_FILTER.has(f) ? ' on' : ''}"
        data-fam="${f}" title="${esc(FAM[f].label)}">${FAM[f].short}
        <span class="fam-n">${counts.get(f)}</span></button>`)
    .join('');
  document.querySelectorAll('.fam-btn').forEach((b) =>
    b.addEventListener('click', () => {
      const f = +b.dataset.fam;
      FAM_FILTER.has(f) ? FAM_FILTER.delete(f) : FAM_FILTER.add(f);
      buildPanel();
    })
  );
}

function rowHTML(p) {
  const diff = p.difficulty || 'none';
  const todo = p.status === 'todo' ? ' todo' : '';
  // 行尾展示的是"另一个维度": 按结构分组时显示范式, 按范式分组时显示结构
  const paras = p[otherDim()].map((x) => `<span class="tag para">${esc(x)}</span>`).join('');
  const tricks = p.techniques.map((x) => `<span class="tag trick">${esc(x)}</span>`).join('');
  const f = famOf(p);
  return `<div class="row${todo}" data-id="${p.id}">
    <span class="dot ${diff}" title="${diff}"></span>
    <span class="fam f${f}" data-id="${p.id}" title="点击改熟练度 (当前: ${esc(FAM[f].label)})">${FAM[f].short}</span>
    <span class="row-id">#${p.id}</span>
    <span class="row-title">${esc(p.title)}</span>
    <span class="row-tags">${paras}${tricks}</span>
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
  menu.innerHTML = [1, 2, 3, 4, 0]
    .map((f) => `<button class="fam-opt${f === cur ? ' on' : ''}" data-f="${f}">
        <span class="fam f${f}">${FAM[f].short}</span>${esc(FAM[f].label)}</button>`)
    .join('');
  document.body.appendChild(menu);

  const r = badge.getBoundingClientRect();
  menu.style.left = `${Math.min(r.left, innerWidth - menu.offsetWidth - 10)}px`;
  menu.style.top = `${r.bottom + 4 + menu.offsetHeight > innerHeight
    ? r.top - menu.offsetHeight - 4 : r.bottom + 4}px`;   // 贴着窗口下沿时朝上开

  menu.querySelectorAll('.fam-opt').forEach((b) =>
    b.addEventListener('click', (e) => { e.stopPropagation(); setFam(id, +b.dataset.f); })
  );
}

async function setFam(id, f) {
  closeFamMenu();
  await fetch(`/api/problems/${id}/meta`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ familiarity: f }),      // 只发这一个字段, 其它标签原样保留
  });
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
  $('#e-familiarity').value = String(famOf(d));
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

function renderChips() {
  for (const field of ['structures', 'paradigms', 'techniques']) {
    const box = document.querySelector(`.chipfield[data-field="${field}"]`);
    box.innerHTML =
      TAGS[field].map((t, i) =>
        `<span class="ce-chip ${field}">${esc(t)}<button class="ce-x" data-i="${i}" title="删除">×</button></span>`
      ).join('') +
      `<input class="ce-input" data-field="${field}" placeholder="+ tag">`;
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
    familiarity: +$('#e-familiarity').value,
  };
  await fetch(`/api/problems/${CURRENT.id}/meta`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  $('#meta-msg').textContent = '已保存 ✓';
  await reloadKeepOpen();
}

// reload the board data without disturbing the open detail modal
async function reloadKeepOpen() {
  PROBLEMS = await api('/api/problems');
  buildPanel();
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
  $('#doc-title').textContent = DOC.name;
  $('#doc-file').textContent = DOC.file;
  $('#doc-edit').value = DOC.content;
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

// ---- tiny markdown renderer (headings/lists/tables/code/inline) ----
function md(src) {
  const lines = src.replace(/\r/g, '').split('\n');
  let out = [], i = 0;
  const inline = (t) =>
    esc(t)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*\w])\*(\S(?:[^*]*\S)?)\*/g, '$1<em>$2</em>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  while (i < lines.length) {
    let l = lines[i];
    if (/^\s*```/.test(l)) {                 // fence 可以缩进(列表项里的代码块)
      const buf = []; i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) buf.push(lines[i++]);
      i++;
      const pad = Math.min(...buf.filter((x) => x.trim())
        .map((x) => x.match(/^ */)[0].length), Infinity);
      const body = buf.map((x) => (pad === Infinity ? x : x.slice(pad))).join('\n');
      out.push(`<pre><code>${esc(body)}</code></pre>`); continue;
    }
    let m = l.match(/^(#{1,6})\s+(.*)/);
    if (m) { out.push(`<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`); i++; continue; }
    if (/^\s*>/.test(l)) {
      const buf = [];
      while (i < lines.length && /^\s*>/.test(lines[i])) buf.push(lines[i++].replace(/^\s*>\s?/, ''));
      out.push(`<blockquote>${inline(buf.join(' '))}</blockquote>`); continue;
    }
    if (/^\s*\|.*\|/.test(l) && i + 1 < lines.length && /^\s*\|[-:\s|]+\|/.test(lines[i + 1])) {
      const row = (s) => s.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const head = row(l); i += 2;
      let body = '';
      while (i < lines.length && /^\s*\|.*\|/.test(lines[i])) {
        body += '<tr>' + row(lines[i++]).map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>';
      }
      out.push(`<table><thead><tr>${head.map((c) => `<th>${inline(c)}</th>`).join('')}</tr></thead><tbody>${body}</tbody></table>`);
      continue;
    }
    if (/^\s*[-*+]\s+/.test(l)) {
      const buf = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i]))
        buf.push(`<li>${inline(lines[i++].replace(/^\s*[-*+]\s+/, ''))}</li>`);
      out.push(`<ul>${buf.join('')}</ul>`); continue;
    }
    if (/^\s*\d+\.\s+/.test(l)) {
      const buf = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i]))
        buf.push(`<li>${inline(lines[i++].replace(/^\s*\d+\.\s+/, ''))}</li>`);
      out.push(`<ol>${buf.join('')}</ol>`); continue;
    }
    if (l.trim() === '') { i++; continue; }
    const buf = [];
    while (i < lines.length && lines[i].trim() !== '' && !/^(#{1,6}\s|\s*```|\s*[-*+]\s|\s*\d+\.\s|\s*>|\s*\|)/.test(lines[i]))
      buf.push(lines[i++]);
    out.push(`<p>${inline(buf.join(' '))}</p>`);
  }
  return out.join('\n');
}

// ---- 🧠 FSRS 复习: 看题面 -> 心里过思路 -> 揭晓 -> 1-4 自评 --------------------
// 调度状态在各题 meta.json 的 fsrs 字段里, 算法在 dashboard/fsrs.py。
// 和 familiarity(L1-L4) 是**两套独立的东西**: 这里只管"什么时候再问一次",
// familiarity 仍然是手工维护的掌握档位, 复习不会去改它。
let REVIEW = null;          // {queue:[id], done, total, revealed, d, items, active}
const isReadOnly = () => document.documentElement.classList.contains('ro');

const todayStr = () => new Date().toLocaleDateString('sv');   // 本地 YYYY-MM-DD
const isCard = (p) => !!p.due;
const isDue = (p) => isCard(p) && p.due <= todayStr();
const rvEligible = (p) => p.status === 'solved' || p.status === 'review';
const FAM_ORDER = { 4: 0, 3: 1, 2: 2, 0: 3, 1: 4 };            // 越生的越先进队列

function buildQueue() {
  const due = PROBLEMS.filter(isDue).sort((a, b) =>
    (a.status === 'review' ? 0 : 1) - (b.status === 'review' ? 0 : 1) ||
    a.due.localeCompare(b.due) || a.id - b.id);
  // 还没成为卡片的题, 按熟练度从生到熟排 —— 只是**读** familiarity 定顺序, 不写它
  const fresh = PROBLEMS.filter((p) => rvEligible(p) && !isCard(p)).sort((a, b) =>
    FAM_ORDER[famOf(a)] - FAM_ORDER[famOf(b)] || a.id - b.id);
  return [...due, ...fresh].map((p) => p.id);
}

function updateReviewBadge() {
  const n = buildQueue().length;
  $('#review-n').textContent = n;
  $('#review-n').classList.toggle('hidden', !n);
}

function fmtInterval(days) {
  if (days <= 0) return '今天';
  if (days === 1) return '明天';
  if (days < 30) return `${days} 天`;
  if (days < 365) return `${(days / 30).toFixed(1)} 个月`;
  return `${(days / 365).toFixed(1)} 年`;
}

async function openReview() {
  const queue = buildQueue();
  REVIEW = { queue, done: 0, total: queue.length, revealed: false, d: null, items: [], active: 0 };
  $('#review-overlay').classList.remove('hidden');
  nextCard();
}

function closeReview() {
  $('#review-overlay').classList.add('hidden');
  REVIEW = null;
}

async function nextCard() {
  if (!REVIEW) return;
  const id = REVIEW.queue.shift();
  if (id === undefined) return showRvEmpty();
  $('#rv-empty').classList.add('hidden');
  $('#rv-card').classList.remove('hidden');
  $('.rv-foot').classList.remove('hidden');
  REVIEW.d = await api(`/api/problems/${id}`);
  REVIEW.revealed = false;
  renderQuestion();
}

function showRvEmpty() {
  const done = REVIEW ? REVIEW.done : 0;
  $('#rv-card').classList.add('hidden');
  $('.rv-foot').classList.add('hidden');
  $('#rv-id').textContent = '';
  $('#rv-title').textContent = '';
  $('#rv-meta').textContent = '';
  $('#rv-progress').textContent = '';
  $('#rv-empty').classList.remove('hidden');
  $('#rv-empty').innerHTML = done
    ? `这一轮复习完了 —— 共 ${done} 道 🎉<br><span class="hint">下次到期时间已经按 FSRS 排好, 徽章上的数字会自己变</span>`
    : '今天没有到期的题 🎉<br><span class="hint">status 是 solved / review 的题才会进复习队列</span>';
}

// 只渲染题面。绝不碰 d.note / d.solutions —— 剧透了这个功能就没意义了
function renderQuestion() {
  const d = REVIEW.d;
  $('#rv-id').textContent = d.id;
  $('#rv-title').textContent = d.title;
  const reps = d.fsrs && d.fsrs.reps ? `第 ${d.fsrs.reps + 1} 次复习` : '第一次进复习';
  $('#rv-meta').textContent = `${d.difficulty || '?'} · ${reps}`;
  $('#rv-progress').textContent = `${REVIEW.done + 1} / ${REVIEW.total}`;
  $('#rv-desc').innerHTML = d.description
    || '<p class="hint">这题没有抓到题面(problem.html 是空的)。只能靠标题回忆 —— 或者跑 dashboard/fetch_desc.py 补抓。</p>';
  $('#rv-card').scrollTop = 0;
  $('#rv-answer').classList.add('hidden');
  $('#rv-reveal').classList.remove('hidden');
  $('#rv-rate').classList.add('hidden');
  $('#rv-rate').innerHTML = '';
}

function revealAnswer() {
  if (!REVIEW || REVIEW.revealed) return;
  REVIEW.revealed = true;
  const d = REVIEW.d;
  REVIEW.items = [{ name: '📝 笔记', md: d.note || '_(还没写笔记)_' },
                  ...d.solutions.map((x) => ({ name: x.name, code: x.content }))];
  renderRvTabs(0);
  $('#rv-answer').classList.remove('hidden');
  $('#rv-reveal').classList.add('hidden');

  const pv = d.fsrs_preview || {};
  const LABEL = { 1: ['忘了', '想不起来'], 2: ['勉强', '想了很久'], 3: ['想起来了', '正常'], 4: ['很熟', '秒答'] };
  $('#rv-rate').innerHTML = [1, 2, 3, 4].map((r) => `
    <button class="rv-btn" data-r="${r}">
      <b>${LABEL[r][0]}</b><i>${fmtInterval(pv[r] ?? 0)}</i><u>${r} · ${LABEL[r][1]}</u>
    </button>`).join('');
  $('#rv-rate').classList.remove('hidden');
  $('#rv-rate').querySelectorAll('.rv-btn').forEach((el) =>
    el.addEventListener('click', () => rate(+el.dataset.r)));
}

function renderRvTabs(i) {
  REVIEW.active = i;
  $('#rv-tabs').innerHTML = REVIEW.items
    .map((x, k) => `<button class="tab${k === i ? ' on' : ''}" data-i="${k}">${esc(x.name)}</button>`)
    .join('');
  $('#rv-tabs').querySelectorAll('.tab').forEach((el) =>
    el.addEventListener('click', () => renderRvTabs(+el.dataset.i)));
  const item = REVIEW.items[i];
  $('#rv-body').innerHTML = item.code !== undefined
    ? `<pre><code>${highlightPython(item.code)}</code></pre>`
    : md(item.md);
}

async function rate(r) {
  if (!REVIEW || !REVIEW.revealed) return;
  const id = REVIEW.d.id;
  let res;
  try {
    res = await api(`/api/review/${id}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating: r }),
    });
  } catch { res = null; }
  if (!res || !res.ok) {
    // 只读站的 403 也走这里(static-shim 是 resolve 不是 reject)。写失败就**不推进**——
    // 假装评过了会让这道题的调度悄悄丢一次, 比停下来更糟。
    $('#rv-meta').textContent = '⚠ 没记录下来(只读站或服务没起) —— 按「下一题」继续自测';
    return;
  }
  {
    const p = PROBLEMS.find((x) => x.id === id);
    if (p) {
      p.due = res.card.due; p.reps = res.card.reps; p.stability = res.card.stability;
      p.last_review = res.card.last_review; p.fsrs_state = res.card.state;
    }
    if (r === 1) { REVIEW.queue.push(id); REVIEW.total++; }   // 忘了 -> 本次会话末尾再问一遍
    buildPanel();
    updateReviewBadge();
  }
  REVIEW.done++;
  nextCard();
}

// ---- 📊 题单覆盖率: dashboard/lists.json 是定义, 进度拿 PROBLEMS 现算 -------
// 定义里有仓库还没有的题(那才是缺口的意义), 所以不能只靠 meta.json 反推。
let LISTS = null;          // {lists: {名字: {source, note, categories}}, premium: [id]}
let LIST_CUR = null;       // 当前看的是哪个题单

// 一题在题单里的档位: 1..4 = 熟练度, 0 = 建了但没评, -1 = 仓库里压根没有
const listFam = (id) => {
  const p = PROBLEMS.find((x) => x.id === id);
  return p ? famOf(p) : -1;
};
const LBUCKETS = [1, 2, 3, 4, 0];                 // 进度条从"最熟"到"最生", 未做是剩下的空白

function barHTML(items) {
  const n = items.length || 1;
  const c = { 1: 0, 2: 0, 3: 0, 4: 0, 0: 0, '-1': 0 };
  for (const [id] of items) c[listFam(id)]++;
  const tip = LBUCKETS.map((f) => `${f ? FAM[f].short : '未评'} ${c[f]}`).join(' · ')
    + ` · 未做 ${c['-1']} · 共 ${items.length}`;
  const seg = LBUCKETS
    .filter((f) => c[f])
    .map((f) => `<i class="f${f}" style="width:${(100 * c[f] / n).toFixed(2)}%"></i>`)
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
    const label = f === -1 ? '未做' : f ? FAM[f].label : '未评';
    const short = f === -1 ? '·' : f ? FAM[f].short : '—';
    return `<span class="lkey f${f}"><i></i>${esc(short)} ${esc(label)} <b>${top.counts[f]}</b></span>`;
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
        const badge = f > 0 ? `<i class="lfam f${f}">${FAM[f].short}</i>` : '';
        const act = f === -1
          ? ` data-add="${id}" title="点一下建文件夹并抓题面"`
          : ` data-open="${id}" title="${esc(title)} · ${f ? FAM[f].label : '未评熟练度'}"`;
        return `<span class="lchip f${f}"${act}>${badge}${id}${star} <em>${esc(title)}</em></span>`;
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
    r = await api('/api/problems', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: String(id) }),
    });
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
    r = await api('/api/problems', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
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

async function reload() {
  PROBLEMS = await api('/api/problems');
  buildPanel();
  loadTodo();                          // 刷新 📋 TODO 上的角标
  updateReviewBadge();                 // 🧠 复习上的到期数
}

// ---- wire global controls ----
$('#sync').addEventListener('click', async () => { await fetch('/api/sync', { method: 'POST' }); reload(); });
$('#close').addEventListener('click', closeDetail);
$('#save-note').addEventListener('click', () => { saveNote(); exitEdit(); });
$('#note-preview').addEventListener('dblclick', enterEdit);
$('#sol-code').addEventListener('dblclick', enterSolEdit);
$('#sol-save').addEventListener('click', () => exitSolEdit(true));
$('#sol-edit').addEventListener('blur', () => exitSolEdit(true));  // 点开 = 保存 + 回高亮
$('#note-edit').addEventListener('blur', () => exitEdit(true));   // click away = save + render
$('#e-difficulty').addEventListener('change', autoSaveMeta);
$('#e-status').addEventListener('change', autoSaveMeta);
$('#e-familiarity').addEventListener('change', autoSaveMeta);

// chip editor: remove on ✕, add on Enter/comma, delete-last on Backspace
document.addEventListener('click', (e) => {
  const x = e.target.closest('.ce-x');
  if (x) removeTag(x.closest('.chipfield').dataset.field, +x.dataset.i);
});
document.addEventListener('keydown', (e) => {
  // 复习模式的单键快捷键。这个全局 handler 原本只处理 Ctrl+S / Esc, 没有任何输入框保护,
  // 所以这里必须自己挡: 输入框内、组合键、以及中文输入法组字中(isComposing / 229)。
  if (REVIEW && !e.ctrlKey && !e.metaKey && !e.altKey && !e.isComposing && e.keyCode !== 229
      && !/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) {
    if (e.key === ' ') {
      e.preventDefault();
      if (!REVIEW.revealed) revealAnswer();
      else if (isReadOnly()) nextCard();   // 只读站没有评分按钮, 空格 = 下一题
      // 本地站揭晓后不响应空格: 必须按 1-4, 防止手滑跳过一道没评分
      return;
    }
    if (REVIEW.revealed && '1234'.includes(e.key)) {
      e.preventDefault();
      rate(+e.key);
      return;
    }
  }
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

document.addEventListener('click', closeFamMenu);
addEventListener('resize', closeFamMenu);
addEventListener('scroll', closeFamMenu, true);

$('#overlay').addEventListener('click', (e) => { if (e.target.id === 'overlay') closeDetail(); });

// 分组维度切换: 结构 <-> 范式
document.querySelectorAll('.gb-btn').forEach((b) =>
  b.addEventListener('click', () => {
    GROUP_BY = b.dataset.by;
    document.querySelectorAll('.gb-btn').forEach((x) => x.classList.toggle('on', x === b));
    buildPanel();
  })
);

// todo popover controls
$('#open-todo').addEventListener('click', (e) => { e.stopPropagation(); toggleTodoPop(); });
$('#todo-pop').addEventListener('click', (e) => e.stopPropagation());
$('#todo-in').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addTodo(); }
});
document.addEventListener('click', closeTodoPop);      // 点别处收起

// notes overlay controls
$('#open-review').addEventListener('click', openReview);
$('#review-close').addEventListener('click', closeReview);
$('#review-overlay').addEventListener('click', (e) => { if (e.target.id === 'review-overlay') closeReview(); });
$('#rv-reveal').addEventListener('click', revealAnswer);
$('#rv-next').addEventListener('click', () => { REVIEW.done++; nextCard(); });  // 只读站用: 没有评分按钮
$('#open-lists').addEventListener('click', openLists);
$('#lists-close').addEventListener('click', closeLists);
$('#lists-overlay').addEventListener('click', (e) => { if (e.target.id === 'lists-overlay') closeLists(); });
$('#open-notes').addEventListener('click', () => openNotes());
$('#notes-close').addEventListener('click', closeNotes);
$('#note-new').addEventListener('click', newNote);
$('#nt-save').addEventListener('click', () => { saveNoteFile(); exitNoteEdit(); });
$('#nt-preview').addEventListener('dblclick', enterNoteEdit);
$('#nt-edit').addEventListener('blur', () => exitNoteEdit(true));
$('#scratch-in').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addScratch(); }
});
$('#notes-overlay').addEventListener('click', (e) => {
  if (e.target.id === 'notes-overlay') closeNotes();
});

// structure-doc overlay controls
$('#doc-close').addEventListener('click', closeDoc);
$('#doc-save').addEventListener('click', () => { saveDoc(); exitDocEdit(); });
$('#doc-preview').addEventListener('dblclick', enterDocEdit);
$('#doc-edit').addEventListener('blur', () => exitDocEdit(true));
$('#doc-overlay').addEventListener('click', (e) => { if (e.target.id === 'doc-overlay') closeDoc(); });

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
    if (REVIEW) { closeReview(); return; }
    if (!$('#lists-overlay').classList.contains('hidden')) { closeLists(); return; }
    if (NOTE) { NOTE_EDITING ? exitNoteEdit(true) : closeNotes(); return; }
    if (DOC) { DOC_EDITING ? exitDocEdit(true) : closeDoc(); return; }
    if (CURRENT) {
      if (SOL_EDITING) { exitSolEdit(true); return; }
      EDITING ? exitEdit(true) : closeDetail();
      return;
    }
  }
});

reload();
