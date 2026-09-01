'use strict';
// 只读静态构建(GitHub Pages)的适配层 —— 本地跑 server.py 时这个文件不会被加载。
//
// 干三件事:
//   1. 把 app.js 的 fetch 改道到 export_static.py 导出的 .json 文件;
//   2. 写请求(PUT/POST)一律就地拒绝, 不出网;
//   3. 关掉所有编辑入口(双击进编辑 / Ctrl+S), 配合 ro.css 把按钮藏掉。
// app.js 本身一行没改, 本地那份仍然是可写的完整看板。
(function () {
  const BASE = new URL('.', document.baseURI);   // 支持挂在 /leetcode/ 这种子路径下
  const realFetch = window.fetch.bind(window);
  const json = (obj, status) =>
    new Response(JSON.stringify(obj), {
      status: status || 200,
      headers: { 'Content-Type': 'application/json' },
    });

  document.documentElement.classList.add('ro');

  // 请求路径里没被 URL 解码, 所以 encodeURIComponent 过的中文名能直接对上磁盘文件名
  function apiTail(u) {
    const m = /\/api\/(.+)$/.exec(u.pathname);
    return m ? m[1] : null;
  }

  // 导出时被剔掉的东西(notes/todo.md 之类)会 404, 给个空壳别让前端炸
  function fallback(tail) {
    if (tail.startsWith('notes/')) {
      return { file: decodeURIComponent(tail.slice('notes/'.length)), content: '' };
    }
    return {};
  }

  window.fetch = function (input, opt) {
    const raw = typeof input === 'string' ? input : input.url;
    const u = new URL(raw, document.baseURI);
    const tail = apiTail(u);
    if (tail === null) return realFetch(input, opt);          // 非 API 的照常走

    const method = ((opt && opt.method) || 'GET').toUpperCase();
    if (method !== 'GET') return Promise.resolve(json({ ok: false, readonly: true }, 403));

    return realFetch(new URL('api/' + tail + '.json', BASE))
      .then((r) => (r.ok ? r : json(fallback(tail))))
      .catch(() => json(fallback(tail)));
  };

  // 编辑入口都挂在元素自己身上, 在 document 上捕获阶段拦一道就够了
  document.addEventListener('dblclick', (e) => e.stopPropagation(), true);
  document.addEventListener(
    'keydown',
    (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {        // 否则会弹"已保存 ✓"的假消息
        e.preventDefault();
        e.stopPropagation();
      }
    },
    true
  );

  // app.js 是同步跑完的, 所以这里拿到的是它初始化之后的 DOM
  document.addEventListener('DOMContentLoaded', () => {
    ['#e-difficulty', '#e-status', '#e-familiarity'].forEach((s) => {
      const el = document.querySelector(s);
      if (el) el.disabled = true;                             // disabled 不影响 app.js 写 .value
    });
    const actions = document.querySelector('header .actions');
    if (actions) {
      const b = document.createElement('span');
      b.className = 'ro-badge';
      b.innerHTML = '只读 · <a href="https://github.com/scatyf3/leetcode">源码</a>';
      actions.appendChild(b);
    }
  });
})();
