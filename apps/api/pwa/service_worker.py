"""
Service Worker Generator for PWA Offline Capabilities
Generates customized service worker JavaScript for caching and offline functionality
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from config.settings import settings


class ServiceWorkerGenerator:
    """Generate service worker JavaScript for PWA functionality"""
    
    def __init__(self):
        self.cache_version = f"seraaj-v{settings.api.version}-{datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M')}"
        self.static_cache_name = f"{self.cache_version}-static"
        self.dynamic_cache_name = f"{self.cache_version}-dynamic"
        self.api_cache_name = f"{self.cache_version}-api"
        
    def generate_service_worker(
        self,
        caching_strategy: str = "network_first",
        offline_pages: Optional[List[str]] = None,
        api_endpoints_to_cache: Optional[List[str]] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate complete service worker JavaScript"""
        
        options = custom_options or {}
        offline_pages = offline_pages or self._get_default_offline_pages()
        api_endpoints = api_endpoints_to_cache or self._get_default_api_endpoints()
        
        sw_code = f"""
// Seraaj PWA Service Worker
// Generated: {datetime.now(datetime.timezone.utc).isoformat()}
// Version: {self.cache_version}

{self._generate_constants()}

{self._generate_install_event(offline_pages)}

{self._generate_activate_event()}

{self._generate_fetch_event(caching_strategy, api_endpoints)}

{self._generate_background_sync()}

{self._generate_push_notification_handler()}

{self._generate_utility_functions()}

{self._generate_custom_handlers(options)}
"""
        return sw_code.strip()
    
    def _generate_constants(self) -> str:
        """Generate service worker constants"""
        
        return f"""
// Cache names
const STATIC_CACHE = '{self.static_cache_name}';
const DYNAMIC_CACHE = '{self.dynamic_cache_name}';
const API_CACHE = '{self.api_cache_name}';

// Cache configuration
const CACHE_CONFIG = {{
    maxEntries: 100,
    maxAgeSeconds: 24 * 60 * 60, // 24 hours
    purgeOnQuotaError: true
}};

// Network timeout
const NETWORK_TIMEOUT = 3000; // 3 seconds

// Offline fallbacks
const OFFLINE_PAGE = '/offline.html';
const OFFLINE_IMAGE = '/static/images/offline-placeholder.svg';
const OFFLINE_AVATAR = '/static/images/default-avatar.svg';
"""
    
    def _generate_install_event(self, offline_pages: List[str]) -> str:
        """Generate install event handler"""
        
        static_resources = [
            '/',
            '/static/css/app.css',
            '/static/js/app.js',
            '/static/icons/icon-192x192.png',
            '/static/icons/icon-512x512.png',
            '/static/images/logo.svg',
            '/offline.html',
            '/static/images/offline-placeholder.svg'
        ] + offline_pages
        
        return f"""
// Install event - cache static resources
self.addEventListener('install', event => {{
    console.log('[SW] Installing service worker...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {{
                console.log('[SW] Caching static resources');
                return cache.addAll({json.dumps(static_resources, indent=16)});
            }})
            .then(() => {{
                console.log('[SW] Static resources cached successfully');
                return self.skipWaiting();
            }})
            .catch(error => {{
                console.error('[SW] Failed to cache static resources:', error);
            }})
    );
}});
"""
    
    def _generate_activate_event(self) -> str:
        """Generate activate event handler"""
        
        return """
// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(cacheName => {
                            // Delete old version caches
                            return cacheName.startsWith('seraaj-v') && 
                                   cacheName !== STATIC_CACHE && 
                                   cacheName !== DYNAMIC_CACHE && 
                                   cacheName !== API_CACHE;
                        })
                        .map(cacheName => {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
            .catch(error => {
                console.error('[SW] Error during activation:', error);
            })
    );
});
"""
    
    def _generate_fetch_event(self, strategy: str, api_endpoints: List[str]) -> str:
        """Generate fetch event handler with caching strategies"""
        
        strategies = {
            "cache_first": self._cache_first_strategy(),
            "network_first": self._network_first_strategy(),
            "stale_while_revalidate": self._stale_while_revalidate_strategy(),
            "network_only": self._network_only_strategy(),
            "cache_only": self._cache_only_strategy()
        }
        
        strategy_code = strategies.get(strategy, strategies["network_first"])
        
        return f"""
// Fetch event - handle network requests
self.addEventListener('fetch', event => {{
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-HTTP requests
    if (!request.url.startsWith('http')) {{
        return;
    }}
    
    // Handle different types of requests
    if (isAPIRequest(url)) {{
        event.respondWith(handleAPIRequest(request));
    }} else if (isImageRequest(url)) {{
        event.respondWith(handleImageRequest(request));
    }} else if (isStaticResource(url)) {{
        event.respondWith(handleStaticResource(request));
    }} else if (isPageRequest(request)) {{
        event.respondWith(handlePageRequest(request));
    }} else {{
        event.respondWith(handleGenericRequest(request));
    }}
}});

{strategy_code}

// Request type detection
function isAPIRequest(url) {{
    return url.pathname.startsWith('/v1/') || 
           {json.dumps(api_endpoints)}.some(endpoint => url.pathname.startsWith(endpoint));
}}

function isImageRequest(url) {{
    return /\\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url.pathname);
}}

function isStaticResource(url) {{
    return url.pathname.startsWith('/static/') || 
           /\\.(css|js|woff|woff2|ttf|eot)$/i.test(url.pathname);
}}

function isPageRequest(request) {{
    return request.method === 'GET' && 
           request.headers.get('accept') && 
           request.headers.get('accept').includes('text/html');
}}
"""
    
    def _network_first_strategy(self) -> str:
        """Generate network-first caching strategy"""
        
        return """
// Network-first strategy handlers
async function handleAPIRequest(request) {
    try {
        // Try network first with timeout
        const networkResponse = await Promise.race([
            fetch(request),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Network timeout')), NETWORK_TIMEOUT)
            )
        ]);
        
        // Cache successful GET requests
        if (networkResponse.ok && request.method === 'GET') {
            const cache = await caches.open(API_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.log('[SW] Network failed for API request, trying cache:', error);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline API response
        return createOfflineAPIResponse(request);
    }
}

async function handleImageRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        // Try cache first for images
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline placeholder
        return caches.match(OFFLINE_IMAGE);
    }
}

async function handleStaticResource(request) {
    // Static resources: cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('[SW] Failed to load static resource:', error);
        throw error;
    }
}

async function handlePageRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        // Try cache for pages
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match(OFFLINE_PAGE);
    }
}

async function handleGenericRequest(request) {
    try {
        return await fetch(request);
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}
"""
    
    def _cache_first_strategy(self) -> str:
        """Generate cache-first strategy for static resources"""
        
        return """
// Cache-first strategy (for static resources)
async function handleStaticResource(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    
    return networkResponse;
}
"""
    
    def _stale_while_revalidate_strategy(self) -> str:
        """Generate stale-while-revalidate strategy"""
        
        return """
// Stale-while-revalidate strategy
async function handleStaleWhileRevalidate(request) {
    const cachedResponse = await caches.match(request);
    
    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    });
    
    return cachedResponse || fetchPromise;
}
"""
    
    def _network_only_strategy(self) -> str:
        """Generate network-only strategy"""
        
        return """
// Network-only strategy (for sensitive data)
async function handleNetworkOnly(request) {
    return fetch(request);
}
"""
    
    def _cache_only_strategy(self) -> str:
        """Generate cache-only strategy"""
        
        return """
// Cache-only strategy (for offline-first content)
async function handleCacheOnly(request) {
    return caches.match(request);
}
"""
    
    def _generate_background_sync(self) -> str:
        """Generate background sync functionality"""
        
        return """
// Background Sync for offline actions
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync-opportunity-applications') {
        event.waitUntil(syncApplications());
    } else if (event.tag === 'background-sync-messages') {
        event.waitUntil(syncMessages());
    } else if (event.tag === 'background-sync-profile-updates') {
        event.waitUntil(syncProfileUpdates());
    }
});

async function syncApplications() {
    try {
        const applications = await getStoredApplications();
        
        for (const application of applications) {
            try {
                const response = await fetch('/v1/applications', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': application.authToken
                    },
                    body: JSON.stringify(application.data)
                });
                
                if (response.ok) {
                    await removeStoredApplication(application.id);
                    console.log('[SW] Synced application:', application.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync application:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

async function syncMessages() {
    try {
        const messages = await getStoredMessages();
        
        for (const message of messages) {
            try {
                const response = await fetch('/v1/messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': message.authToken
                    },
                    body: JSON.stringify(message.data)
                });
                
                if (response.ok) {
                    await removeStoredMessage(message.id);
                    console.log('[SW] Synced message:', message.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync message:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Message sync failed:', error);
    }
}

async function syncProfileUpdates() {
    try {
        const updates = await getStoredProfileUpdates();
        
        for (const update of updates) {
            try {
                const response = await fetch(`/v1/profiles/${update.userId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': update.authToken
                    },
                    body: JSON.stringify(update.data)
                });
                
                if (response.ok) {
                    await removeStoredProfileUpdate(update.id);
                    console.log('[SW] Synced profile update:', update.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync profile update:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Profile sync failed:', error);
    }
}
"""
    
    def _generate_push_notification_handler(self) -> str:
        """Generate push notification handling"""
        
        return """
// Push notification handling
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    let notificationData = {};
    
    if (event.data) {
        try {
            notificationData = event.data.json();
        } catch (error) {
            notificationData = {
                title: 'Seraaj Notification',
                body: event.data.text() || 'You have a new notification',
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/badge-72x72.png'
            };
        }
    }
    
    const notificationOptions = {
        body: notificationData.body,
        icon: notificationData.icon || '/static/icons/icon-192x192.png',
        badge: notificationData.badge || '/static/icons/badge-72x72.png',
        data: notificationData.data || {},
        actions: notificationData.actions || [],
        tag: notificationData.tag || 'seraaj-notification',
        renotify: true,
        requireInteraction: notificationData.requireInteraction || false,
        silent: notificationData.silent || false,
        vibrate: notificationData.vibrate || [200, 100, 200]
    };
    
    event.waitUntil(
        self.registration.showNotification(
            notificationData.title || 'Seraaj',
            notificationOptions
        )
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.notification.tag);
    
    event.notification.close();
    
    const clickAction = event.action;
    const notificationData = event.notification.data;
    
    let urlToOpen = '/';
    
    if (clickAction) {
        // Handle action buttons
        switch (clickAction) {
            case 'view_opportunity':
                urlToOpen = `/opportunities/${notificationData.opportunityId}`;
                break;
            case 'view_application':
                urlToOpen = `/applications/${notificationData.applicationId}`;
                break;
            case 'view_message':
                urlToOpen = `/messages/${notificationData.conversationId}`;
                break;
        }
    } else if (notificationData.url) {
        urlToOpen = notificationData.url;
    }
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(clientList => {
                // Check if app is already open
                for (const client of clientList) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        client.postMessage({
                            type: 'NOTIFICATION_CLICKED',
                            url: urlToOpen,
                            data: notificationData
                        });
                        return client.focus();
                    }
                }
                
                // Open new window if app is not open
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Notification close handling
self.addEventListener('notificationclose', event => {
    console.log('[SW] Notification closed:', event.notification.tag);
    
    // Track notification dismissal
    if (event.notification.data.trackDismissal) {
        fetch('/v1/analytics/notification-dismissed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                notificationId: event.notification.data.id,
                tag: event.notification.tag,
                dismissedAt: new Date().toISOString()
            })
        }).catch(error => {
            console.error('[SW] Failed to track notification dismissal:', error);
        });
    }
});
"""
    
    def _generate_utility_functions(self) -> str:
        """Generate utility functions for service worker"""
        
        return """
// Utility functions
function createOfflineAPIResponse(request) {
    const url = new URL(request.url);
    const offlineData = {
        error: 'offline',
        message: 'This feature is not available offline',
        path: url.pathname,
        timestamp: new Date().toISOString()
    };
    
    return new Response(JSON.stringify(offlineData), {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
    });
}

async function cleanupOldCaches() {
    const cacheNames = await caches.keys();
    const oldCaches = cacheNames.filter(cacheName => 
        cacheName !== STATIC_CACHE && 
        cacheName !== DYNAMIC_CACHE && 
        cacheName !== API_CACHE
    );
    
    return Promise.all(oldCaches.map(cacheName => caches.delete(cacheName)));
}

async function getStoredApplications() {
    // This would integrate with IndexedDB for offline storage
    return [];
}

async function removeStoredApplication(id) {
    // Remove from IndexedDB
    console.log('[SW] Removing stored application:', id);
}

async function getStoredMessages() {
    return [];
}

async function removeStoredMessage(id) {
    console.log('[SW] Removing stored message:', id);
}

async function getStoredProfileUpdates() {
    return [];
}

async function removeStoredProfileUpdate(id) {
    console.log('[SW] Removing stored profile update:', id);
}

// Cache management
async function trimCache(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    
    if (keys.length > maxItems) {
        const itemsToDelete = keys.slice(0, keys.length - maxItems);
        await Promise.all(itemsToDelete.map(key => cache.delete(key)));
    }
}

// Periodic cache cleanup
setInterval(() => {
    trimCache(DYNAMIC_CACHE, CACHE_CONFIG.maxEntries);
    trimCache(API_CACHE, CACHE_CONFIG.maxEntries);
}, 5 * 60 * 1000); // Every 5 minutes
"""
    
    def _generate_custom_handlers(self, options: Dict[str, Any]) -> str:
        """Generate custom handlers based on options"""
        
        custom_code = ""
        
        if options.get("enable_analytics", True):
            custom_code += """
// Analytics tracking
self.addEventListener('fetch', event => {
    if (event.request.url.includes('/v1/analytics')) {
        // Don't cache analytics requests
        event.respondWith(fetch(event.request));
    }
});
"""
        
        if options.get("enable_error_reporting", True):
            custom_code += """
// Error reporting
self.addEventListener('error', event => {
    console.error('[SW] Service worker error:', event.error);
    
    // Report error to analytics (if online)
    if (navigator.onLine) {
        fetch('/v1/analytics/service-worker-error', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                error: event.error.toString(),
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {
            // Ignore errors in error reporting
        });
    }
});
"""
        
        return custom_code
    
    def _get_default_offline_pages(self) -> List[str]:
        """Get default pages to cache for offline access"""
        
        return [
            '/volunteer/dashboard',
            '/organization/dashboard',
            '/opportunities',
            '/applications',
            '/messages',
            '/calendar',
            '/profile'
        ]
    
    def _get_default_api_endpoints(self) -> List[str]:
        """Get default API endpoints to cache"""
        
        return [
            '/v1/opportunities',
            '/v1/applications',
            '/v1/profiles',
            '/v1/messages',
            '/v1/calendar'
        ]
    
    def generate_offline_page_html(self) -> str:
        """Generate HTML for offline fallback page"""
        
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>You're Offline - Seraaj</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .offline-container {
            max-width: 400px;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        .offline-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
        }
        h1 {
            margin: 0 0 20px;
            font-size: 28px;
            font-weight: 600;
        }
        p {
            margin: 0 0 30px;
            font-size: 16px;
            line-height: 1.5;
            opacity: 0.9;
        }
        .offline-actions {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        button {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        button:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        .status-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            font-size: 14px;
            opacity: 0.8;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ef4444;
        }
        .status-dot.online {
            background: #10b981;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📱</div>
        <h1>You're Offline</h1>
        <p>It looks like you've lost your internet connection. Don't worry - some features of Seraaj still work offline!</p>
        
        <div class="offline-actions">
            <button onclick="tryAgain()">Try Again</button>
            <button onclick="goHome()">Go to Home</button>
            <button onclick="viewCachedContent()">View Cached Content</button>
        </div>
        
        <div class="status-indicator">
            <div class="status-dot" id="connectionStatus"></div>
            <span id="connectionText">Offline</span>
        </div>
    </div>

    <script>
        function updateConnectionStatus() {
            const statusDot = document.getElementById('connectionStatus');
            const statusText = document.getElementById('connectionText');
            
            if (navigator.onLine) {
                statusDot.classList.add('online');
                statusText.textContent = 'Online';
            } else {
                statusDot.classList.remove('online');
                statusText.textContent = 'Offline';
            }
        }
        
        function tryAgain() {
            window.location.reload();
        }
        
        function goHome() {
            window.location.href = '/';
        }
        
        function viewCachedContent() {
            // Show cached opportunities or other content
            window.location.href = '/opportunities?cached=true';
        }
        
        // Listen for connection changes
        window.addEventListener('online', updateConnectionStatus);
        window.addEventListener('offline', updateConnectionStatus);
        
        // Initial status check
        updateConnectionStatus();
        
        // Auto-retry when connection is restored
        window.addEventListener('online', () => {
            setTimeout(() => {
                if (confirm('Connection restored! Would you like to reload the page?')) {
                    window.location.reload();
                }
            }, 1000);
        });
    </script>
</body>
</html>
"""


def generate_service_worker(
    caching_strategy: str = "network_first",
    offline_pages: Optional[List[str]] = None,
    api_endpoints: Optional[List[str]] = None,
    custom_options: Optional[Dict[str, Any]] = None
) -> str:
    """Generate service worker JavaScript"""
    
    generator = ServiceWorkerGenerator()
    return generator.generate_service_worker(
        caching_strategy=caching_strategy,
        offline_pages=offline_pages,
        api_endpoints_to_cache=api_endpoints,
        custom_options=custom_options
    )


def save_service_worker_files():
    """Generate and save service worker files"""
    
    from pathlib import Path
    
    generator = ServiceWorkerGenerator()
    static_dir = Path("static")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main service worker
    sw_code = generator.generate_service_worker()
    with open(static_dir / "sw.js", "w", encoding="utf-8") as f:
        f.write(sw_code)
    
    # Generate offline page
    offline_html = generator.generate_offline_page_html()
    with open(static_dir / "offline.html", "w", encoding="utf-8") as f:
        f.write(offline_html)
    
    print("Service worker files generated successfully!")