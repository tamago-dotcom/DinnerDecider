/* Service Worker for 気分メシ！ */

const CACHE_NAME = 'kibun-meshi-v1';
const OFFLINE_CACHE = [
  '/',
  '/static/css/style.css',
];

// インストール: トップ画面と主要アセットをキャッシュ
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_CACHE))
  );
  self.skipWaiting();
});

// アクティベート: 古いキャッシュを削除
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// フェッチ: ナビゲーションリクエストのみオフラインフォールバック
self.addEventListener('fetch', (event) => {
  if (event.request.mode !== 'navigate') return;
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match('/').then(
        (r) => r || new Response(
          '<html lang="ja"><body style="font-family:sans-serif;text-align:center;padding:40px">' +
          '<h1>🍽️ 気分メシ！</h1><p>オフラインのため表示できません。<br>インターネットに接続してください。</p>' +
          '</body></html>',
          { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
        )
      )
    )
  );
});
