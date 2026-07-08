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
var prevLink = document.getElementById('prevLink');
if (!prevLink.href || prevLink.href.includes('#')) {
prevLink.style.opacity = '0.5';
prevLink.style.pointerEvents = 'none';
}