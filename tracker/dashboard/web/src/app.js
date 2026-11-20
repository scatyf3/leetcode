// 看板的手写 DOM 部分(坐标系 / 矩阵 / 各个 overlay)。纯计算在 ./lib/*.ts(有单测),
// 复习面板是 ./components/ReviewPanel.vue —— 这个文件只剩"拿数据 -> 拼 DOM -> 绑事件"。
import { createApp } from 'vue';
import ReviewPanel from './components/ReviewPanel.vue';
import SyncControl from './components/SyncControl.vue';
import { initSync, pendingEvents, record as recordEvent } from './sync';
import { againToday, applyEvent, commentRow } from './lib/inbox';
import { api, isReadOnly } from './api';
import { esc } from './lib/esc';
import { FAM, FAM_LEVELS, L_NEXT, depthOf, famCls, famInfo, famKey, famOf } from './lib/fam';
import { dAdd, dParse, daysSince, fmtDays, mmdd, todayStr, weekStart } from './lib/dates';
import { highlightPython } from './lib/highlight';
import { renderMd } from './lib/markdown';
import * as Q from './lib/queue';
import { buildQuiz as buildQuizFor } from './lib/quiz';
import { TL_GONE, buildTimeline as buildTimelineFor, depthKey } from './lib/timeline';

const $ = (s) => document.querySelector(s);
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
// 只读站 + GitHub token: 还没落进 main 的复习事件重放出来的 reviews.jsonl 行(见 ./sync.ts)。
// 本地 server.py 那份看板永远是空的
let SYNTH_REVIEWS = [];
let CURRENT = null; // detail object

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
  $('#e-paused').checked = !!d.paused;
  $('#e-pit').value = d.pit || '';
  $('#e-cluster').value = d.cluster || '';
  $('#e-paused').title = d.paused ? `自 ${d.paused} 起暂停` : '勾上后不进复习队列, interval 也一起冻住';
  $('#note-file').textContent = d.note_file;
  $('#note-edit').value = d.note;
  $('#note-msg').textContent = '';
  $('#meta-msg').textContent = '';
  exitEdit();                 // always open in rendered (preview) mode
  buildSolTabs(d);
  $('#overlay').classList.remove('hidden');
  $('#attempt-msg').textContent = '';
  renderAttemptBtn();                       // 先按已有缓存画一版
  loadAttempts().then(renderAttemptBtn);    // 第一次打开时缓存是空的, 拉回来再画一次
}

// ---- 「＋ 做了一遍」: 日课那两半唯一的入口 ----------------------------------
// 故意**不碰 familiarity** —— 打卡说的是"我动手了", 升不升档是另一件事。合成一个动作的话
// 又会变成"只有做好了才算做过", 日课就退回原来那个只奖励升档的样子(见 AT_META 那段)。
// 一天一题只记一次, 再点一下是撤销(手滑用)。
function renderAttemptBtn() {
  const b = $('#d-attempt');
  if (!b || !CURRENT) return;
  const a = attemptToday(CURRENT.id);
  renderResultRow(a);
  b.classList.toggle('on', !!a);
  if (a) {
    const m = AT_META[a.kind] || { label: a.kind };
    b.textContent = `✓ 今天记过 · ${m.label}`;
    b.title = `打卡时 ${a.fam === null || a.fam === undefined ? '未评' : 'L' + a.fam} → 计入「${m.label}」。点一下撤销`;
  } else {
    // 按钮上先说清这一下会记进哪一半。判据来自服务端(detail 的 attempt_next), 不在这儿重算
    const nx = CURRENT.attempt_next || {};
    const m = AT_META[nx.kind] || AT_META.warm;
    const L = famOf(CURRENT);
    b.textContent = '＋ 做了一遍';
    b.title = `记一次「做了一遍」→ 计入「${m.label}」（${
      nx.first ? '以前没碰过' : '以前做过'}，当前 ${L === null ? '未评' : 'L' + L}）。`
      + '不改熟练度，做成什么样都算数';
  }
}

// 打卡后那一行: 做成什么样 + 算不算攻坚 + 踩了什么坑。没打卡时藏起来 ——
// 点任何一个结果按钮都会先替你打卡(服务端 set_attempt_result 兜底), 所以藏不藏只是省地方。
function renderResultRow(a) {
  const row = $('#d-result');
  if (!row) return;
  row.classList.toggle('hidden', !a || isReadOnly());
  if (!a) return;
  row.querySelectorAll('.d-res[data-res]').forEach((x) =>
    x.classList.toggle('on', x.dataset.res === a.result));
  const at = row.querySelector('.d-attack');
  if (at) at.classList.toggle('on', !!a.attack);
  const pit = $('#d-res-pit');
  if (pit && document.activeElement !== pit) pit.value = a.pit || '';
  // 变体簇的补全: 全库已经出现过的簇名
  const dl = $('#cluster-list');
  if (dl) {
    const cs = [...new Set(PROBLEMS.map((p) => p.cluster).filter(Boolean))];
    dl.innerHTML = cs.map((c) => `<option value="${esc(c)}">`).join('');
  }
}

async function setResult(patch) {
  if (!CURRENT) return;
  const r = await api('/api/attempts', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: CURRENT.id, op: 'result', ...patch }),
  });
  const msg = $('#d-res-msg');
  if (!r || r.ok === false) { if (msg) msg.textContent = (r && r.error) || '记不上'; return; }
  ATTEMPTS = null;
  WEAK = null;
  await loadAttempts();
  renderAttemptBtn();
  if (msg) { msg.textContent = '记下了'; setTimeout(() => { msg.textContent = ''; }, 1500); }
  renderDaily(); renderDrill();
}

async function punchAttempt() {
  if (!CURRENT) return;
  const had = !!attemptToday(CURRENT.id);
  const r = await api('/api/attempts', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: CURRENT.id, op: had ? 'undo' : 'punch' }),
  });
  if (!r || r.ok === false) { $('#attempt-msg').textContent = (r && r.error) || '记不上'; return; }
  ATTEMPTS = null;                    // 重新拉一份, 别在前端猜服务端写了什么
  WEAK = null;
  await loadAttempts();
  renderAttemptBtn();
  $('#attempt-msg').textContent = had ? '已撤销' : '记下了';
  setTimeout(() => { if ($('#attempt-msg')) $('#attempt-msg').textContent = ''; }, 1800);
  renderDaily(); renderDrill();   // 首屏的本周额度跟着变
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
    paused: $('#e-paused').checked,        // 服务端幂等: 已经暂停的再发 true 不会重新计时
    pit: $('#e-pit').value, cluster: $('#e-cluster').value.trim(),
  };
  await putMeta(CURRENT.id, body);
  $('#meta-msg').textContent = '已保存 ✓';
  setTimeout(() => { if ($('#meta-msg')) $('#meta-msg').textContent = ''; }, 1500);
  await reloadKeepOpen();
}

// reload the board data without disturbing the open detail modal
async function reloadKeepOpen() {
  PROBLEMS = await api('/api/problems');
  buildGrid();
  renderPaused();                     // 详情页勾 / 取消「暂停复习」, ⏸ 上的角标跟着变
}

// ---- note: render-by-default, double-click to edit source ----
let EDITING = false;

