"""
Offline Storage Management for PWA
Handles client-side data synchronization and offline data management
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid


class OfflineDataType(str, Enum):
    """Types of data that can be stored offline"""

    OPPORTUNITIES = "opportunities"
    APPLICATIONS = "applications"
    MESSAGES = "messages"
    PROFILE = "profile"
    CALENDAR_EVENTS = "calendar_events"
    CONVERSATIONS = "conversations"
    NOTIFICATIONS = "notifications"
    DRAFTS = "drafts"
    MEDIA = "media"


class SyncPriority(str, Enum):
    """Priority levels for data synchronization"""

    HIGH = "high"  # Critical user actions
    MEDIUM = "medium"  # Important updates
    LOW = "low"  # Background data
    DEFER = "defer"  # Can wait for good connection


class OfflineAction:
    """Represents an action to be synced when online"""

    def __init__(
        self,
        action_type: str,
        endpoint: str,
        method: str,
        data: Dict[str, Any],
        priority: SyncPriority = SyncPriority.MEDIUM,
        retry_count: int = 0,
        max_retries: int = 3,
    ):
        self.id = str(uuid.uuid4())
        self.action_type = action_type
        self.endpoint = endpoint
        self.method = method
        self.data = data
        self.priority = priority
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.created_at = datetime.now(datetime.timezone.utc)
        self.last_attempt = None
        self.error_message = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "endpoint": self.endpoint,
            "method": self.method,
            "data": self.data,
            "priority": self.priority.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "last_attempt": (
                self.last_attempt.isoformat() if self.last_attempt else None
            ),
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OfflineAction":
        action = cls(
            action_type=data["action_type"],
            endpoint=data["endpoint"],
            method=data["method"],
            data=data["data"],
            priority=SyncPriority(data["priority"]),
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
        )
        action.id = data["id"]
        action.created_at = datetime.fromisoformat(data["created_at"])
        if data["last_attempt"]:
            action.last_attempt = datetime.fromisoformat(data["last_attempt"])
        action.error_message = data.get("error_message")
        return action


class OfflineStorageManager:
    """Manages offline data storage and synchronization"""

    def __init__(self):
        self.storage_limits = {
            OfflineDataType.OPPORTUNITIES: 100,  # Max opportunities to cache
            OfflineDataType.APPLICATIONS: 50,  # Max applications to cache
            OfflineDataType.MESSAGES: 200,  # Max messages to cache
            OfflineDataType.CALENDAR_EVENTS: 100,
            OfflineDataType.CONVERSATIONS: 20,
            OfflineDataType.NOTIFICATIONS: 50,
            OfflineDataType.DRAFTS: 10,
            OfflineDataType.MEDIA: 20,  # Max media files
        }

        self.cache_duration = {
            OfflineDataType.OPPORTUNITIES: timedelta(hours=6),
            OfflineDataType.APPLICATIONS: timedelta(hours=12),
            OfflineDataType.MESSAGES: timedelta(days=7),
            OfflineDataType.PROFILE: timedelta(days=1),
            OfflineDataType.CALENDAR_EVENTS: timedelta(hours=12),
            OfflineDataType.CONVERSATIONS: timedelta(days=7),
            OfflineDataType.NOTIFICATIONS: timedelta(days=3),
            OfflineDataType.DRAFTS: timedelta(days=30),
            OfflineDataType.MEDIA: timedelta(days=7),
        }

    def generate_storage_schema(self) -> Dict[str, Any]:
        """Generate IndexedDB schema for offline storage"""

        return {
            "name": "SeraajOfflineDB",
            "version": 1,
            "stores": {
                "opportunities": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "organization_id", "keyPath": "organization_id"},
                        {"name": "created_at", "keyPath": "created_at"},
                        {"name": "location", "keyPath": "location"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "applications": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "volunteer_id", "keyPath": "volunteer_id"},
                        {"name": "opportunity_id", "keyPath": "opportunity_id"},
                        {"name": "status", "keyPath": "status"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "messages": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "conversation_id", "keyPath": "conversation_id"},
                        {"name": "sender_id", "keyPath": "sender_id"},
                        {"name": "created_at", "keyPath": "created_at"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "conversations": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "updated_at", "keyPath": "updated_at"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "profiles": {
                    "keyPath": "user_id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "role", "keyPath": "role"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "calendar_events": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "user_id", "keyPath": "user_id"},
                        {"name": "start_datetime", "keyPath": "start_datetime"},
                        {"name": "event_type", "keyPath": "event_type"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "notifications": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "user_id", "keyPath": "user_id"},
                        {"name": "is_read", "keyPath": "is_read"},
                        {"name": "created_at", "keyPath": "created_at"},
                        {"name": "cached_at", "keyPath": "_cached_at"},
                    ],
                },
                "drafts": {
                    "keyPath": "id",
                    "autoIncrement": True,
                    "indices": [
                        {"name": "type", "keyPath": "type"},
                        {"name": "created_at", "keyPath": "created_at"},
                        {"name": "updated_at", "keyPath": "updated_at"},
                    ],
                },
                "sync_queue": {
                    "keyPath": "id",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "priority", "keyPath": "priority"},
                        {"name": "created_at", "keyPath": "created_at"},
                        {"name": "retry_count", "keyPath": "retry_count"},
                    ],
                },
                "media_cache": {
                    "keyPath": "url",
                    "autoIncrement": False,
                    "indices": [
                        {"name": "type", "keyPath": "type"},
                        {"name": "size", "keyPath": "size"},
                        {"name": "cached_at", "keyPath": "cached_at"},
                    ],
                },
                "app_settings": {
                    "keyPath": "key",
                    "autoIncrement": False,
                    "indices": [{"name": "updated_at", "keyPath": "updated_at"}],
                },
            },
        }

    def generate_client_storage_js(self) -> str:
        """Generate JavaScript code for client-side storage management"""

        schema = self.generate_storage_schema()

        return f"""
