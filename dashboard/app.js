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

// ---- 坐标系 view: coverage (tier) × depth (stage) ----
// tier  = how far the题单 is spread (75 / 110 / 135)
// stage = how well each problem is held (S1 思路 / S2 写得对 / S3 讲得清)
// a cell counts problems at that stage *or deeper*, so S3 also feeds S1 and S2.
let PLAN = null;   // dashboard/plan.json  — the curriculum, hand-edited
let STAGE = {};    // dashboard/progress.json — '<id>' -> 1..3
let VIEW = 'board';

const SUBTITLE = { board: '数据结构 × 算法范式', grid: '覆盖 × 深度 · NeetCode 150' };

const parseDay = (s) => { const a = s.split('-').map(Number); return new Date(a[0], a[1] - 1, a[2]); };
const stageOf = (id) => STAGE[String(id)] || 0;

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
  const out = [];
  for (const g of PLAN.groups)
    for (const p of g.problems) out.push({ id: p[0], tier: g.tier });
  return out;
}

function buildGrid() {
  if (!PLAN) return;
  if (PLAN.error) { $('#grid-view').innerHTML = `<p class="empty-hint">${esc(PLAN.error)}</p>`; return; }

  const { today, live } = datePhases();
  const all = planProblems();
  const size = (t) => all.filter((p) => p.tier === t).length;
  const reached = (t, s) => all.filter((p) => p.tier === t && stageOf(p.id) >= s).length;

  $('#count').textContent =
    `${all.filter((p) => stageOf(p.id) > 0).length}/${all.length} 已开始 · 阶段 ${live.n}`;

  // --- the grid itself: tiers down, stages across ---
  let m = '<div class="gr-matrix"><div></div>';
  for (const st of PLAN.stages)
    m += `<div class="gr-colh"><span class="gr-colh-t">${esc(st.t)}</span><span class="gr-colh-d">${esc(st.d)}</span></div>`;
  for (const tr of PLAN.tiers) {
    const N = size(tr.t);
    m += `<div class="gr-rowh">
      <span class="gr-rowh-t">${esc(tr.name)}<span class="gr-rowh-n">本层 ${N} 题 · 做完题单累计 ${esc(tr.cum)}</span></span>
      <span class="gr-rowh-d">${esc(tr.desc)}</span></div>`;
    for (const st of PLAN.stages) {
      const n = reached(tr.t, st.s);
      const pct = N ? Math.round((n / N) * 100) : 0;
      const tg = PLAN.targets.filter((x) => x.tier === tr.t && x.stage === st.s);
      const isNow = tg.some((x) => x.phase === live.n);
      const badges = tg
        .map((x) => `<span class="gr-badge${x.phase < live.n ? ' met' : ''}">阶段 ${x.phase} 目标</span>`)
        .join('');
      m += `<div class="gr-cell${isNow ? ' target' : ''}">
        <div class="gr-cell-top"><span class="gr-frac">${n}<small>/${N}</small></span><span class="gr-pct">${pct}%</span></div>
        <div class="gr-bar"><i class="s${st.s}" style="width:${pct}%"></i></div>
        <div class="gr-cell-foot">${badges || '&nbsp;'}</div></div>`;
    }
  }
  m += '</div>';

  // --- timeline: the four phases are a real sequence, so they're numbered ---
  const md_ = (d) => `${d.getMonth() + 1}/${d.getDate()}`;
  let t = '<div class="gr-tl">';
  for (const ph of PLAN.phases) {
    const range = md_(parseDay(ph.from)) + (ph.to ? ' – ' + md_(parseDay(ph.to)) : ' 起');
    const left = ph.to ? Math.max(0, Math.round((parseDay(ph.to) - today) / 864e5)) : null;
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
  let g = '';
  for (const grp of PLAN.groups) {
    const started = grp.problems.filter((p) => stageOf(p[0]) > 0).length;
    const label = `第 ${grp.tier} 层${grp.low ? ' · 低优先' : ''}`;
    const chips = grp.problems.map((p) => {
      const s = stageOf(p[0]);
      return `<button class="gr-chip" data-id="${p[0]}" data-s="${s}"
        title="${esc(p[1])} — ${s ? 'S' + s : '未开始'}，点击进到下一级">
        <span class="gr-st">${s || '·'}</span>
        <span class="gr-id">${p[0]}</span>
        <span class="gr-nm">${esc(p[1])}</span>
        <span class="dot ${p[2]}"></span></button>`;
    }).join('');
    g += `<div class="gr-grp${grp.low ? ' low' : ''}">
      <div class="gr-grp-h"><h3>${esc(grp.name)}</h3>
        <span class="gr-tier${grp.low ? ' low' : ''}" data-t="${grp.tier}">${label}</span>
        ${grp.sub ? `<span class="gr-sub">${esc(grp.sub)}</span>` : ''}
        <span class="gr-grp-c">${started}/${grp.problems.length}</span></div>
      <div class="gr-chips">${chips}</div></div>`;
  }

  $('#grid-view').innerHTML = `
    <section class="gr-sec">
      <div class="gr-sec-h"><h2>格子</h2><p>每格 = 该层里达到<b>该深度及以上</b>的题数 —— 一道 S3 的题同时计进 S1、S2 三列。层之间<b>不</b>累计：每题只属于一层。琥珀框 = 当前阶段该站的位置。</p></div>
      ${m}
      <div class="gr-legend">
        <span class="gr-key"><i class="s0"></i>未开始</span>
        <span class="gr-key"><i class="s1"></i>S1 思路清楚</span>
        <span class="gr-key"><i class="s2"></i>S2 能写对</span>
        <span class="gr-key"><i class="s3"></i>S3 英语讲得清</span>
      </div>
      <p class="gr-note">S1→S2 是 OA 门槛，S2→S3 是面试门槛。S3 不是第三阶段才开始练 —— 阶段一就挑 15 题顺手讲，
      否则会攒下一整个月「做得出但讲不清」的题。</p>
    </section>
    <section class="gr-sec">
      <div class="gr-sec-h"><h2>时间线</h2><p>四段是真序列：每段的目标格建立在前一段已达标的基础上。</p></div>
      ${t}
    </section>
    <section class="gr-sec">
      <div class="gr-sec-h"><h2>题目</h2><p>点一下循环切换 <span class="mono">— → S1 → S2 → S3</span>，写回 dashboard/progress.json。<b>灰掉的组</b>低优先，时间不够先砍它们。</p></div>
      ${g}
    </section>`;
}

async function bumpStage(id) {
  const next = (stageOf(id) + 1) % 4;
  const r = await api('/api/progress', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, stage: next }),
  });
  STAGE = r.stages || STAGE;
  buildGrid();
}