function enterEdit() {
  EDITING = true;
  $('#note-preview').classList.add('hidden');
  $('#note-edit').classList.remove('hidden');
  $('#save-note').classList.remove('hidden');
  $('#note-mode').textContent = '编辑中 · Ctrl+S 保存';
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
  $('#note-mode').textContent = '';
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
  // 再往后是可视化(题目文件夹里的 viz.html), 有就排在题面后面
  SOL_ITEMS = [
    ...(d.description ? [{ name: '📄 题目', html: d.description }] : []),
    ...(d.viz ? [{ name: '🎞 可视化', viz: d.viz, readonly: true }] : []),
    ...d.solutions,
  ];
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
  desc.classList.toggle('viz', item.viz !== undefined);
  if (item.viz !== undefined) {
    // viz.html 自带脚本, 关进 sandbox iframe(不给 same-origin, 碰不到看板的 DOM / API);
    // 深浅色在打开 tab 时注入到它的 <html data-theme>
    const doc = item.viz.replace(/<html\b/i, `<html data-theme="${document.documentElement.dataset.theme || 'light'}"`);
    desc.innerHTML = `<iframe class="viz-frame" sandbox="allow-scripts" srcdoc="${esc(doc)}"></iframe>`;
    desc.classList.remove('hidden');
    code.classList.add('hidden');
    $('#sol-mode').textContent = '';
    return;
  }
  if (item.html !== undefined) {
    desc.innerHTML = item.html;
    desc.scrollTop = 0;
    desc.classList.remove('hidden');
    code.classList.add('hidden');
    $('#sol-mode').textContent = '';
    return;
  }
  code.firstChild.innerHTML = item.name.endsWith('.py')
    ? highlightPython(item.content)
    : esc(item.content);
  code.scrollTop = 0;
  code.classList.remove('hidden');
  desc.classList.add('hidden');
  $('#sol-mode').textContent = '';
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
  $('#sol-mode').textContent = '编辑中 · Ctrl+S 保存';
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
  $('#doc-msg').textContent = '';
  exitDocEdit();
  $('#doc-overlay').classList.remove('hidden');
}

function enterDocEdit() {
  DOC_EDITING = true;
  $('#doc-preview').classList.add('hidden');
  $('#doc-edit').classList.remove('hidden');
  $('#doc-save').classList.remove('hidden');
  $('#doc-mode').textContent = '编辑中 · Ctrl+S 保存';
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
  $('#doc-mode').textContent = '';
}

