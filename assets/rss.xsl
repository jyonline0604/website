<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/rss/channel">
<html lang="zh-Hant">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title><xsl:value-of select="title"/> — RSS 訂閱</title>
<link rel="stylesheet" href="assets/fonts/master.css"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans TC',-apple-system,sans-serif;background:#0a0a0f;color:#e0e0e0;min-height:100vh}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(10,10,15,.85);z-index:-1;pointer-events:none}
header{background:rgba(0,0,0,.5);backdrop-filter:blur(8px);border-bottom:1px solid rgba(255,255,255,.1);padding:15px 0;text-align:center}
header h1{font-size:1.3rem;color:#00d4ff}
header p{color:rgba(255,255,255,.5);font-size:.75rem;margin-top:4px}
.container{max-width:720px;margin:0 auto;padding:20px}
.info{background:rgba(255,255,255,.05);border-radius:12px;padding:20px;margin-bottom:20px;text-align:center}
.info h2{color:#fff;font-size:1.1rem;margin-bottom:6px}
.info p{color:rgba(255,255,255,.6);font-size:.8rem;line-height:1.6}
.info .copy-btn{margin-top:10px;padding:8px 20px;background:#00d4ff;color:#000;border:none;border-radius:20px;font-size:.8rem;font-weight:600;cursor:pointer}
.info .copy-btn:active{opacity:.8}
.item{display:flex;align-items:center;padding:12px 16px;background:rgba(255,255,255,.04);border-radius:10px;margin-bottom:6px;transition:background .2s}
.item:hover{background:rgba(0,212,255,.1)}
.item-num{color:#00d4ff;font-weight:700;font-size:.85rem;min-width:80px}
.item-title{flex:1;font-size:.85rem;color:#e0e0e0}
.item-title a{color:#e0e0e0;text-decoration:none}
.item-title a:hover{color:#00d4ff}
.item-date{font-size:.7rem;color:rgba(255,255,255,.35);min-width:100px;text-align:right}
footer{text-align:center;padding:30px;color:rgba(255,255,255,.3);font-size:.7rem}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#00d4ff;color:#000;padding:10px 24px;border-radius:20px;font-size:.8rem;font-weight:600;opacity:0;transition:opacity .3s}
.toast.show{opacity:1}
</style>
</head>
<body>
<header>
<h1>📡 <xsl:value-of select="title"/> · RSS 訂閱</h1>
<p><xsl:value-of select="description"/></p>
</header>
<div class="container">
<div class="info">
<h2>🔗 訂閱連結</h2>
<p id="feedUrl"><xsl:value-of select="atom:link/@href"/></p>
<button class="copy-btn" onclick="copyFeedUrl()">📋 複製 RSS 連結</button>
<p style="font-size:.65rem;margin-top:8px;opacity:.5">將此連結加入你的 RSS 閱讀器即可訂閱更新</p>
</div>
<xsl:for-each select="item">
<div class="item">
<div class="item-num"><xsl:value-of select="substring-before(substring-after(title,'第'),'章')"/> 章</div>
<div class="item-title">
<a href="{link}"><xsl:value-of select="substring-after(title,'· ')"/></a>
</div>
<div class="item-date"><xsl:value-of select="pubDate"/></div>
</div>
</xsl:for-each>
</div>
<footer>共 <xsl:value-of select="count(item)"/> 章 · 作者：<xsl:value-of select="item[1]/author"/> · <a href="/" style="color:#00d4ff;text-decoration:none">返回首頁</a></footer>
<div class="toast" id="toast">已複製！</div>
<script>
function copyFeedUrl() {
var el=document.getElementById('feedUrl');
var url=el.textContent.trim();
navigator.clipboard.writeText(url).then(function(){
var t=document.getElementById('toast');
t.classList.add('show');
setTimeout(function(){t.classList.remove('show')},1500);
});
}
</script>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
