// 科技修真傳 - Service Worker
// 版本: 1.0.0
// 日期: 2026-04-18

const CACHE_NAME = 'tech-cultivation-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/home.html',
  '/chapters.html',
  '/av-novels.html',
  '/author.html',
  '/news.html',
  '/finance.html',
  '/dashboard.html',
  
  // 核心資源
  '/assets/favicon.ico',
  '/assets/favicon-32x32.png',
  '/assets/favicon-16x16.png',
  '/assets/apple-touch-icon.png',
  '/assets/book-cover.png',
  '/assets/site.webmanifest',
  
  // 字體（可選）
  'https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;700&family=Noto+Sans+TC:wght@300;400;500;700&display=swap'
];

// 安裝Service Worker
self.addEventListener('install', event => {
  // 只在需要時才記錄
  if (typeof console !== 'undefined') {
    console.log('[Service Worker] 安裝中...');
  }
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        return self.skipWaiting();
      })
      .catch(error => {
        if (typeof console !== 'undefined') {
          console.error('[Service Worker] 安裝失敗:', error);
        }
      })
  );
});

// 激活Service Worker
self.addEventListener('activate', event => {
  // 清理舊緩存
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            if (typeof console !== 'undefined') {
              console.log('[Service Worker] 刪除舊緩存:', cacheName);
            }
            return caches.delete(cacheName);
          }
        })
      );
    })
    .then(() => {
      return self.clients.claim();
    })
  );
});

// 攔截網絡請求
self.addEventListener('fetch', event => {
  // 跳過非GET請求
  if (event.request.method !== 'GET') return;
  
  // 跳過瀏覽器擴展請求
  if (event.request.url.startsWith('chrome-extension://')) return;
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 如果有緩存，返回緩存
        if (response) {
          return response;
        }
        
        // 否則從網絡獲取
        return fetch(event.request)
          .then(networkResponse => {
            // 檢查是否有效響應
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }
            
            // 緩存新資源
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            
            return networkResponse;
          })
          .catch(error => {
            // 對於HTML頁面，返回離線頁面
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline.html')
                .then(offlineResponse => offlineResponse || caches.match('/home.html'));
            }
            
            // 對於其他資源，返回緩存的替代資源
            if (event.request.destination === 'image') {
              return caches.match('/assets/book-cover.png');
            }
            
            // 返回錯誤響應
            return new Response('網絡連接失敗，請檢查網絡連接後重試。', {
              status: 408,
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          });
      })
  );
});

// 後台同步（如果瀏覽器支持）
self.addEventListener('sync', event => {
  if (event.tag === 'sync-news') {
    console.log('[Service Worker] 後台同步: 新聞更新');
    event.waitUntil(syncNews());
  }
});

// 推送通知（如果瀏覽器支持）
self.addEventListener('push', event => {
  console.log('[Service Worker] 收到推送通知');
  
  const options = {
    body: event.data ? event.data.text() : '《科技修真傳》有新章節更新！',
    icon: '/assets/favicon-192x192.png',
    badge: '/assets/favicon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '閱讀新章節',
        icon: '/assets/favicon-32x32.png'
      },
      {
        action: 'close',
        title: '關閉',
        icon: '/assets/favicon-32x32.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('科技修真傳', options)
  );
});

// 通知點擊處理
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] 通知被點擊');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    // 打開網站
    event.waitUntil(
      clients.openWindow('https://kofhk.com')
    );
  } else {
    // 默認打開首頁
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// 輔助函數
function syncNews() {
  // 這裡可以實現後台數據同步
  return fetch('/api/news/latest')
    .then(response => response.json())
    .then(data => {
      console.log('[Service Worker] 新聞同步完成:', data);
      return data;
    })
    .catch(error => {
      console.error('[Service Worker] 新聞同步失敗:', error);
    });
}

console.log('[Service Worker] 加載完成');