async function saveDoc() {
  const content = $('#doc-edit').value;
  await fetch(`/api/${DOC.kind}/` + encodeURIComponent(DOC.name), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  DOC.content = content;
  $('#doc-msg').textContent = '已保存 ✓';
  setTimeout(() => { if ($('#doc-msg')) $('#doc-msg').textContent = ''; }, 1500);
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
  $('#nt-mode').textContent = '编辑中 · Ctrl+S 保存';
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
  $('#nt-mode').textContent = '';
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

// markdown: marked + 题号链接(lib/markdown.ts)。题号索引每次现建, 和看板永远对得上
const md = (src) => renderMd(src, byId());

// ---- 🧠 FSRS 复习 -----------------------------------------------------------
// 排队规则在 lib/queue.ts, 面板在 components/ReviewPanel.vue。这里只把两个牌组的行接上去,
// 📈 进度那节和日课那节也用这几个数。
const isCard = Q.isCard;
const isDue = (p) => Q.isDue(p);
const rvEligible = Q.rvEligible;
const deckRows = (deck) => (deck === 'syntax' ? SYNTAX : PROBLEMS);
const queuePool = (deck = 'problems') => Q.queuePool(deckRows(deck), deck);
// 三种模式的**范围完全一样**, 所以徽章和 📈 里的数字跟模式无关
const buildQueue = (mode = 'fsrs', deck = 'problems') => Q.orderQueue(queuePool(deck), mode, deck);
// 每天复习上限(两个牌组各算各的)。PLAN 在坐标系视图才会拉, 没拉到就按 10。
const rvCap = () => (PLAN && +PLAN.review_cap) || 10;
const reviewedToday = (deck) => deckRows(deck).filter((p) => p.last_review === todayStr()).length;
const rvCapLeft = (deck) => Math.max(0, rvCap() - reviewedToday(deck));
const deckDue = (deck) => queuePool(deck).length;

function updateReviewBadge() {
  const n = { problems: deckDue('problems'), syntax: deckDue('syntax') };
  const total = n.problems + n.syntax;
  $('#review-n').textContent = total;
  $('#review-n').classList.toggle('hidden', !total);
  const btn = $('#open-review');
  if (btn) btn.title = `题目 ${n.problems} 道 · 语法 ${n.syntax} 张`;
  renderPaused();                      // 复习面板里按 ⏸ 暂停也走这儿
  return n;
}

// 复习面板和看板之间只走这一个口子(见 ReviewPanel.vue 的 ReviewHost)。
// 全写成箭头函数: putMeta / PLAN 这些在文件更下面才声明, 现在就取值会撞上 TDZ。
const RV = createApp(ReviewPanel, {
  host: {
    rows: (deck) => deckRows(deck),
    queue: (mode, deck) => buildQueue(mode, deck).slice(0, rvCapLeft(deck)),
    quiz: (d) => buildQuizFor(d, PROBLEMS),
    md: (src) => md(src),
    refresh: () => { buildGrid(); return updateReviewBadge(); },
    badge: () => updateReviewBadge(),
    putMeta: (id, body) => putMeta(id, body),
    openStats: () => openStats(),
    reviewsChanged: () => { REVIEWS = null; },
    // 只读站连上 GitHub 之后才走这几个(面板里看 syncState.mode 决定)
    record: (e) => {
      const ev = recordEvent(e);
      applyOne(ev);
      if (ev.op === 'rate') REVIEWS = null;
      return ev;
    },
    again: (deck) => againToday(SYNTH_REVIEWS, deck, todayStr()),
    pendingComments: () => pendingEvents().filter((e) => e.op === 'comment').map(commentRow),
  },
}).mount('#review-app');

// ---- 只读站的复习同步 ---------------------------------------------------------
// 导出的数据是 main 当时的状态; 手机上评过、还没落进 main 的事件(./sync.ts)在它上面重放一遍,
// 到期数 / 队列 / 📈 才对得上。重放用的 FSRS 是 lib/fsrs.ts —— fsrs.py 的逐行移植, 有对拍。
function applyOne(ev) {
  if (ev.op === 'comment') return;
  const r = applyEvent(deckRows(ev.deck), ev);
  if (r) SYNTH_REVIEWS.push(r);
}
function applyPending() {
  SYNTH_REVIEWS = [];
  for (const ev of pendingEvents()) applyOne(ev);
  REVIEWS = null;
}
if (isReadOnly()) {
  const box = document.createElement('div');
  const actions = $('header .actions');
  if (actions) {
    actions.insertBefore(box, $('#theme-toggle'));
    createApp(SyncControl).mount(box);
  }
}

// ---- 📈 复习进度: 到期预测 / 记忆强度 / 复习历史 -----------------------------
// 每个数字都从 /api/problems 的 fsrs 列 + /api/reviews(reviews.jsonl) **现算**,
// 不落第二份统计 —— 手改了某题的 meta.json 或者删掉 data.db 重建, 这里跟着变, 不会对不上。
let REVIEWS = null;                 // reviews.jsonl 的全部行; null = 还没拉过
let EDITS = null;                   // edits.jsonl 的全部行(标签/熟练度改动); null = 还没拉过
let ATTEMPTS = null;                // attempts.jsonl 的全部行(做题打卡); null = 还没拉过

const RATE_LABEL = { 1: '忘了', 2: '勉强', 3: '想起来了', 4: '很熟' };
const FORECAST_DAYS = 30;           // 到期预测往前看多远
const HISTORY_DAYS = 30;            // 复习历史往回看多久

// stability(天)的分桶: [上界(不含), 标签]。最后一档兜底。
const SBUCKETS = [[1, '<1天'], [3, '1-3天'], [7, '3-7天'], [14, '1-2周'],
                  [30, '2-4周'], [90, '1-3月'], [180, '3-6月'], [Infinity, '>6月']];
const sBucket = (d) => SBUCKETS.findIndex(([hi]) => d < hi);

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
// 统计的题(ids)也铺进初始状态: 题单里有、NeetCode 150 和仓库里都没有的题得算作「未做」占一格
const buildTimeline = (opts = {}) => buildTimelineFor({
  planGroups: [...(PLAN?.groups || []), ...(opts.ids ? [{ problems: [...opts.ids].map((id) => [id]) }] : [])],
  problems: PROBLEMS, edits: EDITS,
  keyOf: opts.keyOf || tlKey, ids: opts.ids || null,
});

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
  await loadReviews();                 // 拿不到历史也要能画出到期预测那部分
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
  buildGrid();
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
  buildGrid();
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
  closePausedPop();
  await loadTodo();                   // 每次打开都重读, 拿到我在别处的改动
  pop.classList.remove('hidden');
  $('#todo-in').focus();
}

// ---- ⏸ 暂停: 暂停中的题一览, 就地恢复 / 按题号再加 ----------------------------
// 真相还是各题 meta.json 的 paused(见 server.set_paused), 这里只是个集中入口 ——
// 以前要恢复得一道道点进详情取消勾选, 暂停的一多就忘了哪些还停着。
let PAUSED_MSG_T = null;
function flashPaused(msg, ms = 2500) {
  clearTimeout(PAUSED_MSG_T);
  $('#paused-msg').textContent = msg;
  PAUSED_MSG_T = setTimeout(() => ($('#paused-msg').textContent = ''), ms);
}

function renderPaused() {
  const rows = PROBLEMS.filter((p) => p.paused)
    .sort((a, b) => a.paused.localeCompare(b.paused) || a.id - b.id);   // 停得最久的在上
  $('#paused-n').textContent = rows.length;
  $('#paused-n').classList.toggle('hidden', !rows.length);
  $('#paused-list').innerHTML = rows.length
    ? rows.map((p) => {
        const n = daysSince(p.paused);
        return `<div class="todo-item">
          <span class="dot ${p.difficulty || 'none'}" title="${p.difficulty || 'none'}"></span>
          <span class="todo-text openable" data-open="${p.id}" title="打开 #${p.id}">${p.id} ${esc(p.title)}</span>
          <span class="paused-since" title="自 ${esc(p.paused)} 起暂停">${n > 0 ? `${n} 天` : '今天'}</span>
          <button class="paused-resume" data-id="${p.id}" title="恢复复习: due 一起往后推 ${n} 天">恢复</button>
        </div>`;
      }).join('')
    : '<div class="todo-empty">没有暂停中的题。</div>';

  $('#paused-list').querySelectorAll('.paused-resume').forEach((el) =>
    el.addEventListener('click', () => setPaused(+el.dataset.id, false)));
  $('#paused-list').querySelectorAll('.todo-text.openable').forEach((el) =>
    el.addEventListener('click', () => { closePausedPop(); openDetail(+el.dataset.open); }));
}

async function setPaused(id, on) {
  let ok = false;
  try { ok = (await putMeta(id, { paused: on })).ok; } catch { ok = false; }
  if (!ok) return flashPaused('没存上(服务没起?)');
  PROBLEMS = await api('/api/problems');           // 恢复会改 due, 得重拉
  buildGrid();
  updateReviewBadge();                             // 里面顺带 renderPaused
  flashPaused(on ? `#${id} 已暂停` : `#${id} 已恢复 ✓`);
}

function addPaused() {
  const raw = $('#paused-in').value.trim().replace(/^#/, '');
  if (!raw) return;
  const p = PROBLEMS.find((x) => x.id === +raw);
  if (!p) return flashPaused(`看板里没有 #${raw}`);
  if (p.paused) return flashPaused(`#${p.id} 已经在暂停了`);
  $('#paused-in').value = '';
  setPaused(p.id, true);
}

function closePausedPop() { $('#paused-pop').classList.add('hidden'); }

function togglePausedPop() {
  const pop = $('#paused-pop');
  if (!pop.classList.contains('hidden')) return closePausedPop();
  closeTodoPop();
  renderPaused();
  pop.classList.remove('hidden');
  $('#paused-in').focus();
}

// ---- 首页: 今天 / 每日 / 专题熟练度 + 下面几个折叠区 -------------------------
// 不再跟计划(阶段 / 里程碑 / 额度)比。首页只回答两件事: 这些天手上有没有在动,
// 每个专题熟到哪了。plan.json 现在只当分类表用: groups(专题 = NeetCode 的 pattern 组)、
// extras(其他题单往组里归)、topics(专题区)、mock、review_cap。
let PLAN = null;   // dashboard/plan.json

// 深度不另存: 由每题 meta.json 的 familiarity 算出来。一个字段, 一条阶梯:
//   L0 英语讲得清                      -> S3 讲得清 (面试门槛)
//   L1 已经熟悉 / L2 思路会·细节易写错  -> S2 写得对 (OA 门槛)
//   L2.5 默写得出·道理不熟             -> S2 (OA 够, 离 L0 比 L2 远)
//   L3 思路大概知道·不熟               -> S1 思路清楚
//   L4 思路都不知道 / 未评 / 没建文件夹  -> 还没到 S1
// 阶梯是有序的, 所以 S3 ⊂ S2 ⊂ S1 由构造保证 —— 讲得清的题必然也写得对,
// 不会出现"讲得出但写不对"的题混进 S2 那一列(而 S2 正是判断能不能做 OA 的那列)。
const byId = () => new Map(PROBLEMS.map((p) => [p.id, p]));


const reduceMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

// 题卡左边那个方块的颜色: 按熟练度的档(和专题熟练度那根条同一套色), 没建文件夹 = 不加类
const stCls = (rec) => (rec ? 'fm-' + (FM_BUCKETS.find(([, , f]) => f(famOf(rec))) || ['nr'])[0] : '');

// 坐标系里几个折叠区的展开状态(题目 / 其他), 存本地
function gridFolds() {
  try { return new Set(JSON.parse(localStorage.getItem('lc-grid-folds') || '[]')); } catch (e) { return new Set(); }
}

// 其他题单(lists.json)在坐标系每组下面的框。只补 NeetCode 150 没有的题, 每题全页只出现一次:
// plan.json extras.lists 的顺序就是去重优先级。归到哪组看那张「分类 → 组名」表。
// 只是看的 —— 不进 planProblems, 所以格子、组计数、目标都不受影响。
const OTHER_GROUP = '其他';
function planExtras() {
  const byGroup = new Map();           // 组名 -> [{list, short, items: [[id, title]]}]
  const srcOf = new Map();             // id -> 出现在哪些题单(简称), 题卡角标用
  const nc = new Set(PLAN.groups.flatMap((g) => g.problems.map((p) => p[0])));
  const names = new Set(PLAN.groups.map((g) => g.name));
  const placed = new Set();
  for (const d of (PLAN.extras?.lists || [])) {
    const def = LISTS?.lists?.[d.name];
    if (!def) { console.warn(`plan.json extras: lists.json 里没有题单「${d.name}」`); continue; }
    for (const [cat, items] of Object.entries(def.categories)) {
      let grp = d.map?.[cat] || OTHER_GROUP;
      if (grp !== OTHER_GROUP && !names.has(grp)) {
        console.warn(`plan.json extras: ${d.name} · ${cat} 指向不存在的组「${grp}」, 先放进${OTHER_GROUP}`);
        grp = OTHER_GROUP;
      }
      for (const [id, title] of items) {
        const s = srcOf.get(id) || srcOf.set(id, []).get(id);
        if (!s.includes(d.short)) s.push(d.short);
        if (nc.has(id) || placed.has(id)) continue;
        placed.add(id);
        const boxes = byGroup.get(grp) || byGroup.set(grp, []).get(grp);
        let box = boxes.find((b) => b.list === d.name);
        if (!box) boxes.push(box = { list: d.name, short: d.short, items: [] });
        box.items.push([id, title]);
      }
    }
  }
  return { byGroup, srcOf };
}

function buildGrid() {
  if (!PLAN) return;
  if (PLAN.error) { $('#grid-view').innerHTML = `<p class="empty-hint">${esc(PLAN.error)}</p>`; return; }

  const good = PROBLEMS.filter((p) => depthOf(p) >= 2).length;
  $('#sub').textContent = '';
  $('#count').textContent = `${PROBLEMS.length} 题 · 熟 ${good}`;
  $('#count').title = '熟 = L0–L2.5(写得对)';

  // --- the problems, by pattern group; click a badge to cycle its familiarity ---
  const recs = byId();
  const famTip = {};
  for (const f of (PLAN.familiarity || [])) famTip[f.l] = `${f.t} ${f.d}`;
  const X = planExtras();
  const listName = new Map((PLAN.extras?.lists || []).map((d) => [d.short, d.name]));
  const startedOf = (ids) => ids.filter((id) => depthOf(recs.get(id)) >= 1).length;
  // 两个点击区: 左边徽章翻熟练度(或建文件夹), 右边题名打开详情。
  // 内层 span 的 title 会盖住外层 button 的, 所以悬停提示也各说各的。
  // skip = 题卡所在那个框的题单简称 —— 角标只说「还在哪些别的题单里」。
  const chipHTML = (id, title, diff, skip) => {
    const rec = recs.get(id);
    const L = rec ? famOf(rec) : undefined;        // undefined = 还没建文件夹
    const d = depthOf(rec);
    const badge = rec === undefined ? '+' : famInfo(L).short;
    const tip = rec === undefined ? '还没建文件夹 — 点击建（去 LeetCode 抓题面）'
      : L === null ? '还没评熟练度 — 点击标 L4' : famTip[L];
    const src = (X.srcOf.get(id) || []).filter((s) => s !== skip);
    return `<button class="gr-chip" data-id="${id}" data-d="${d}" title="${esc(title)} — ${
      rec === undefined ? '还没建文件夹 — 点击建（去 LeetCode 抓题面）' : '点击打开题目'}">
        <span class="gr-st s${d} ${stCls(rec)}" title="${esc(title)} — ${esc(tip)}">${badge}</span>
        <span class="gr-id">${id}</span>
        <span class="gr-nm">${esc(title)}</span>
        ${src.length ? `<span class="gr-src" title="也在 ${
          esc(src.map((s) => listName.get(s)).join(' / '))}">${esc(src.join(' '))}</span>` : ''}
        <span class="dot ${diff}"></span></button>`;
  };
  const xBoxes = (name) => (X.byGroup.get(name) || []).map((b) => {
    const k = Math.min(b.items.length, 5);         // 题少的框窄一点, 好几个框能并排
    return `<div class="gr-box gr-box-x" style="flex:${k} 1 ${k * 215}px">
      <div class="gr-box-h" title="${esc(b.list)} 里有、NeetCode 150 没有的题 —— 只看, 不计进度">
        ${esc(b.list)} <b>+${b.items.length}</b>
        <span class="gr-box-c">${startedOf(b.items.map((p) => p[0]))}/${b.items.length}</span></div>
      <div class="gr-chips">${b.items.map(([id, t]) =>
        chipHTML(id, t, recs.get(id)?.difficulty || 'none', b.short)).join('')}</div></div>`;
  }).join('');
  let g = '', gl = '';           // gl = 低优先/砍掉的组, 折在最底下
  PLAN.groups.forEach((grp, gi) => {
    const chips = grp.problems.map((p) => chipHTML(p[0], p[1], p[2])).join('');
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
    const fm = topicFam(grp, X, recs);
    const add = `<div class="gr-grp${grp.low ? ' low' : ''}" id="gr-g-${gi}">
      <div class="gr-grp-h">${head}
        ${grp.low ? '<span class="gr-tier low">低优先</span>' : ''}
        ${grp.sub ? `<span class="gr-sub">${esc(grp.sub)}</span>` : ''}
        <span class="gr-grp-c" title="熟 = L0–L2.5 · 分母 = NeetCode 150 这组 + 其他题单里建过文件夹的">
          <span class="fm-bar fm-mini">${famBarHTML(fm)}</span><b>${fm.good}</b>/${fm.N}</span></div>
      <div class="gr-box"><div class="gr-box-h">NeetCode 150</div><div class="gr-chips">${chips}</div></div>
      ${X.byGroup.has(grp.name) ? `<div class="gr-xboxes">${xBoxes(grp.name)}</div>` : ''}</div>`;
    if (grp.low) gl += add; else g += add;
  });
  if (X.byGroup.has(OTHER_GROUP)) gl += `<div class="gr-grp">
      <div class="gr-grp-h"><h3 title="题单分类对不上上面任何一组的题 · 归组规则在 plan.json 的 extras">${OTHER_GROUP}</h3></div>
      <div class="gr-xboxes">${xBoxes(OTHER_GROUP)}</div></div>`;

  // 首屏: KPI 一排 + 每日热力图 + 专题熟练度。其余折起来, 展开状态记在 localStorage。
  const fold = (k, label, body) => `<details class="gr-more" data-fold="${k}"${
    gridFolds().has(k) ? ' open' : ''}><summary>${label}</summary>${body}</details>`;
  const topics = topicsHTML();
  $('#grid-view').innerHTML = `
    <section class="kpis" id="gr-kpi">${kpiHTML()}</section>
    <section class="gr-sec">
      <div class="gr-sec-h"><h2>每日</h2></div>
      <div class="dl-row">
        <div class="card" id="gr-heat"><p class="empty-hint">读取历史…</p></div>
        <div class="card" id="gr-bars"></div>
      </div>
      <div id="gr-today"></div>
    </section>
    <section class="gr-sec" id="gr-fam">${famSecHTML(X, recs)}</section>
    ${fold('problems', '题目', `
      ${g}
      ${gl ? `<details class="gr-lowbox"><summary>低优先 · 其他题单</summary>${gl}</details>` : ''}`)}
    ${fold('drill', '攻坚 · Mock', '<section class="gr-sec" id="gr-drill"><p class="empty-hint">读取中…</p></section>')}
    ${topics ? fold('topics', '专题', topics) : ''}`;
  $('#grid-view').querySelectorAll('details[data-fold]').forEach((el) =>
    el.addEventListener('toggle', () => {
      const s = gridFolds();
      el.open ? s.add(el.dataset.fold) : s.delete(el.dataset.fold);
      try { localStorage.setItem('lc-grid-folds', JSON.stringify([...s])); } catch (e) { /* private mode */ }
    }));
  renderDaily();         // 异步: 要等 attempts.jsonl + reviews.jsonl
  renderDrill();         // 异步: 要等 /api/weak + /api/mock
}

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



// ---- 做题打卡 / 日课: 复习重做 + 新题, 两半各自计数 ---------------------------
// 日课**不能**接着从 familiarity 跃迁算。那样只有"升档"才得分, 于是重做一道 L4 没升上去
// = 白干、诚实降档 = 倒扣, 唯一的最优策略变成挑软柿子 + 把自己评高 —— 恰好是刷题里最该
// 避免的两件事。所以这里读的是 attempts.jsonl: 记的是**动作**(哪天做了哪道题、打卡当时
// 是什么档), 效果一概不参与, 重做完更差了照样算今天做过。
//
// 分档在服务端定死一处(server.py 的 attempt_state), 前端不重算 —— 重算迟早会和那边分叉,
// 而按钮上的预告和真正落盘的那一笔必须是同一个答案。规则是**先问以前碰过没有, 再看档位**:
//   new  = 之前没打过卡, 且(从没评过档 或 文件夹是今天才建的)
//   redo = 碰过 + 打卡时 L3 / L3.5 / L4
//   warm = 其余(打卡时 L0-L2), 记一行但不占额度 —— 重刷熟题不该能凑满日课
// 顺序不能反: 只看档位的话, "今天新建 → 做一遍 → 不会 → 评 L4 → 打卡"会被算成复习重做,
// 新题就洗成了复习。反过来"有没有文件夹"也不能单独当判据 —— 📋 TODO 会提前把空文件夹建出来。
// **档位看的是打卡那一刻**, 打完卡再改熟练度不回头改写这一笔。
const AT_META = {
  redo: { label: '复习重做', cls: 'b-redo', tip: '以前做过 · 打卡时 L3 / L3.5 / L4' },
  new:  { label: '新题',     cls: 'b-new',  tip: '以前没碰过 · 第一次做' },
  warm: { label: '巩固',     cls: 'b-warm', tip: '以前做过 · 打卡时已 L0–L2 · 不占额度' },
  attack: { label: '攻坚',   cls: 'b-attack', tip: '弱题的变体簇 · 打卡后在详情页点「攻坚」' },
};

async function loadAttempts() {
  if (ATTEMPTS === null) {
    try { ATTEMPTS = (await api('/api/attempts')).attempts || []; } catch { ATTEMPTS = []; }
  }
  return ATTEMPTS;
}

const attemptToday = (id) => (ATTEMPTS || []).find((a) => a.id === id && a.date === todayStr());

// 标了攻坚的那一笔只进攻坚那格, 不再同时算新题/重做 —— 一笔不能吃两份额度
function attemptCounts(date) {
  const c = { redo: 0, new: 0, warm: 0, attack: 0 };
  for (const a of (ATTEMPTS || [])) {
    if (a.date !== date) continue;
    const k = a.attack ? 'attack' : a.kind;
    if (c[k] !== undefined) c[k]++;
  }
  return c;
}

// ---- 每日: 打卡(attempts.jsonl) + 复习(reviews.jsonl) 按天聚合 ---------------------
// 两份日志都是**动作**: 做没做、评没评, 不看效果。热力图的深浅 = 当天动作总数,
// 柱状图只画做题(按 kind 堆叠) —— 复习一天几十张, 和做题放一根柱子里做题就看不见了。
async function loadReviews() {
  if (REVIEWS === null) {
    // 只读站没有这个文件时 shim 会回一个空壳
    try { REVIEWS = (await api('/api/reviews')).reviews || []; } catch { REVIEWS = []; }
    REVIEWS = [...REVIEWS, ...SYNTH_REVIEWS];      // 只读站: 还没落进 main 的那几次也算上
  }
  return REVIEWS;
}

// date -> { a: 做题数, r: 复习数, k: {new, redo, warm, attack} }; 两份日志有一份没拉到就是 null
function activityByDay() {
  if (ATTEMPTS === null || REVIEWS === null) return null;
  const m = new Map();
  const get = (d) => m.get(d) || m.set(d, { a: 0, r: 0, k: { new: 0, redo: 0, warm: 0, attack: 0 } }).get(d);
  for (const a of ATTEMPTS) {
    const x = get(a.date);
    x.a++;
    const k = a.attack ? 'attack' : a.kind;
    if (x.k[k] !== undefined) x.k[k]++;
  }
  for (const r of REVIEWS) if (r.date) get(r.date).r++;
  return m;
}
const ZERO_DAY = { a: 0, r: 0, k: { new: 0, redo: 0, warm: 0, attack: 0 } };

// 连续天数: 做题或复习有一样就算这天没断。今天还没动的话从昨天往回数 —— 早上打开页面不该看到 0
function streakOf(act) {
  const on = (d) => { const x = act.get(d); return !!x && x.a + x.r > 0; };
  let d = todayStr();
  if (!on(d)) d = dAdd(d, -1);
  let cur = 0;
  while (on(d)) { cur++; d = dAdd(d, -1); }
  let best = 0, run = 0, prev = null;
  for (const x of [...act.keys()].filter(on).sort()) {
    run = prev && dAdd(prev, 1) === x ? run + 1 : 1;
    best = Math.max(best, run);
    prev = x;
  }
  return { cur, best: Math.max(best, cur), todayOn: on(todayStr()) };
}

// ---- 首屏 KPI: 今天做题 / 本周 / 连续 / 今日复习 ----------------------------------
function kpiHTML() {
  const today = todayStr();
  const act = activityByDay();
  const tile = (k, v, sub, cls = '', attrs = '') => `<div class="kpi${cls ? ' ' + cls : ''}"${attrs}>
      <span class="kpi-k">${k}</span><b class="kpi-v">${v}</b><span class="kpi-s">${sub}</span></div>`;
  let t1, t2, t3;
  if (!act) {
    t1 = tile('今天做题', '…', ''); t2 = tile('本周做题', '…', ''); t3 = tile('连续', '…', '');
  } else {
    const x = act.get(today) || ZERO_DAY;
    const parts = ['new', 'redo', 'attack', 'warm'].filter((k) => x.k[k]).map((k) => `${AT_META[k].label} ${x.k[k]}`);
    t1 = tile('今天做题', `${x.a}<small> 道</small>`, parts.join(' · ') || '详情页「＋ 做了一遍」打卡', x.a ? 'met' : '');

    // 本周: 一个合计 + 周一到周日七根小柱
    const ws = weekStart(today);
    const days = [...Array(7)].map((_, i) => dAdd(ws, i));
    const per = days.map((d) => (act.get(d) || ZERO_DAY).a);
    const mx = Math.max(1, ...per);
    const bars = days.map((d, i) => `<i class="wk-b${d === today ? ' now' : ''}${d > today ? ' fut' : ''}"
        title="${esc(mmdd(d))} · 做题 ${per[i]} · 复习 ${(act.get(d) || ZERO_DAY).r}"><u style="height:${
        per[i] ? Math.max(12, Math.round((per[i] / mx) * 100)) : 0}%"></u><em>${'一二三四五六日'[i]}</em></i>`).join('');
    t2 = `<div class="kpi kpi-wk"><span class="kpi-k">本周做题</span>
      <div class="kpi-wk-row"><b class="kpi-v">${per.reduce((a, b) => a + b, 0)}<small> 道</small></b>
      <div class="wk-bars">${bars}</div></div></div>`;

    const s = streakOf(act);
    t3 = tile('连续', `${s.cur}<small> 天</small>`,
      `${s.todayOn ? '今天已动' : s.cur ? '今天还没动' : '从今天开始'} · 最长 ${s.best} 天`,
      s.todayOn ? 'met' : '', ' title="做题或复习有一样就算"');
  }
  // 今日复习: 两个牌组都刷到上限(或刷空)就打勾
  const left = Math.min(deckDue('problems'), rvCapLeft('problems')) + Math.min(deckDue('syntax'), rvCapLeft('syntax'));
  const rated = reviewedToday('problems') + reviewedToday('syntax');
  const t4 = tile('今日复习', left ? `${left}<small> 张</small>` : '✓',
    left ? `已评 ${rated} · 点这里开始 →` : `已评 ${rated} 张`,
    left ? 'go' : 'met', ` data-review="1" role="button" tabindex="0" title="每个牌组每天上限 ${rvCap()} 张"`);
  return t1 + t2 + t3 + t4;
}