// Seraaj Offline Storage Manager
// Generated: {datetime.now(datetime.timezone.utc).isoformat()}

class SeraajOfflineStorage {{
    constructor() {{
        this.dbName = '{schema["name"]}';
        this.dbVersion = {schema["version"]};
        this.db = null;
        this.isOnline = navigator.onLine;
        
        // Storage limits
        this.limits = {json.dumps(self.storage_limits, default=str, indent=12)};
        
        // Cache duration (in milliseconds)
        this.cacheDuration = {{
            opportunities: {int(self.cache_duration[OfflineDataType.OPPORTUNITIES].total_seconds() * 1000)},
            applications: {int(self.cache_duration[OfflineDataType.APPLICATIONS].total_seconds() * 1000)},
            messages: {int(self.cache_duration[OfflineDataType.MESSAGES].total_seconds() * 1000)},
            profile: {int(self.cache_duration[OfflineDataType.PROFILE].total_seconds() * 1000)},
            calendar_events: {int(self.cache_duration[OfflineDataType.CALENDAR_EVENTS].total_seconds() * 1000)},
            conversations: {int(self.cache_duration[OfflineDataType.CONVERSATIONS].total_seconds() * 1000)},
            notifications: {int(self.cache_duration[OfflineDataType.NOTIFICATIONS].total_seconds() * 1000)},
            drafts: {int(self.cache_duration[OfflineDataType.DRAFTS].total_seconds() * 1000)},
            media: {int(self.cache_duration[OfflineDataType.MEDIA].total_seconds() * 1000)}
        }};
        
        this.initDB();
        this.setupEventListeners();
    }}
    
    async initDB() {{
        return new Promise((resolve, reject) => {{
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {{
                this.db = request.result;
                resolve(this.db);
            }};
            
            request.onupgradeneeded = (event) => {{
                const db = event.target.result;
                
                // Create object stores
                {self._generate_store_creation_js(schema["stores"])}
            }};
        }});
    }}
    
    setupEventListeners() {{
        // Listen for online/offline events
        window.addEventListener('online', () => {{
            this.isOnline = true;
            this.syncPendingActions();
        }});
        
        window.addEventListener('offline', () => {{
            this.isOnline = false;
        }});
        
        // Periodic cleanup
        setInterval(() => {{
            this.cleanupExpiredData();
        }}, 30 * 60 * 1000); // Every 30 minutes
    }}
    
