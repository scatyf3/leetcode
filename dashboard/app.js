'use strict';
const $ = (s) => document.querySelector(s);
const api = (u, opt) => fetch(u, opt).then((r) => r.json());

let PROBLEMS = [];
let CURRENT = null; // detail object

// ---- board: cluster by data structure, cards carry trick tags ----
const NO_STRUCT = '未分类';

function buildPanel() {
  const groups = new Map();            // structure -> [problems]
  for (const p of PROBLEMS) {
    const keys = p.structures.length ? p.structures : [NO_STRUCT];
    for (const k of keys) (groups.get(k) || groups.set(k, []).get(k)).push(p);
  }
  const nStruct = [...groups.keys()].filter((k) => k !== NO_STRUCT).length;
  $('#count').textContent = `${PROBLEMS.length} 题 · ${nStruct} 类`;

  // sort columns alphabetically, 未分类 always last
  const order = [...groups.keys()].sort((a, b) =>
    a === NO_STRUCT ? 1 : b === NO_STRUCT ? -1 : a.localeCompare(b));

  if (!PROBLEMS.length) {
    $('#panel').innerHTML = `<p class="empty-hint">还没有题目。建一个「编号. 标题」文件夹后点 ↻ Sync。</p>`;
    return;
  }

  let h = '<div class="groups">';
  for (const g of order) {
    const items = groups.get(g).slice().sort((a, b) => a.id - b.id);
    const openable = g !== NO_STRUCT;
    h += `<div class="group">
      <div class="group-label${openable ? ' openable' : ''}"${openable ? ` data-struct="${esc(g)}" title="打开 ${esc(g)} 通用 trick 文档"` : ''}>
        <span class="group-name">${esc(g)}</span>
        <span class="group-count">${items.length}</span>
        ${openable ? '<span class="group-open">通用 trick →</span>' : ''}</div>
      <div class="group-rows">${items.map(rowHTML).join('')}</div>
    </div>`;
  }
  h += '</div>';
  $('#panel').innerHTML = h;
  wireCards();
}

function rowHTML(p) {
  const diff = p.difficulty || 'none';
  const todo = p.status === 'todo' ? ' todo' : '';
  const paras = p.paradigms.map((x) => `<span class="tag para">${esc(x)}</span>`).join('');
  const tricks = p.techniques.map((x) => `<span class="tag trick">${esc(x)}</span>`).join('');
  return `<div class="row${todo}" data-id="${p.id}">
    <span class="dot ${diff}" title="${diff}"></span>
    <span class="row-id">#${p.id}</span>
    <span class="row-title">${esc(p.title)}</span>
    <span class="row-tags">${paras}${tricks}</span>
  </div>`;
}