function renderKpi() {
  const box = $('#gr-kpi');
  if (box) box.innerHTML = kpiHTML();
}

// 热力图: 周一开头的列, 一列一周, 最右一列是本周
const HEAT_WEEKS = 20;
function heatHTML(act) {
  const today = todayStr();
  const start = dAdd(weekStart(today), -7 * (HEAT_WEEKS - 1));
  const lvl = (n) => (n === 0 ? 0 : n <= 3 ? 1 : n <= 8 ? 2 : n <= 15 ? 3 : 4);
  let cells = '', months = '', active = 0, A = 0, R = 0;
  for (let w = 0; w < HEAT_WEEKS; w++) {
    const d0 = dAdd(start, 7 * w);
    // 月份标在含 1 号的那一列上(GitHub 那样), 不然开头那列和下个月挤成「6月7月」
    const first = [...Array(7)].map((_, i) => dAdd(d0, i)).find((d) => d.endsWith('-01'));
    months += `<span>${first ? `${+first.slice(5, 7)}月` : ''}</span>`;
    for (let i = 0; i < 7; i++) {
      const d = dAdd(d0, i);
      if (d > today) { cells += '<i class="hm-c fut"></i>'; continue; }
      const x = act.get(d) || ZERO_DAY;
      const n = x.a + x.r;
      if (n) active++;
      A += x.a; R += x.r;
      cells += `<i class="hm-c l${lvl(n)}${d === today ? ' now' : ''}" title="${esc(mmdd(d))} 周${'一二三四五六日'[i]} · 做题 ${x.a} · 复习 ${x.r}"></i>`;
    }
  }
  const key = [0, 1, 2, 3, 4].map((l) => `<i class="hm-c l${l}"></i>`).join('');
  return `<div class="card-h"><b>活跃</b><span class="hint">近 ${HEAT_WEEKS} 周 · ${active} 天 · 做题 ${A} · 复习 ${R}</span></div>
    <div class="hm" style="--w:${HEAT_WEEKS}">
      <div></div><div class="hm-months">${months}</div>
      <div class="hm-days"><span>一</span><span></span><span>三</span><span></span><span>五</span><span></span><span>日</span></div>
      <div class="hm-grid">${cells}</div>
    </div>
    <div class="hm-key">少 ${key} 多</div>`;
}