async function switchView(v) {
  VIEW = v;
  $('#subtitle').textContent = SUBTITLE[v];
  document.querySelectorAll('.view-tab').forEach((b) => b.classList.toggle('active', b.dataset.view === v));
  $('#panel').classList.toggle('hidden', v !== 'board');
  $('#grid-view').classList.toggle('hidden', v !== 'grid');
  try { localStorage.setItem('lc-view', v); } catch (e) { /* private mode */ }
  if (v === 'grid') {
    if (!PLAN) {
      const [plan, prog] = await Promise.all([api('/api/plan'), api('/api/progress')]);
      PLAN = plan;
      STAGE = prog.stages || {};
    }
    buildGrid();
  } else {
    buildPanel();
  }
}

async function reload() {
  PROBLEMS = await api('/api/problems');
  buildPanel();
  if (VIEW === 'grid') buildGrid();   // buildPanel owns #count; give it back
}

// ---- wire global controls ----
$('#sync').addEventListener('click', async () => { await fetch('/api/sync', { method: 'POST' }); reload(); });
document.querySelectorAll('.view-tab').forEach((b) =>
  b.addEventListener('click', () => switchView(b.dataset.view)));
$('#grid-view').addEventListener('click', (e) => {
  const chip = e.target.closest('.gr-chip');
  if (chip) bumpStage(+chip.dataset.id);
});
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

let startView = 'board';
try { startView = localStorage.getItem('lc-view') || 'board'; } catch (e) { /* private mode */ }
reload().then(() => switchView(startView));
