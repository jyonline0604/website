#!/usr/bin/env python3
"""Fix finance.html script issues - code fragments after </script> tags."""

with open('finance.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Issue 1: Line 1743 - loadFinanceNews code after </script>
# Fix: The </script> at line 1743 should have a <script> before the loadFinanceNews code
old_pattern1 = '''// SECURITY NOTE: Consider replacing innerHTML assignments with textContent
// or DOM manipulation methods to prevent XSS vulnerabilities.
// Example: element.textContent = value instead of element.innerHTML = value
</script>        // 載入財經新聞
        async function loadFinanceNews() {'''

new_pattern1 = '''// SECURITY NOTE: Consider replacing innerHTML assignments with textContent
// or DOM manipulation methods to prevent XSS vulnerabilities.
// Example: element.textContent = value instead of element.innerHTML = value
    </script>
    <script>
        // 載入財經新聞
        async function loadFinanceNews() {'''

if old_pattern1 in content:
    content = content.replace(old_pattern1, new_pattern1)
    print("Fixed issue 1: loadFinanceNews fragment")
else:
    print("Issue 1 pattern not found exactly, trying alternate...")

# Issue 2: Line 2018 - lazy loading code after </script>
old_pattern2 = '''});
            }
        });
    </script>
        // 圖片懶加載實現'''

new_pattern2 = '''});
            }
        });
    </script>
    <script>
        // 圖片懶加載實現'''

if old_pattern2 in content:
    content = content.replace(old_pattern2, new_pattern2)
    print("Fixed issue 2: lazy loading fragment")
else:
    print("Issue 2 pattern not found")

# Issue 3: Line 2114 - service worker code after </script>
old_pattern3 = '''});
            }
        });
    </script>
        // 註冊Service Worker'''

new_pattern3 = '''});
            }
        });
    </script>
    <script>
        // 註冊Service Worker'''

if old_pattern3 in content:
    content = content.replace(old_pattern3, new_pattern3)
    print("Fixed issue 3: service worker fragment")
else:
    print("Issue 3 pattern not found")

# Also fix any remaining orphaned script code
# The PWA service worker code at the end should be wrapped in a script tag
old_pwa = '''        // 註冊Service Worker
            
            // 離線狀態檢測
            window.addEventListener('online', function() {
                document.documentElement.classList.remove('offline');
            });
            
            window.addEventListener('offline', function() {
                document.documentElement.classList.add('offline');
            });
            
            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
        
        // 添加到主屏幕提示（僅在移動端顯示）
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', function(e) {
            // 防止Chrome 67及更早版本自動顯示提示
            e.preventDefault();
            deferredPrompt = e;
            
            // 顯示添加到主屏幕按鈕
            const installBtn = document.getElementById('install-pwa-btn');
            if (installBtn) {
                installBtn.style.display = 'block';
                installBtn.addEventListener('click', function() {
                    // 顯示安裝提示
                    deferredPrompt.prompt();
                    
                    // 等待用戶選擇
                    deferredPrompt.userChoice.then(function(choiceResult) {
                        if (choiceResult.outcome === 'accepted') {
                            } else {
                            }
                        deferredPrompt = null;
                    });
                });
            }
        });
    
    <script src="assets/main.js" defer></script>'''

new_pwa = '''        // 註冊Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js').then(function(registration) {
                    console.log('ServiceWorker registered: ', registration);
                }).catch(function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }
            
            // 離線狀態檢測
            window.addEventListener('online', function() {
                document.documentElement.classList.remove('offline');
            });
            
            window.addEventListener('offline', function() {
                document.documentElement.classList.add('offline');
            });
            
            // 初始檢查
            if (!navigator.onLine) {
                document.documentElement.classList.add('offline');
            }
        
        // 添加到主屏幕提示（僅在移動端顯示）
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', function(e) {
            // 防止Chrome 67及更早版本自動顯示提示
            e.preventDefault();
            deferredPrompt = e;
            
            // 顯示添加到主屏幕按鈕
            const installBtn = document.getElementById('install-pwa-btn');
            if (installBtn) {
                installBtn.style.display = 'block';
                installBtn.addEventListener('click', function() {
                    // 顯示安裝提示
                    deferredPrompt.prompt();
                    
                    // 等待用戶選擇
                    deferredPrompt.userChoice.then(function(choiceResult) {
                        if (choiceResult.outcome === 'accepted') {
                            } else {
                            }
                        deferredPrompt = null;
                    });
                });
            }
        });
    </script>
    
    <script src="assets/main.js" defer></script>'''

if old_pwa in content:
    content = content.replace(old_pwa, new_pwa)
    print("Fixed PWA service worker code")
else:
    print("PWA pattern not found")

with open('finance.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