// 最近 28 天的做题柱, 按 kind 堆叠(颜色和打卡那套一致)
const BAR_DAYS = 28;
function barsHTML(act) {
  const today = todayStr();
  const days = [...Array(BAR_DAYS)].map((_, i) => dAdd(today, i - BAR_DAYS + 1));
  const rows = days.map((d) => act.get(d) || ZERO_DAY);
  const mx = Math.max(3, ...rows.map((x) => x.a));
  const order = ['new', 'redo', 'attack', 'warm'];
  const cols = days.map((d, i) => {
    const x = rows[i];
    const segs = order.filter((k) => x.k[k]).map((k) =>
      `<u class="${AT_META[k].cls}" style="height:${((x.k[k] / mx) * 100).toFixed(1)}%"></u>`).join('');
    const tip = [`${mmdd(d)}`, ...order.filter((k) => x.k[k]).map((k) => `${AT_META[k].label} ${x.k[k]}`), `复习 ${x.r}`].join(' · ');
    return `<div class="db-c${d === today ? ' now' : ''}" title="${esc(tip)}">
      <div class="db-bar">${segs}</div><em>${(BAR_DAYS - 1 - i) % 7 === 0 ? esc(mmdd(d)) : ''}</em></div>`;
  }).join('');
  const sum = rows.reduce((a, x) => a + x.a, 0);
  const legend = order.map((k) => `<span class="skey"><i class="${AT_META[k].cls}"></i>${AT_META[k].label}</span>`).join('');
  return `<div class="card-h"><b>做题</b><span class="hint">近 ${BAR_DAYS} 天 ${sum} 道 · 日均 ${(sum / BAR_DAYS).toFixed(1)}</span></div>
    <div class="db" style="--n:${BAR_DAYS}">${cols}</div>
    <div class="db-key">${legend}</div>`;
}