    // Data storage methods
    async storeOpportunities(opportunities) {{
        const store = this.getStore('opportunities', 'readwrite');
        const now = new Date().toISOString();
        
        for (const opportunity of opportunities) {{
            opportunity._cached_at = now;
            await this.putData(store, opportunity);
        }}
        
        await this.enforceStorageLimit('opportunities');
    }}
    
    async getOpportunities(filters = {{}}) {{
        const store = this.getStore('opportunities', 'readonly');
        let opportunities = await this.getAllFromStore(store);
        
        // Filter expired data
        opportunities = this.filterExpiredData(opportunities, 'opportunities');
        
        // Apply filters
        if (filters.location) {{
            opportunities = opportunities.filter(opp => 
                opp.location && opp.location.toLowerCase().includes(filters.location.toLowerCase())
            );
        }}
        
        if (filters.skills) {{
            opportunities = opportunities.filter(opp => 
                opp.skills_required && 
                filters.skills.some(skill => opp.skills_required.includes(skill))
            );
        }}
        
        return opportunities;
    }}
    
    async storeApplications(applications) {{
        const store = this.getStore('applications', 'readwrite');
        const now = new Date().toISOString();
        
        for (const application of applications) {{
            application._cached_at = now;
            await this.putData(store, application);
        }}
        
        await this.enforceStorageLimit('applications');
    }}
    
    async getApplications(userId) {{
        const store = this.getStore('applications', 'readonly');
        const index = store.index('volunteer_id');
        let applications = await this.getAllFromIndex(index, userId);
        
        return this.filterExpiredData(applications, 'applications');
    }}
    
    async storeMessages(messages) {{
        const store = this.getStore('messages', 'readwrite');
        const now = new Date().toISOString();
        
        for (const message of messages) {{
            message._cached_at = now;
            await this.putData(store, message);
        }}
        
        await this.enforceStorageLimit('messages');
    }}
    
    async getMessages(conversationId) {{
        const store = this.getStore('messages', 'readonly');
        const index = store.index('conversation_id');
        let messages = await this.getAllFromIndex(index, conversationId);
        
        return this.filterExpiredData(messages, 'messages');
    }}
    
    // Draft management
    async saveDraft(type, data) {{
        const draft = {{
            id: this.generateId(),
            type: type,
            data: data,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        }};
        
        const store = this.getStore('drafts', 'readwrite');
        await this.putData(store, draft);
        
        return draft.id;
    }}
    
    async getDrafts(type) {{
        const store = this.getStore('drafts', 'readonly');
        const index = store.index('type');
        return await this.getAllFromIndex(index, type);
    }}
    
    async deleteDraft(id) {{
        const store = this.getStore('drafts', 'readwrite');
        await this.deleteData(store, id);
    }}
    
    // Sync queue management
    async addToSyncQueue(action) {{
        const store = this.getStore('sync_queue', 'readwrite');
        await this.putData(store, action);
    }}
    
    async getSyncQueue() {{
        const store = this.getStore('sync_queue', 'readonly');
        const actions = await this.getAllFromStore(store);
        
        // Sort by priority and creation time
        return actions.sort((a, b) => {{
            const priorityOrder = {{ high: 3, medium: 2, low: 1, defer: 0 }};
            const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
            
            if (priorityDiff !== 0) return priorityDiff;
            return new Date(a.created_at) - new Date(b.created_at);
        }});
    }}
    
    async removeFromSyncQueue(actionId) {{
        const store = this.getStore('sync_queue', 'readwrite');
        await this.deleteData(store, actionId);
    }}
    
    async syncPendingActions() {{
        if (!this.isOnline) return;
        
        const actions = await this.getSyncQueue();
        console.log(`[Storage] Syncing ${{actions.length}} pending actions`);
        
        for (const action of actions) {{
            try {{
                await this.executeSyncAction(action);
                await this.removeFromSyncQueue(action.id);
                console.log(`[Storage] Synced action: ${{action.action_type}}`);
            }} catch (error) {{
                console.error(`[Storage] Failed to sync action:`, error);
                
                // Update retry count
                action.retry_count += 1;
                action.last_attempt = new Date().toISOString();
                action.error_message = error.message;
                
                if (action.retry_count >= action.max_retries) {{
                    console.log(`[Storage] Max retries reached for action ${{action.id}}, removing`);
                    await this.removeFromSyncQueue(action.id);
                }} else {{
                    // Update action in queue
                    const store = this.getStore('sync_queue', 'readwrite');
                    await this.putData(store, action);
                }}
            }}
        }}
    }}
    
