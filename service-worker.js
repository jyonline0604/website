// 萬古塵埃 - Optimized Service Worker
// 版本: 2.3.0 (移至根目錄修正 scope；修正舊快取清理邏輯；移除無用 Google Fonts 預快取)
// 日期: 2026-07-24

const CACHE_VERSION = 'v2.3.0';
const CACHE_NAME = 'tech-cultivation-' + CACHE_VERSION;
const STATIC_CACHE = 'static-assets-' + CACHE_VERSION;
const DYNAMIC_CACHE = 'dynamic-data-' + CACHE_VERSION;
const IMAGE_CACHE = 'images-' + CACHE_VERSION;

// 靜態資源（長期緩存）
const staticUrls = [
  '/',
  '/index.html',
  '/home.html',
  '/chapters.html',
  // '/av-novels.html' — removed, page does not exist
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
  '/assets/main.js',
  '/assets/chapters-data.json',
  '/assets/fonts/master.css'
];

// 安裝 - 預載靜態資源
self.addEventListener('install', event => {
  if (typeof console !== 'undefined') {
    console.log('[Service Worker] 安裝中，版本:', CACHE_NAME);
  }
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(staticUrls))
      .then(() => self.skipWaiting())
      .catch(err => console.error('Install failed:', err))
  );
});

// 激活 - 清理舊緩存
self.addEventListener('activate', event => {
  const KEEP_CACHES = [CACHE_NAME, STATIC_CACHE, DYNAMIC_CACHE, IMAGE_CACHE];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(name => {
          // 刪除所有非當前版本的緩存（避免舊版本無限累積）
          if (!KEEP_CACHES.includes(name)) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 智能攔截策略
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // 跳過非 GET 請求
  if (request.method !== 'GET') return;
  
  // 跳過瀏覽器擴展
  if (url.protocol === 'chrome-extension:') return;
  
  // 策略 1: API/動態數據 - Network First
  if (url.pathname.includes('/api/') || url.searchParams.has('callback')) {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    return;
  }
  
  // 策略 2: 圖片 - Stale While Revalidate
  if (url.pathname.match(/\.(jpg|jpeg|png|gif|webp|avif)$/)) {
    event.respondWith(staleWhileRevalidate(request, IMAGE_CACHE));
    return;
  }
  
  // 策略 3: HTML/主要頁面 - Stale While Revalidate（先給快取，背景更新）
  if (request.headers.get('accept') && request.headers.get('accept').includes('text/html')) {
    event.respondWith(staleWhileRevalidate(request, STATIC_CACHE));
    return;
  }
  
  // 策略 4: 其他靜態資源 - Cache First
  event.respondWith(cacheFirst(request, STATIC_CACHE));
});

// Cache First 策略（適合靜態資源）
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('Cache first failed:', request.url);
    return new Response('Offline', { status: 503 });
  }
}

// Network First 策略（適合 API/動態數據）
async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // 網絡失敗時返回緩存
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    console.error('Network first failed:', request.url);
    return new Response('Offline', { status: 503 });
  }
}

// Stale While Revalidate（適合圖片）
async function staleWhileRevalidate(request, cacheName) {
  const cached = await caches.match(request);
  
  // 立即返回緩存（如果有）
  if (cached) {
    // 在後台更新緩存
    fetch(request).then(response => {
      if (response.ok) {
        caches.open(cacheName).then(cache => cache.put(request, response));
      }
    }).catch(() => {});
    
    return cached;
  }
  
  // 沒有緩存時從網絡獲取
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('Stale while revalidate failed:', request.url);
    return new Response('Offline', { status: 503 });
  }
}

// 後台同步（可选，用于离线操作）
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(backgroundSync());
  }
});

async function backgroundSync() {
  // 處理離線隊列中的請求
  console.log('[Service Worker] 後台同步');
}

// 推送通知（可选）
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || '科技修真傳更新';
  const options = {
    body: data.body || '有新的章節更新了！',
    icon: '/assets/favicon-96x96.png',
    badge: '/assets/favicon-32x32.png'
  };
  
  event.waitUntil(self.registration.showNotification(title, options));
});

console.log('[Service Worker] 已激活，版本:', CACHE_NAME);
