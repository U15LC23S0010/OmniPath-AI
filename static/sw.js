
const CACHE_NAME = 'omnipath-pwa-v2';

const CACHED_URLS = [
    '/',
    '/dashboard',
    '/static/css/style.css'
];

// Install the service worker and cache essential files.
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(CACHED_URLS))
            .catch((error) => {
                console.warn('Cache initialization failed:', error);
            })
    );

    self.skipWaiting();
});

// Activate the new service worker and remove old caches.
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) =>
                Promise.all(
                    keys
                        .filter((key) => key !== CACHE_NAME)
                        .map((key) => caches.delete(key))
                )
            )
            .then(() => self.clients.claim())
    );
});

// Handle requests safely.
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // Do not intercept external requests such as Google Fonts.
    if (url.origin !== self.location.origin) {
        return;
    }

    // Only handle GET requests.
    if (request.method !== 'GET') {
        return;
    }

    // API requests must reach the Flask backend directly.
    if (url.pathname.startsWith('/api/')) {
        return;
    }

    event.respondWith(
        fetch(request)
            .then((response) => {
                // Cache successful responses for offline use.
                if (response && response.ok) {
                    const responseCopy = response.clone();

                    caches.open(CACHE_NAME)
                        .then((cache) => cache.put(request, responseCopy))
                        .catch((error) => {
                            console.warn('Unable to cache response:', error);
                        });
                }

                return response;
            })
            .catch(async () => {
                // Use a cached response when the network is unavailable.
                const cachedResponse = await caches.match(request);

                if (cachedResponse) {
                    return cachedResponse;
                }

                // Always return a valid Response object.
                return new Response(
                    'Offline: this resource is unavailable.',
                    {
                        status: 503,
                        statusText: 'Service Unavailable',
                        headers: {
                            'Content-Type': 'text/plain; charset=utf-8'
                        }
                    }
                );
            })
    );
});