    async executeSyncAction(action) {{
        const response = await fetch(action.endpoint, {{
            method: action.method,
            headers: {{
                'Content-Type': 'application/json',
                'Authorization': localStorage.getItem('auth_token')
            }},
            body: action.method !== 'GET' ? JSON.stringify(action.data) : null
        }});
        
        if (!response.ok) {{
            throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
        }}
        
        return response.json();
    }}
    
    // Utility methods
    getStore(storeName, mode = 'readonly') {{
        const transaction = this.db.transaction([storeName], mode);
        return transaction.objectStore(storeName);
    }}
    
    async putData(store, data) {{
        return new Promise((resolve, reject) => {{
            const request = store.put(data);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        }});
    }}
    
    async deleteData(store, key) {{
        return new Promise((resolve, reject) => {{
            const request = store.delete(key);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        }});
    }}
    
    async getAllFromStore(store) {{
        return new Promise((resolve, reject) => {{
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        }});
    }}
    
    async getAllFromIndex(index, key) {{
        return new Promise((resolve, reject) => {{
            const request = index.getAll(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        }});
    }}
    
    filterExpiredData(data, dataType) {{
        const now = Date.now();
        const duration = this.cacheDuration[dataType];
        
        return data.filter(item => {{
            if (!item._cached_at) return true;
            
            const cachedAt = new Date(item._cached_at).getTime();
            return (now - cachedAt) < duration;
        }});
    }}
    
    async enforceStorageLimit(storeName) {{
        const limit = this.limits[storeName];
        if (!limit) return;
        
        const store = this.getStore(storeName, 'readwrite');
        const data = await this.getAllFromStore(store);
        
        if (data.length > limit) {{
            // Sort by cached date (oldest first)
            data.sort((a, b) => new Date(a._cached_at) - new Date(b._cached_at));
            
            // Remove oldest entries
            const toRemove = data.slice(0, data.length - limit);
            for (const item of toRemove) {{
                await this.deleteData(store, item.id);
            }}
            
            console.log(`[Storage] Removed ${{toRemove.length}} old entries from ${{storeName}}`);
        }}
    }}
    
    async cleanupExpiredData() {{
        console.log('[Storage] Running cleanup of expired data');
        
        for (const [storeName, duration] of Object.entries(this.cacheDuration)) {{
            if (storeName === 'drafts') continue; // Don't auto-cleanup drafts
            
            try {{
                const store = this.getStore(storeName, 'readwrite');
                const data = await this.getAllFromStore(store);
                const now = Date.now();
                
                let removed = 0;
                for (const item of data) {{
                    if (item._cached_at) {{
                        const cachedAt = new Date(item._cached_at).getTime();
                        if ((now - cachedAt) > duration) {{
                            await this.deleteData(store, item.id);
                            removed++;
                        }}
                    }}
                }}
                
                if (removed > 0) {{
                    console.log(`[Storage] Cleaned up ${{removed}} expired items from ${{storeName}}`);
                }}
            }} catch (error) {{
                console.error(`[Storage] Error cleaning up ${{storeName}}:`, error);
            }}
        }}
    }}
    
    generateId() {{
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }}
    
    // Storage info
    async getStorageInfo() {{
        const info = {{ stores: {{}} }};
        
        for (const storeName of Object.keys(this.limits)) {{
            try {{
                const store = this.getStore(storeName, 'readonly');
                const data = await this.getAllFromStore(store);
                
                info.stores[storeName] = {{
                    count: data.length,
                    limit: this.limits[storeName],
                    size: JSON.stringify(data).length
                }};
            }} catch (error) {{
                info.stores[storeName] = {{ error: error.message }};
            }}
        }}
        
        return info;
    }}
}}

// Global instance
const seraajStorage = new SeraajOfflineStorage();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = SeraajOfflineStorage;
}}
"""

    def _generate_store_creation_js(self, stores: Dict[str, Any]) -> str:
        """Generate JavaScript code for creating IndexedDB stores"""

        js_code = ""
        for store_name, config in stores.items():
            js_code += f"""
                // Create {store_name} store
                if (!db.objectStoreNames.contains('{store_name}')) {{
                    const {store_name}Store = db.createObjectStore('{store_name}', {{
                        keyPath: '{config["keyPath"]}', 
                        autoIncrement: {str(config["autoIncrement"]).lower()}
                    }});
                    
                    // Create indices
"""

            for index in config.get("indices", []):
                js_code += f"""                    {store_name}Store.createIndex('{index["name"]}', '{index["keyPath"]}');
"""

            js_code += "                }\n"

        return js_code

    def generate_offline_api_handlers(self) -> str:
        """Generate JavaScript for handling API requests when offline"""

        return """
// Offline API Request Handlers
class OfflineAPIHandler {
    constructor(storage) {
        this.storage = storage;
    }
    
    async handleRequest(request) {
        const url = new URL(request.url);
        const path = url.pathname;
        const method = request.method;
        
        // Route to appropriate handler
        if (path.startsWith('/v1/opportunities')) {
            return this.handleOpportunityRequest(request, path, method);
        } else if (path.startsWith('/v1/applications')) {
            return this.handleApplicationRequest(request, path, method);
        } else if (path.startsWith('/v1/messages')) {
            return this.handleMessageRequest(request, path, method);
        } else if (path.startsWith('/v1/profiles')) {
            return this.handleProfileRequest(request, path, method);
        }
        
        // Default offline response
        return this.createOfflineResponse({
            error: 'offline',
            message: 'This feature is not available offline',
            path: path
        }, 503);
    }
    
    async handleOpportunityRequest(request, path, method) {
        if (method === 'GET') {
            const opportunities = await this.storage.getOpportunities();
            return this.createSuccessResponse({
                data: opportunities,
                cached: true,
                offline: true
            });
        }
        
        return this.createOfflineResponse({
            error: 'offline_write_operation',
            message: 'Cannot create opportunities while offline'
        }, 503);
    }
    
    async handleApplicationRequest(request, path, method) {
        if (method === 'GET') {
            const userId = this.getCurrentUserId();
            const applications = await this.storage.getApplications(userId);
            return this.createSuccessResponse({
                data: applications,
                cached: true,
                offline: true
            });
        } else if (method === 'POST') {
            // Handle offline application creation
            const data = await request.json();
            
            // Save as draft
            const draftId = await this.storage.saveDraft('application', data);
            
            // Add to sync queue
            await this.storage.addToSyncQueue({
                id: this.generateId(),
                action_type: 'create_application',
                endpoint: '/v1/applications',
                method: 'POST',
                data: data,
                priority: 'high',
                retry_count: 0,
                max_retries: 3,
                created_at: new Date().toISOString()
            });
            
            return this.createSuccessResponse({
                message: 'Application saved offline and will be submitted when online',
                draft_id: draftId,
                offline: true
            });
        }
        
        return this.createOfflineResponse({
            error: 'offline_operation',
            message: 'This operation is not available offline'
        }, 503);
    }
    
    async handleMessageRequest(request, path, method) {
        if (method === 'GET') {
            const conversationId = this.extractIdFromPath(path);
            const messages = await this.storage.getMessages(conversationId);
            return this.createSuccessResponse({
                data: messages,
                cached: true,
                offline: true
            });
        } else if (method === 'POST') {
            // Handle offline message sending
            const data = await request.json();
            
            // Save as draft
            const draftId = await this.storage.saveDraft('message', data);
            
            // Add to sync queue
            await this.storage.addToSyncQueue({
                id: this.generateId(),
                action_type: 'send_message',
                endpoint: '/v1/messages',
                method: 'POST',
                data: data,
                priority: 'medium',
                retry_count: 0,
                max_retries: 5,
                created_at: new Date().toISOString()
            });
            
            return this.createSuccessResponse({
                message: 'Message saved offline and will be sent when online',
                draft_id: draftId,
                offline: true
            });
        }
        
        return this.createOfflineResponse({
            error: 'offline_operation',
            message: 'This operation is not available offline'
        }, 503);
    }
    
    async handleProfileRequest(request, path, method) {
        if (method === 'GET') {
            // Return cached profile data
            const userId = this.getCurrentUserId();
            const profile = await this.storage.getProfile(userId);
            return this.createSuccessResponse({
                data: profile,
                cached: true,
                offline: true
            });
        } else if (method === 'PUT') {
            // Handle offline profile updates
            const data = await request.json();
            const userId = this.extractIdFromPath(path);
            
            // Save as draft
            const draftId = await this.storage.saveDraft('profile_update', {
                userId: userId,
                data: data
            });
            
            // Add to sync queue
            await this.storage.addToSyncQueue({
                id: this.generateId(),
                action_type: 'update_profile',
                endpoint: path,
                method: 'PUT',
                data: data,
                priority: 'medium',
                retry_count: 0,
                max_retries: 3,
                created_at: new Date().toISOString()
            });
            
            return this.createSuccessResponse({
                message: 'Profile changes saved offline and will be synced when online',
                draft_id: draftId,
                offline: true
            });
        }
        
        return this.createOfflineResponse({
            error: 'offline_operation',
            message: 'This operation is not available offline'
        }, 503);
    }
    
    createSuccessResponse(data) {
        return new Response(JSON.stringify({
            success: true,
            ...data,
            timestamp: new Date().toISOString()
        }), {
            status: 200,
            headers: {
                'Content-Type': 'application/json',
                'X-Offline-Response': 'true'
            }
        });
    }
    
    createOfflineResponse(data, status = 503) {
        return new Response(JSON.stringify({
            success: false,
            ...data,
            timestamp: new Date().toISOString()
        }), {
            status: status,
            headers: {
                'Content-Type': 'application/json',
                'X-Offline-Response': 'true'
            }
        });
    }
    
    getCurrentUserId() {
        // Extract from JWT token or localStorage
        try {
            const token = localStorage.getItem('auth_token');
            if (token) {
                const payload = JSON.parse(atob(token.split('.')[1]));
                return payload.sub || payload.user_id;
            }
        } catch (error) {
            console.error('Failed to get user ID:', error);
        }
        return null;
    }
    
    extractIdFromPath(path) {
        const matches = path.match(/\\/([0-9]+)$/);
        return matches ? parseInt(matches[1]) : null;
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
}

// Create global instance
const offlineAPIHandler = new OfflineAPIHandler(seraajStorage);
"""

    def generate_sync_manager_js(self) -> str:
        """Generate JavaScript for managing data synchronization"""

        return """
// Data Synchronization Manager
class SyncManager {
    constructor(storage) {
        this.storage = storage;
        this.syncInProgress = false;
        this.lastSyncTime = null;
        this.syncInterval = 5 * 60 * 1000; // 5 minutes
        
        this.setupPeriodicSync();
    }
    
    setupPeriodicSync() {
        // Sync when online
        window.addEventListener('online', () => {
            this.performFullSync();
        });
        
        // Periodic sync when online
        setInterval(() => {
            if (navigator.onLine && !this.syncInProgress) {
                this.performIncrementalSync();
            }
        }, this.syncInterval);
    }
    
    async performFullSync() {
        if (this.syncInProgress) return;
        
        console.log('[Sync] Starting full synchronization');
        this.syncInProgress = true;
        
        try {
            // Sync pending actions first
            await this.storage.syncPendingActions();
            
            // Sync fresh data
            await this.syncOpportunities();
            await this.syncApplications();
            await this.syncMessages();
            await this.syncProfile();
            await this.syncCalendarEvents();
            
            this.lastSyncTime = new Date();
            console.log('[Sync] Full synchronization completed');
            
            // Emit sync complete event
            window.dispatchEvent(new CustomEvent('seraaj:sync:complete', {
                detail: { type: 'full', timestamp: this.lastSyncTime }
            }));
            
        } catch (error) {
            console.error('[Sync] Full synchronization failed:', error);
            
            window.dispatchEvent(new CustomEvent('seraaj:sync:error', {
                detail: { type: 'full', error: error.message }
            }));
        } finally {
            this.syncInProgress = false;
        }
    }
    
    async performIncrementalSync() {
        if (this.syncInProgress) return;
        
        console.log('[Sync] Starting incremental synchronization');
        this.syncInProgress = true;
        
        try {
            // Only sync pending actions for incremental sync
            await this.storage.syncPendingActions();
            
            // Update timestamps
            const currentTime = new Date();
            if (this.lastSyncTime) {
                await this.syncUpdatedData(this.lastSyncTime);
            }
            
            this.lastSyncTime = currentTime;
            console.log('[Sync] Incremental synchronization completed');
            
            window.dispatchEvent(new CustomEvent('seraaj:sync:complete', {
                detail: { type: 'incremental', timestamp: this.lastSyncTime }
            }));
            
        } catch (error) {
            console.error('[Sync] Incremental synchronization failed:', error);
        } finally {
            this.syncInProgress = false;
        }
    }
    
    async syncOpportunities() {
        try {
            const response = await fetch('/v1/opportunities?limit=50', {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                await this.storage.storeOpportunities(data.data || data);
                console.log('[Sync] Opportunities synced');
            }
        } catch (error) {
            console.error '[Sync] Failed to sync opportunities:', error);
        }
    }
    
    async syncApplications() {
        try {
            const response = await fetch('/v1/applications', {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                await this.storage.storeApplications(data.data || data);
                console.log('[Sync] Applications synced');
            }
        } catch (error) {
            console.error('[Sync] Failed to sync applications:', error);
        }
    }
    
    async syncMessages() {
        try {
            const response = await fetch('/v1/messages/recent?limit=100', {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                await this.storage.storeMessages(data.data || data);
                console.log('[Sync] Messages synced');
            }
        } catch (error) {
            console.error('[Sync] Failed to sync messages:', error);
        }
    }
    
    async syncProfile() {
        try {
            const response = await fetch('/v1/profiles/me', {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                await this.storage.storeProfile(profile.data || profile);
                console.log('[Sync] Profile synced');
            }
        } catch (error) {
            console.error('[Sync] Failed to sync profile:', error);
        }
    }
    
    async syncCalendarEvents() {
        try {
            const response = await fetch('/v1/calendar/events', {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                await this.storage.storeCalendarEvents(data.data || data);
                console.log('[Sync] Calendar events synced');
            }
        } catch (error) {
            console.error('[Sync] Failed to sync calendar events:', error);
        }
    }
    
    async syncUpdatedData(since) {
        const timestamp = since.toISOString();
        
        // Sync only data updated since last sync
        try {
            const response = await fetch(`/v1/sync/updates?since=${timestamp}`, {
                headers: {
                    'Authorization': localStorage.getItem('auth_token')
                }
            });
            
            if (response.ok) {
                const updates = await response.json();
                
                if (updates.opportunities) {
                    await this.storage.storeOpportunities(updates.opportunities);
                }
                if (updates.applications) {
                    await this.storage.storeApplications(updates.applications);
                }
                if (updates.messages) {
                    await this.storage.storeMessages(updates.messages);
                }
                
                console.log('[Sync] Updated data synced');
            }
        } catch (error) {
            console.error('[Sync] Failed to sync updated data:', error);
        }
    }
    
    // Manual sync trigger
    async forcSync() {
        await this.performFullSync();
    }
    
    getSyncStatus() {
        return {
            inProgress: this.syncInProgress,
            lastSync: this.lastSyncTime,
            isOnline: navigator.onLine
        };
    }
}

// Create global sync manager
const syncManager = new SyncManager(seraajStorage);
"""


def generate_offline_storage_files():
    """Generate all offline storage related files"""

    from pathlib import Path

    manager = OfflineStorageManager()
    static_dir = Path("static/js")
    static_dir.mkdir(parents=True, exist_ok=True)

    # Generate main storage script
    storage_js = manager.generate_client_storage_js()
    with open(static_dir / "offline-storage.js", "w", encoding="utf-8") as f:
        f.write(storage_js)

    # Generate API handlers
    api_handlers_js = manager.generate_offline_api_handlers()
    with open(static_dir / "offline-api.js", "w", encoding="utf-8") as f:
        f.write(api_handlers_js)

    # Generate sync manager
    sync_manager_js = manager.generate_sync_manager_js()
    with open(static_dir / "sync-manager.js", "w", encoding="utf-8") as f:
        f.write(sync_manager_js)

    print("Offline storage files generated successfully!")
