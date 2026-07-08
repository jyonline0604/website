document.getElementById('themeSelect').addEventListener('change', function() {
document.body.dataset.theme = this.value;
localStorage.setItem('novelTheme', this.value);
});
var savedTheme = localStorage.getItem('novelTheme');
if (savedTheme) {
document.body.dataset.theme = savedTheme;
document.getElementById('themeSelect').value = savedTheme;
}
document.getElementById('fontSize').addEventListener('change', function() {
document.body.style.setProperty('--font-size', this.value);
localStorage.setItem('novelFont', this.value);
});
var savedFont = localStorage.getItem('novelFont');
if (savedFont) {
document.body.style.setProperty('--font-size', savedFont);
document.getElementById('fontSize').value = savedFont;
}
window.addEventListener('scroll', function() {
var btn = document.getElementById('backToTop');
btn.classList.toggle('visible', window.pageYOffset > 300);
});
(function(){
var main = document.querySelector('main');
if (main) {
var chars = main.textContent.replace(/\s/g, '').length;
var minutes = Math.max(1, Math.round(chars / 400));
var span = document.createElement('span');
span.style.cssText = 'display:block;text-align:center;color:var(--text);opacity:0.6;font-size:0.85em;margin-top:-20px;margin-bottom:20px';
span.textContent = '預計閱讀：' + minutes + ' 分鐘（約 ' + chars + ' 字）';
var h1 = document.querySelector('h1');
if (h1) h1.insertAdjacentElement('afterend', span);
}
})();
var prevLink = document.getElementById('prevLink');
if (prevLink && (!prevLink.href || prevLink.href.includes('#'))) {
prevLink.style.opacity = '0.5';
prevLink.style.pointerEvents = 'none';
}