// ---- 专题熟练度: 每个 pattern 组里各档几道 ----------------------------------------
// 分母 = NeetCode 150 这组的题 + 其他题单归进这组、**建过文件夹**的题。
// 没建过的其他题单题不算: 题单一加, 分母凭空涨一截, 熟练度看着就掉了, 其实一道没退步。
// 「熟」= L0–L2.5, 和 README 里 OA 门槛那条线同一个口径。
const FM_BUCKETS = [
  ['l0', 'L0 讲得清', (L) => L === 0],
  ['l1', 'L1 · L1.5', (L) => L === 1 || L === 1.5],
  ['l2', 'L2 · L2.5', (L) => L === 2 || L === 2.5],
  ['l3', 'L3 · L3.5', (L) => L === 3 || L === 3.5],
  ['l4', 'L4', (L) => L === 4],
  ['nr', '未评', (L) => L === null],
  ['gone', '没建', () => false],
];
function topicFam(grp, X, recs) {
  const ids = new Set(grp.problems.map((p) => p[0]));
  for (const b of (X.byGroup.get(grp.name) || [])) for (const [id] of b.items) if (recs.get(id)) ids.add(id);
  const c = Object.fromEntries(FM_BUCKETS.map(([k]) => [k, 0]));
  let sum = 0, rated = 0;
  for (const id of ids) {
    const rec = recs.get(id);
    if (!rec) { c.gone++; continue; }
    const L = famOf(rec);
    const b = FM_BUCKETS.find(([, , f]) => f(L));
    c[b ? b[0] : 'nr']++;
    if (L !== null) { sum += L; rated++; }
  }
  const N = ids.size;
  const good = c.l0 + c.l1 + c.l2;
  return { c, N, good, pct: N ? good / N : 0, avg: rated ? sum / rated : null };
}
const famBarHTML = (fm) => FM_BUCKETS.filter(([k]) => fm.c[k]).map(([k, label]) =>
  `<i class="fm-s ${k}" style="flex:${fm.c[k]}" title="${esc(label)} · ${fm.c[k]} 道"></i>`).join('');

function fmSort() {
  try { return localStorage.getItem('lc-fm-sort') === 'weak' ? 'weak' : 'plan'; } catch { return 'plan'; }
}
function famSecHTML(X, recs) {
  const rows = PLAN.groups.map((grp, gi) => ({ grp, gi, fm: topicFam(grp, X, recs) }));
  const sort = fmSort();
  if (sort === 'weak') rows.sort((a, b) => a.fm.pct - b.fm.pct || b.fm.N - a.fm.N);
  const row = ({ grp, gi, fm }) => `<button class="fm-row${grp.low ? ' low' : ''}" data-jump-g="${gi}"
      title="${esc(grp.name)} · 熟 ${fm.good}/${fm.N}${fm.avg !== null ? ` · 平均 L${fm.avg.toFixed(1)}` : ''} · 点击跳到这组的题">
      <span class="fm-nm">${esc(grp.name)}</span>
      <span class="fm-bar">${famBarHTML(fm)}</span>
      <span class="fm-n"><b>${fm.good}</b>/${fm.N}</span>
      <span class="fm-p">${Math.round(fm.pct * 100)}%</span></button>`;
  const legend = FM_BUCKETS.map(([k, label]) => `<span class="skey"><i class="fm-s ${k}"></i>${esc(label)}</span>`).join('');
  return `<div class="gr-sec-h fm-h"><h2 title="熟 = L0–L2.5 · 分母 = NeetCode 150 这组 + 其他题单里建过文件夹的">专题熟练度</h2>
      <div class="groupby"><button class="gb-btn${sort === 'plan' ? ' on' : ''}" data-fm-sort="plan">按顺序</button><button
        class="gb-btn${sort === 'weak' ? ' on' : ''}" data-fm-sort="weak">最生的在前</button></div></div>
    <div class="card fm-card"><div class="fm-list">${rows.map(row).join('')}</div>
    <div class="db-key fm-key">${legend}</div></div>`;
}

// 今天打过卡的题。用 .gr-chip 的壳, 点一下开详情这件事就白捡了(#grid-view 那个委托监听)
function todayHTML() {
  const today = todayStr();
  const recs = byId();
  const done = (ATTEMPTS || []).filter((a) => a.date === today).sort((a, b) => (a.ts || 0) - (b.ts || 0));
  if (!done.length) return '';
  const chips = done.map((a) => {
    const rec = recs.get(a.id);
    const L = rec ? famOf(rec) : null;
    const famTxt = (a.fam === null || a.fam === undefined) ? '未评' : 'L' + a.fam;
    return `<button class="gr-chip td-chip ${esc(a.kind)}" data-id="${a.id}"
        title="${esc(AT_META[a.kind] ? AT_META[a.kind].label : a.kind)} · 打卡时 ${esc(famTxt)}">
        <span class="gr-st s${depthOf(rec)} ${stCls(rec)}">${esc(famInfo(L).short)}</span>
        <span class="gr-id">${a.id}</span>
        <span class="gr-nm">${esc(rec ? rec.title : '')}</span></button>`;
  }).join('');
  return `<div class="td-done"><span class="td-done-k">今天打过卡</span>
      <div class="gr-chips td-chips">${chips}</div></div>`;
}

// ---- 攻坚 + mock ---------------------------------------------------------------
// 覆盖(格子)之外的两个数: 弱题还剩几道没关、随机没见过的题能不能做对。
// 弱题: server.weak_list 算(做过且当前 L3 / L3.5 / L4), 降到 L2.5 及以上就算关掉。
// mock: 抽题/记结果都在 server, 这里只画 + 计时。计时器只是显示, 不拦你。
let WEAK = null;
let MOCKS = null;
let MOCK_TIMER = null;
const lcUrl = (p) => (p.slug ? `https://leetcode.com/problems/${p.slug}/`
  : `https://leetcode.com/problemset/?search=${p.id}`);

function mockOpen(m) {                 // 还有题没记完(AC 和范式都要记)的那一轮, 且是这两天抽的
  // 以前只看 AC: 两题 AC 都勾完这轮就收起, 最后一题的范式没机会勾
  return m && m.date >= dAdd(todayStr(), -1)
    && m.problems.some((p) => {
      const r = (m.results || {})[p.id] || {};
      return r.ac === undefined || r.pattern === undefined;
    });
}