function wireCards() {
  document.querySelectorAll('.row').forEach((el) =>
    el.addEventListener('click', () => openDetail(+el.dataset.id))
  );
  document.querySelectorAll('.group-label.openable').forEach((el) =>
    el.addEventListener('click', () => openDoc(el.dataset.struct))
  );
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
  $('#note-file').textContent = d.note_file;
  $('#note-edit').value = d.note;
  $('#note-msg').textContent = '';
  $('#meta-msg').textContent = '改动自动保存';
  exitEdit();                 // always open in rendered (preview) mode
  buildSolTabs(d.solutions);
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

let activeSol = 0;
function buildSolTabs(sols) {
  const tabs = $('#sol-tabs');
  if (!sols.length) {
    tabs.innerHTML = '';
    $('#sol-code').firstChild.textContent = '(没有 .py 文件)';
    return;
  }
  activeSol = 0;
  tabs.innerHTML = sols
    .map((s, i) => `<span class="tab${i === 0 ? ' active' : ''}" data-i="${i}">${esc(s.name)}</span>`)
    .join('');
  tabs.querySelectorAll('.tab').forEach((t) =>
    t.addEventListener('click', () => {
      activeSol = +t.dataset.i;
      tabs.querySelectorAll('.tab').forEach((x) => x.classList.toggle('active', x === t));
      showCode(sols[activeSol]);
    })
  );
  showCode(sols[0]);
}

function showCode(sol) {
  // highlight python; fall back to plain escaped text for other extensions
  $('#sol-code').firstChild.innerHTML = sol.name.endsWith('.py')
    ? highlightPython(sol.content)
    : esc(sol.content);
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

async function openDoc(name) {
  DOC = await api('/api/structures/' + encodeURIComponent(name));
  $('#doc-title').textContent = DOC.name;
  $('#doc-file').textContent = 'structures/' + DOC.file;
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
    : '<p style="color:var(--dim)">（还没有内容 — 双击这里开始写这个结构的通用 trick）</p>';
  $('#doc-edit').classList.add('hidden');
  $('#doc-save').classList.add('hidden');
  $('#doc-preview').classList.remove('hidden');
  $('#doc-mode').textContent = '双击渲染区编辑';
}

async function saveDoc() {
  const content = $('#doc-edit').value;
  await fetch('/api/structures/' + encodeURIComponent(DOC.name), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  DOC.content = content;
  $('#doc-msg').textContent = '已保存 ✓';
  setTimeout(() => { if ($('#doc-msg')) $('#doc-msg').textContent = '改动自动保存'; }, 1500);
}

function closeDoc() { $('#doc-overlay').classList.add('hidden'); DOC = null; }

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
      .replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  while (i < lines.length) {
    let l = lines[i];
    if (/^```/.test(l)) {
      const buf = []; i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      i++; out.push(`<pre><code>${esc(buf.join('\n'))}</code></pre>`); continue;
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
    while (i < lines.length && lines[i].trim() !== '' && !/^(#{1,6}\s|```|\s*[-*+]\s|\s*\d+\.\s|\s*>|\s*\|)/.test(lines[i]))
      buf.push(lines[i++]);
    out.push(`<p>${inline(buf.join(' '))}</p>`);
  }
  return out.join('\n');
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

async function reload() {
  PROBLEMS = await api('/api/problems');
  buildPanel();
}

// ---- wire global controls ----
$('#sync').addEventListener('click', async () => { await fetch('/api/sync', { method: 'POST' }); reload(); });
$('#close').addEventListener('click', closeDetail);
$('#save-note').addEventListener('click', () => { saveNote(); exitEdit(); });
$('#note-preview').addEventListener('dblclick', enterEdit);
$('#note-edit').addEventListener('blur', () => exitEdit(true));   // click away = save + render
$('#e-difficulty').addEventListener('change', autoSaveMeta);
$('#e-status').addEventListener('change', autoSaveMeta);

// chip editor: remove on ✕, add on Enter/comma, delete-last on Backspace
document.addEventListener('click', (e) => {
  const x = e.target.closest('.ce-x');
  if (x) removeTag(x.closest('.chipfield').dataset.field, +x.dataset.i);
});
document.addEventListener('keydown', (e) => {
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

$('#overlay').addEventListener('click', (e) => { if (e.target.id === 'overlay') closeDetail(); });

// structure-doc overlay controls
$('#doc-close').addEventListener('click', closeDoc);
$('#doc-save').addEventListener('click', () => { saveDoc(); exitDocEdit(); });
$('#doc-preview').addEventListener('dblclick', enterDocEdit);
$('#doc-edit').addEventListener('blur', () => exitDocEdit(true));
$('#doc-overlay').addEventListener('click', (e) => { if (e.target.id === 'doc-overlay') closeDoc(); });

document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    if (DOC) { e.preventDefault(); saveDoc(); return; }
    if (CURRENT) { e.preventDefault(); saveNote(); return; }
  }
  if (e.key === 'Escape') {
    if (DOC) { DOC_EDITING ? exitDocEdit(true) : closeDoc(); return; }
    if (CURRENT) { EDITING ? exitEdit(true) : closeDetail(); return; }
  }
});

reload();
