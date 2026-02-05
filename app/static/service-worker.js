const CACHE_NAME = 'tt-agenda-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/shared/css/output.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];

// Installation - Cache wichtige Ressourcen
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('Service Worker: Cache error', err))
  );
  self.skipWaiting();
});

// Aktivierung - Alte Caches löschen
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch - Network First, dann Cache (für Live-Daten)
self.addEventListener('fetch', event => {
  // Für API-Anfragen: Network First
  if (event.request.url.includes('/live') || 
      event.request.url.includes('/api/') ||
      event.request.method !== 'GET') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Für statische Ressourcen: Cache First
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request).then(response => {
          // Nur erfolgreiche Antworten cachen
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// Background Sync für Offline-Aktionen (optional)
self.addEventListener('sync', event => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Hier könntest du Offline-Daten synchronisieren
  console.log('Service Worker: Background sync');
}