function mockWeeks() {
  const wk = new Map();
  for (const m of (MOCKS || [])) {
    const k = weekStart(m.date);
    const w = wk.get(k) || wk.set(k, { rounds: 0, n: 0, ac: 0, pat: 0, patN: 0 }).get(k);
    w.rounds++;
    for (const p of m.problems) {
      const r = (m.results || {})[p.id] || {};
      if (r.ac !== undefined) { w.n++; if (r.ac) w.ac++; }
      if (r.pattern !== undefined) { w.patN++; if (r.pattern) w.pat++; }
    }
  }
  return [...wk.entries()].sort((a, b) => b[0].localeCompare(a[0])).slice(0, 8);
}

function drillHTML() {
  const recs = byId();
  const chip = (id, title) => {
    const rec = recs.get(id);
    return `<button class="gr-chip" data-id="${id}" title="${esc(title)} — ${rec ? '点击打开题目' : '还没建文件夹 — 点击建'}">
      <span class="gr-st s${depthOf(rec)} ${stCls(rec)}">${rec ? esc(famInfo(famOf(rec)).short) : '+'}</span>
      <span class="gr-id">${id}</span><span class="gr-nm">${esc(title)}</span></button>`;
  };
  // 弱题
  const W = WEAK || { open: [], closed: [] };
  const wrow = (r) => `<div class="dr-w">
      ${chip(r.id, r.title)}
      <span class="dr-why">${esc(r.why)}</span>
      ${r.pit ? `<span class="dr-pit"><b>坑</b>${esc(r.pit)}</span>` : '<span class="dr-pit none" title="打开题目在「坑」里写一行">没写坑</span>'}
      ${r.cluster ? `<span class="dr-cl" title="变体簇">${esc(r.cluster)}</span>`
        : '<span class="dr-cl none" title="在详情页标签栏挂变体簇">没挂簇</span>'}</div>`;
  const weak = `<div class="dr-col">
      <div class="pc-sub-h" title="当前熟练度 L3 / L3.5 / L4 的题 · 降到 L2.5 及以上就关掉">
        <b>弱题 · 开着 ${W.open.length}</b><span class="hint">已关 ${W.closed.length}</span></div>
      ${W.open.length ? W.open.map(wrow).join('') : '<p class="empty-hint">没有开着的弱题</p>'}</div>`;

  // mock
  const cur = (MOCKS || []).slice().reverse().find(mockOpen);
  let mock;
  if (cur) {
    const res = cur.results || {};
    const yn = (p, k, v, t) => {
      const on = (res[p.id] || {})[k] === v;
      return `<button class="dr-yn${on ? ' on ' + (v ? 'y' : 'n') : ''}" data-mock="${esc(cur.mid)}"
        data-id="${p.id}" data-k="${k}" data-v="${v ? 1 : 0}">${t}</button>`;
    };
    mock = `<div class="dr-mock-cur">
        <div class="dr-mock-h"><b>这一轮 · ${esc(cur.date.slice(5))}${cur.mode === 'company' ? ' · 公司加权' : ''}</b>
          <span id="mock-timer" class="dr-timer" data-ts="${cur.ts}" data-min="${cur.minutes}"
            title="每题 ${cur.minutes} 分钟, 这是整轮的总时长 · 不看笔记题解, 先写下判断的范式再开写"></span>
          <button class="dr-drop" data-drop="${esc(cur.mid)}" title="抽错了/没开始做: 撤掉这一轮, 题放回池子">作废</button></div>
        ${cur.problems.map((p) => `<div class="dr-mp">
          <a href="${lcUrl(p)}" target="_blank" rel="noopener"><b>${p.id}</b> ${esc(p.title)}</a>
          <span class="hint">${esc(p.src || '')}</span>
          <span class="dr-yns">AC ${yn(p, 'ac', true, '✓')}${yn(p, 'ac', false, '✗')}
            　范式 ${yn(p, 'pattern', true, '✓')}${yn(p, 'pattern', false, '✗')}</span></div>`).join('')}</div>`;
  } else {
    const mc = PLAN.mock || {};
    const co = mc.company;
    mock = `<div class="dr-mock-cur"><button class="dr-draw" data-draw="unseen" title="${esc(mc.note || '')}"
      >抽 ${esc(String(mc.count || 2))} 道没见过的题</button>${co && co.list ? `
      <button class="dr-draw" data-draw="company" title="${esc(co.note || '')}"
      >按 ${esc(co.list)} 频率抽${co.mix ? ' · ' + co.mix.map((m) => ({ easy: '易', medium: '中', hard: '难' })[m] || m).join(' + ') : ''}</button>` : ''}</div>`;
  }
  const weeks = mockWeeks();
  const pct = (a, b) => (b ? Math.round((100 * a) / b) + '%' : '—');
  const hist = weeks.length ? `<table class="dr-hist"><thead><tr><th>周</th><th>轮</th><th>AC</th><th>范式对</th></tr></thead><tbody>${
    weeks.map(([k, w]) => `<tr><td>${esc(mmdd(k))}</td><td>${w.rounds}</td>
      <td>${w.ac}/${w.n} <small>${pct(w.ac, w.n)}</small></td><td>${w.pat}/${w.patN} <small>${pct(w.pat, w.patN)}</small></td></tr>`).join('')
  }</tbody></table>` : '<p class="empty-hint">还没做过 mock。</p>';

  return `<div class="dr-grid">${weak}
      <div class="dr-col"><div class="pc-sub-h" title="每周 1 次 · 只记 AC 和范式判断"><b>Mock</b></div>${mock}${hist}</div></div>`;
}

// ---- 专题(plan.topics): 按小节排的一组题, 不计进 NC150 进度、mock 不抽 ---------------
// 题卡和坐标系同一套壳, 点 + 建文件夹 / 点题名开详情都走 #grid-view 那个委托监听。
function topicsHTML() {
  const T = PLAN.topics || [];
  if (!T.length) return '';
  const recs = byId();
  const chip = (id, title, key) => {
    const rec = recs.get(id);
    return `<button class="gr-chip${key ? ' tp-key' : ''}" data-id="${id}" title="${key ? '本节代表题 · ' : ''}${esc(title)} — ${rec ? '点击打开题目' : '还没建文件夹 — 点击建'}">
      <span class="gr-st s${depthOf(rec)} ${stCls(rec)}">${rec ? esc(famInfo(famOf(rec)).short) : '+'}</span>
      <span class="gr-id">${id}</span><span class="gr-nm">${esc(title)}</span></button>`;
  };
  // 每节的代表题(sec.key)排第一个、加粗 —— 时间不够就只做这几道
  const ordered = (x) => [...x.problems].sort((a, b) => (b[0] === x.key) - (a[0] === x.key));
  const one = (t, i) => {
    const ids = t.sections.flatMap((x) => x.problems.map((p) => p[0]));
    const done = ids.filter((id) => depthOf(recs.get(id)) >= 2).length;
    const keys = t.sections.map((x) => x.key).filter(Boolean);
    const kdone = keys.filter((id) => depthOf(recs.get(id)) >= 2).length;
    return `<details class="tp"${i === 0 ? ' open' : ''}><summary><b>${esc(t.name)}</b>
        <span class="tp-c">${keys.length ? `代表题 ${kdone}/${keys.length} · ` : ''}全部 ${done}/${ids.length} 到 S2</span><span class="hint">${esc(t.note || '')}</span></summary>
      ${t.sections.map((x) => `<div class="tp-sec">${x.name ? `<div class="tp-sec-h">${esc(x.name)}</div>` : ''}
        ${x.note ? `<p class="tp-sec-note">${esc(x.note)}</p>` : ''}
        <div class="gr-chips">${ordered(x).map(([id, tt]) => chip(id, tt, id === x.key)).join('')}</div></div>`).join('')}
    </details>`;
  };
  return `<section class="gr-sec">${T.map(one).join('')}</section>`;
}

