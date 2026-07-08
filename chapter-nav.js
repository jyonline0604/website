(function () {
'use strict';
var prevHref = '';
var nextHref = '';
var chapterNum = '';
// Extract prev/next from <link> or bottom nav
var prevLink = document.querySelector('link[rel="prev"]');
var nextLink = document.querySelector('link[rel="next"]');
if (prevLink) prevHref = prevLink.getAttribute('href');
if (nextLink) nextHref = nextLink.getAttribute('href');
// Extract chapter number from title
var titleMatch = document.title.match(/第(\d+)章/);
if (titleMatch) chapterNum = titleMatch[1];
if (!prevHref && !nextHref && !chapterNum) return;
var css = ''
+ '#kofhk-fab-nav { position:fixed; bottom:0; left:0; right:0; z-index:99; '
+ 'background:var(--panel-bg,#fff); border-top:1px solid var(--border,#e5e7eb); '
+ 'display:none; align-items:center; justify-content:space-between; '
+ 'padding:8px 16px; padding-bottom:max(8px,env(safe-area-inset-bottom)); '
+ 'box-shadow:0 -2px 10px rgba(0,0,0,0.08); transition:background 0.3s; }'
+ '#kofhk-fab-nav a, #kofhk-fab-nav button { '
+ 'background:var(--accent,#6366F1); color:#fff; border:none; '
+ 'padding:8px 16px; border-radius:6px; text-decoration:none; '
+ 'font-size:14px; cursor:pointer; white-space:nowrap; }'
+ '#kofhk-fab-nav a.kofhk-fab-toc { background:transparent; color:var(--text,#1f2937); '
+ 'border:1px solid var(--border,#e5e7eb); }'
+ '#kofhk-fab-nav .kofhk-fab-progress { font-size:12px; color:var(--text,#1f2937); '
+ 'opacity:0.6; text-align:center; flex:1; }'
+ '@media (max-width:600px) { #kofhk-fab-nav { display:flex; } '
+ 'body { padding-bottom:80px !important; } '
+ '.back-to-top { bottom:70px !important; } }';
var style = document.createElement('style');
style.textContent = css;
document.head.appendChild(style);
// Read progress
var readPct = 0;
function updateProgress() {
var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
var docHeight = document.documentElement.scrollHeight - window.innerHeight;
readPct = docHeight > 0 ? Math.round((scrollTop / docHeight) * 100) : 0;
var el = document.getElementById('kofhkFabProgress');
if (el) el.textContent = readPct + '%';
}
var bar = document.createElement('div');
bar.id = 'kofhk-fab-nav';
bar.innerHTML = ''
+ (prevHref ? '<a href="' + prevHref + '" id="kofhkFabPrev">← 上一章</a>' : '<span></span>')
+ '<span class="kofhk-fab-progress" id="kofhkFabProgress">0%</span>'
+ (nextHref ? '<a href="' + nextHref + '" id="kofhkFabNext">下一章 →</a>'
: '<a href="chapters.html" class="kofhk-fab-toc">📖 目錄</a>');
document.body.appendChild(bar);
window.addEventListener('scroll', updateProgress, { passive: true });
updateProgress();
})();