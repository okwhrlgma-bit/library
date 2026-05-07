// kormarc-auto Service Worker (Cycle 70·PWA)
// 사서 모바일 친화·오프라인 지원·앱스토어 X·핸드폰 홈 추가

const CACHE_NAME = 'kormarc-auto-v0.7.1';
const ASSETS = [
  '/library/',
  '/library/index.html',
  '/library/manifest.json',
  '/library/about.md',
  '/library/install.md'
];

// 설치 = ASSETS 캐시
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// 활성화 = 오래된 캐시 정리
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names.filter((name) => name !== CACHE_NAME).map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim();
});

// fetch = 네트워크 우선·실패 시 캐시 (사서 모바일 = 인터넷 불안정 대비)
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 성공 = 캐시 갱신 + 응답
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          if (event.request.url.startsWith(self.location.origin)) {
            cache.put(event.request, clone);
          }
        });
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// 알림 (Phase 2·푸시 알림 활성 시)
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : { title: 'kormarc-auto', body: '새 알림' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/library/icon-192.png',
      badge: '/library/icon-72.png',
      lang: 'ko'
    })
  );
});