function tickMock() {
  const el = $('#mock-timer');
  if (!el) { clearInterval(MOCK_TIMER); MOCK_TIMER = null; return; }
  const total = (+el.dataset.min) * 60 * (MOCKS_CUR_N || 2);
  const gone = Math.floor(Date.now() / 1000) - (+el.dataset.ts);
  const left = total - gone;
  const f = (x) => `${Math.floor(Math.abs(x) / 60)}:${String(Math.abs(x) % 60).padStart(2, '0')}`;
  el.textContent = left >= 0 ? `剩 ${f(left)}` : `超时 ${f(left)}`;
  el.classList.toggle('over', left < 0);
}
let MOCKS_CUR_N = 2;

async function renderDrill() {
  if (!$('#gr-drill')) return;
  const jobs = [];
  if (WEAK === null) jobs.push(api('/api/weak').then((r) => { WEAK = r; }).catch(() => { WEAK = { open: [], closed: [] }; }));
  if (MOCKS === null) jobs.push(api('/api/mock').then((r) => { MOCKS = r.mocks || []; }).catch(() => { MOCKS = []; }));
  await Promise.all(jobs);
  const box = $('#gr-drill');
  if (!box) return;
  // 旧 server 没这两个接口 -> 返回 {error: "not found"}。别卡在"读取中", 直接说原因
  if (!WEAK || !Array.isArray(WEAK.open) || !Array.isArray(MOCKS)) {
    WEAK = null; MOCKS = null;
    box.innerHTML = `<p class="empty-hint">攻坚 · Mock 读不到 —— server 还是旧代码。
      Ctrl+C 停掉，重新 <span class="mono">python dashboard/server.py</span> 再刷新。</p>`;
    return;
  }
  try {
    box.innerHTML = drillHTML();
  } catch (e) {
    console.error('[drill]', e);
    box.innerHTML = `<p class="empty-hint">攻坚 · Mock 画不出来: ${esc(String(e))}</p>`;
    return;
  }
  const cur = (MOCKS || []).slice().reverse().find(mockOpen);
  MOCKS_CUR_N = cur ? cur.problems.length : 2;
  if (MOCK_TIMER) clearInterval(MOCK_TIMER);
  MOCK_TIMER = cur ? setInterval(tickMock, 1000) : null;
  if (cur) tickMock();
  const post = (body) => api('/api/mock', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  box.querySelectorAll('[data-draw]').forEach((draw) => draw.addEventListener('click', async () => {
    if (isReadOnly()) return;
    draw.disabled = true;
    const r = await post({ op: 'draw', mode: draw.dataset.draw });
    if (!r || r.ok === false) { flash((r && r.error) || '抽不出来'); draw.disabled = false; return; }
    MOCKS = null; renderDrill();
  }));
  box.querySelectorAll('[data-mock]').forEach((b) => b.addEventListener('click', async () => {
    if (isReadOnly()) return;
    const body = { op: 'result', mid: b.dataset.mock, id: +b.dataset.id };
    body[b.dataset.k] = b.dataset.v === '1';
    const r = await post(body);
    if (!r || r.ok === false) return void flash((r && r.error) || '记不上');
    MOCKS = null;
    const at = r.attempt;                 // 记 AC 时 server 顺手打了今天的卡
    if (at && at.ok === false) flash(at.error || '打卡没记上');
    else if (at && at.logged && !at.dup) {
      ATTEMPTS = null; WEAK = null;
      await loadAttempts();
      if (at.created) await reloadKeepOpen();   // 新建了文件夹, 看板格子要多一格
      renderDaily();
      flash(`#${b.dataset.id} 已记进今天的打卡`);
    }
    renderDrill();
  }));
  const drop = box.querySelector('[data-drop]');
  if (drop) drop.addEventListener('click', async () => {
    if (isReadOnly()) return;
    await post({ op: 'drop', mid: drop.dataset.drop });
    MOCKS = null; renderDrill();
  });
}

async function renderDaily() {
  if (!$('#gr-today')) return;
  await Promise.all([loadAttempts(), loadReviews()]);
  const act = activityByDay();
  const put = (sel, html) => { const el = $(sel); if (el) el.innerHTML = html; };   // 等的功夫可能已经重画了
  put('#gr-today', todayHTML());
  if (act) { put('#gr-heat', heatHTML(act)); put('#gr-bars', barsHTML(act)); }
  renderKpi();
}

// 坐标系要 plan.json; 每组下面那几个题单框要 lists.json —— 拉不到就只画 NeetCode 150
async function loadPlan() {
  if (!PLAN) PLAN = await api('/api/plan');
  if (!LISTS) { try { LISTS = await api('/api/lists'); } catch { LISTS = null; } }
}

async function reload() {
  await loadPlan();
  PROBLEMS = await api('/api/problems');
  // 语法牌组拉失败不能连累看板(只读站没导出这个文件时就会走到这) —— 空数组即可,
  // 队列自然是 0, 徽章上只剩题目那边的数字。
  try {
    SYNTAX = (await api('/api/syntax')).cards || [];
  } catch { SYNTAX = []; }
  SYNTAX.forEach((c, i) => { c.ord = i; });   // 书写顺序, 给「题号」那档排序用
  if (isReadOnly()) {
    // 别的设备推上来新事件时再 reload 一次: 行是重新拉的导出数据, 重放不会叠两遍
    await initSync(() => { reload(); });
    applyPending();
  }
  buildGrid();
  loadTodo();                          // 刷新 📋 TODO 上的角标
  renderPaused();                      // ⏸ 暂停上的角标
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
// 首屏「今日复习」那格 = 开复习。先把焦点从格子上拿走: 不然面板里按空格揭晓时,
// 事件先冒泡到这格的 keydown, 等于又点了一次「开复习」, 队列被重开。
const startReview = (tile) => { tile.blur(); RV.start(); };
on('#grid-view', 'click', (e) => {
  const rv = e.target.closest('[data-review]');
  if (rv) return void startReview(rv);
  const doc = e.target.closest('.gr-doc');
  if (doc) return void openDoc(doc.dataset.kind, doc.dataset.tag);
  const srt = e.target.closest('[data-fm-sort]');
  if (srt) {
    try { localStorage.setItem('lc-fm-sort', srt.dataset.fmSort); } catch { /* private mode */ }
    return void buildGrid();
  }
  // 专题熟练度那一行 -> 题目区里那一组。题目区和「低优先」都可能折着, 一路往外展开再跳
  const jump = e.target.closest('[data-jump-g]');
  if (jump) {
    const el = document.getElementById(`gr-g-${jump.dataset.jumpG}`);
    if (!el) return;
    for (let d = el.closest('details'); d; d = d.parentElement.closest('details')) d.open = true;
    el.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' });
    el.classList.remove('flash-hl'); void el.offsetWidth; el.classList.add('flash-hl');
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
on('#grid-view', 'keydown', (e) => {
  const rv = e.target.closest('[data-review]');
  if (rv && !RV.open && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); startReview(rv); }
});
on('#d-attempt', 'click', punchAttempt);
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
on('#e-paused', 'change', autoSaveMeta);
on('#e-pit', 'change', autoSaveMeta);
on('#e-cluster', 'change', autoSaveMeta);
on('#d-result', 'click', (e) => {
  const b = e.target.closest('.d-res');
  if (!b || !CURRENT) return;
  if (b.dataset.attack) {
    const a = attemptToday(CURRENT.id);
    return void setResult({ attack: !(a && a.attack) });
  }
  setResult({ result: b.dataset.res });
});
on('#d-res-pit', 'keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); setResult({ pit: e.target.value }); }
});

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

on('#overlay', 'click', (e) => { if (e.target.id === 'overlay') closeDetail(); });

// todo popover controls
on('#open-todo', 'click', (e) => { e.stopPropagation(); toggleTodoPop(); });
on('#todo-pop', 'click', (e) => e.stopPropagation());
on('#todo-in', 'keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addTodo(); }
});
document.addEventListener('click', closeTodoPop);      // 点别处收起

on('#open-paused', 'click', (e) => { e.stopPropagation(); togglePausedPop(); });
on('#paused-pop', 'click', (e) => e.stopPropagation());
on('#paused-in', 'keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); addPaused(); }
});
document.addEventListener('click', closePausedPop);

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
    if (!$('#paused-pop').classList.contains('hidden')) { closePausedPop(); return; }
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

reload();
