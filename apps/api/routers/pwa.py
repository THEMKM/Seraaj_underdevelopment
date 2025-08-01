"""
Progressive Web App (PWA) Router
Handles PWA manifests, service workers, and offline functionality
"""

from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from sqlmodel import Session
from typing import Annotated, Dict, Any, Optional, List

from database import get_session
from models import User
from routers.auth import get_current_user, get_current_user_optional
from pwa.manifest_generator import generate_pwa_manifest
from pwa.service_worker import ServiceWorkerGenerator, generate_service_worker
from pwa.offline_storage import OfflineStorageManager, generate_offline_storage_files
from utils.response_formatter import success_with_data
from config.settings import settings
import logging

router = APIRouter(prefix="/v1/pwa", tags=["pwa"])
logger = logging.getLogger(__name__)


@router.get("/manifest.json")
async def get_manifest(
    request: Request,
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
    role: Optional[str] = Query(None, description="User role for customized manifest"),
    theme: Optional[str] = Query(None, description="Theme color preference"),
):
    """Get PWA manifest file"""

    try:
        # Determine user preferences
        user_preferences = {}
        # if user:
        #     user_preferences = {
        #         "user_role": user.role,
        #         "language": getattr(user, 'language_preference', 'en'),
        #         "theme_color": theme or getattr(user, 'theme_preference', None)
        #     }
        if role:
            user_preferences["user_role"] = role

        if theme:
            user_preferences["theme_color"] = theme

        # Generate manifest
        manifest = generate_pwa_manifest(
            user_role=user_preferences.get("user_role"),
            user_preferences=user_preferences,
        )

        # Add request-specific URLs
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        manifest["start_url"] = f"{base_url}{manifest.get('start_url', '/')}"
        manifest["scope"] = f"{base_url}/"

        # Update icon URLs to be absolute
        if "icons" in manifest:
            for icon in manifest["icons"]:
                if icon["src"].startswith("/"):
                    icon["src"] = f"{base_url}{icon['src']}"

        return JSONResponse(
            content=manifest,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                "Content-Type": "application/manifest+json",
            },
        )

    except Exception as e:
        logger.error(f"Error generating manifest: {e}")
        # Return basic manifest as fallback
        basic_manifest = {
            "name": "Seraaj",
            "short_name": "Seraaj",
            "start_url": "/",
            "display": "standalone",
            "theme_color": "#2563eb",
            "background_color": "#ffffff",
            "icons": [
                {
                    "src": "/static/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                }
            ],
        }
        return JSONResponse(content=basic_manifest)


@router.get("/sw.js")
async def get_service_worker(
    request: Request,
    strategy: str = Query("network_first", description="Caching strategy"),
    version: Optional[str] = Query(None, description="Service worker version"),
):
    """Get service worker JavaScript file"""

    try:
        # Generate service worker with custom options
        custom_options = {
            "enable_analytics": True,
            "enable_error_reporting": True,
            "enable_background_sync": True,
            "enable_push_notifications": True,
        }

        # Get API endpoints to cache based on user context
        api_endpoints = [
            "/v1/opportunities",
            "/v1/applications",
            "/v1/messages",
            "/v1/profiles",
            "/v1/calendar",
        ]

        # Get pages to cache offline
        offline_pages = [
            "/",
            "/opportunities",
            "/applications",
            "/messages",
            "/calendar",
            "/profile",
        ]

        sw_code = generate_service_worker(
            caching_strategy=strategy,
            offline_pages=offline_pages,
            api_endpoints=api_endpoints,
            custom_options=custom_options,
        )

        return PlainTextResponse(
            content=sw_code,
            headers={
                "Content-Type": "application/javascript",
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Service-Worker-Allowed": "/",
            },
        )

    except Exception as e:
        logger.error(f"Error generating service worker: {e}")
        # Return minimal service worker as fallback
        fallback_sw = """
        console.log('[SW] Fallback service worker loaded');
        
        self.addEventListener('install', event => {
            console.log('[SW] Installing fallback service worker');
            self.skipWaiting();
        });
        
        self.addEventListener('activate', event => {
            console.log('[SW] Activating fallback service worker');
            self.clients.claim();
        });
        
        self.addEventListener('fetch', event => {
            // Pass through all requests
            event.respondWith(fetch(event.request));
        });
        """
        return PlainTextResponse(content=fallback_sw)


@router.get("/offline.html")
async def get_offline_page():
    """Get offline fallback HTML page"""

    generator = ServiceWorkerGenerator()
    offline_html = generator.generate_offline_page_html()

    return HTMLResponse(
        content=offline_html,
        headers={"Cache-Control": "public, max-age=86400"},  # Cache for 24 hours
    )


@router.get("/install-prompt")
async def get_install_prompt_data(
    request: Request, user: Annotated[Optional[User], Depends(get_current_user)] = None
):
    """Get data for PWA install prompt"""

    try:
        # Check if app is already installed (basic heuristic)
        user_agent = request.headers.get("user-agent", "").lower()
        is_mobile = any(
            device in user_agent for device in ["mobile", "android", "iphone", "ipad"]
        )
        is_standalone = request.headers.get("x-requested-with") == "seraaj-pwa"

        # Determine install eligibility
        can_install = is_mobile and not is_standalone

        # Get user-specific benefits
        benefits = [
            "Work offline and sync when connected",
            "Receive push notifications for new opportunities",
            "Quick access from your home screen",
            "Faster loading with cached content",
        ]

        if user and user.role == "volunteer":
            benefits.extend(
                [
                    "Save draft applications offline",
                    "Get instant notifications for application updates",
                    "Access your calendar without internet",
                ]
            )
        elif user and user.role == "organization":
            benefits.extend(
                [
                    "Manage applications on the go",
                    "Post opportunities from anywhere",
                    "Review volunteer profiles offline",
                ]
            )

        install_data = {
            "can_install": can_install,
            "is_mobile": is_mobile,
            "is_standalone": is_standalone,
            "benefits": benefits,
            "install_instructions": {
                "android_chrome": [
                    "Tap the menu button (⋮) in Chrome",
                    "Select 'Add to Home screen'",
                    "Confirm by tapping 'Add'",
                ],
                "ios_safari": [
                    "Tap the Share button (□↑) in Safari",
                    "Scroll down and tap 'Add to Home Screen'",
                    "Tap 'Add' to confirm",
                ],
                "desktop": [
                    "Look for the install icon in your browser's address bar",
                    "Click it and select 'Install'",
                    "The app will be added to your applications",
                ],
            },
        }

        return success_with_data(install_data, "Install prompt data retrieved")

    except Exception as e:
        logger.error(f"Error getting install prompt data: {e}")
        return success_with_data(
            {"can_install": False, "error": "Unable to determine install eligibility"}
        )


@router.post("/install-analytics")
async def track_install_analytics(
    request: Request,
    event_data: Dict[str, Any],
    user: Annotated[Optional[User], Depends(get_current_user_optional)] = None,
    session: Annotated[Session, Depends(get_session)] = None,
):
    """Track PWA installation analytics"""

    try:
        # Log install event
        # logger.info(f"PWA install event: {event_data.get('event')} from user {user.id if user else 'anonymous'}")

        # In production, you would store this in analytics database
        analytics_data = {
            "event_type": "pwa_install",
            "event": event_data.get("event"),  # 'prompted', 'accepted', 'dismissed'
            "user_id": None,  # user.id if user else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": event_data.get("timestamp"),
            "metadata": event_data.get("metadata", {}),
        }

        # Store in analytics (placeholder)
        # analytics_service.track_event(analytics_data)

        return success_with_data({"tracked": True}, "Install analytics tracked")

    except Exception as e:
        logger.error(f"Error tracking install analytics: {e}")
        return success_with_data({"tracked": False, "error": str(e)})


@router.get("/offline-data")
async def get_offline_data_info(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get information about offline data storage"""

    try:
        # Generate storage info
        manager = OfflineStorageManager()

        storage_info = {
            "storage_limits": manager.storage_limits,
            "cache_duration": {
                key: int(duration.total_seconds())
                for key, duration in manager.cache_duration.items()
            },
            "supported_offline_actions": [
                "view_opportunities",
                "view_applications",
                "view_messages",
                "save_application_drafts",
                "save_message_drafts",
                "update_profile_drafts",
            ],
            "sync_triggers": [
                "app_startup",
                "network_reconnection",
                "manual_refresh",
                "periodic_background_sync",
            ],
        }

        return success_with_data(storage_info, "Offline data info retrieved")

    except Exception as e:
        logger.error(f"Error getting offline data info: {e}")
        return success_with_data({"error": str(e)})


@router.post("/sync-status")
async def update_sync_status(
    sync_data: Dict[str, Any],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update client-side sync status"""

    try:
        # Log sync activity
        logger.info(
            f"Sync status update from user {user.id}: {sync_data.get('status')}"
        )

        # In production, you might want to track sync statistics
        sync_info = {
            "user_id": user.id,
            "sync_type": sync_data.get("sync_type"),  # 'full', 'incremental'
            "status": sync_data.get("status"),  # 'success', 'error', 'in_progress'
            "items_synced": sync_data.get("items_synced", 0),
            "errors": sync_data.get("errors", []),
            "timestamp": sync_data.get("timestamp"),
            "duration_ms": sync_data.get("duration_ms"),
        }

        return success_with_data({"status_updated": True}, "Sync status updated")

    except Exception as e:
        logger.error(f"Error updating sync status: {e}")
        return success_with_data({"status_updated": False, "error": str(e)})


@router.get("/cache-info")
async def get_cache_info(user: Annotated[User, Depends(get_current_user)]):
    """Get information about cached data"""

    # This would typically be handled client-side, but we can provide server-side cache info
    cache_info = {
        "server_cache": {
            "opportunities": {"ttl": 3600, "size": "~50 items"},
            "applications": {"ttl": 7200, "size": "~20 items"},
            "messages": {"ttl": 1800, "size": "~100 items"},
        },
        "recommended_client_storage": {
            "opportunities": "6 hours",
            "applications": "12 hours",
            "messages": "7 days",
            "profile": "24 hours",
            "calendar_events": "12 hours",
        },
        "cache_strategies": {
            "opportunities": "network_first",
            "applications": "cache_first",
            "messages": "network_first",
            "static_assets": "cache_first",
            "api_responses": "stale_while_revalidate",
        },
    }

    return success_with_data(cache_info, "Cache information retrieved")


@router.post("/clear-cache")
async def clear_client_cache(
    cache_types: List[str] = Query(default=["all"]),
    user: Annotated[User, Depends(get_current_user)] = None,
):
    """Trigger client-side cache clearing"""

    try:
        # This endpoint mainly serves as a trigger for client-side cache clearing
        # Actual cache clearing happens in the service worker

        clear_instructions = {
            "action": "clear_cache",
            "cache_types": cache_types,
            "timestamp": datetime.now().isoformat(),
            "user_id": user.id if user else None,
        }

        return success_with_data(
            clear_instructions, "Cache clear instructions sent to client"
        )

    except Exception as e:
        logger.error(f"Error processing cache clear request: {e}")
        return success_with_data({"error": str(e)})


@router.get("/capabilities")
async def get_pwa_capabilities(
    request: Request, user: Annotated[Optional[User], Depends(get_current_user)] = None
):
    """Get PWA capabilities and feature support"""

    try:
        user_agent = request.headers.get("user-agent", "").lower()

        # Detect browser capabilities
        capabilities = {
            "service_worker": True,  # Assume modern browser
            "push_notifications": True,
            "background_sync": True,
            "indexed_db": True,
            "cache_api": True,
            "web_share": "share" in user_agent or "mobile" in user_agent,
            "install_prompt": True,
            "offline_support": True,
            "file_system_access": "chrome" in user_agent and "mobile" not in user_agent,
            "camera_access": True,
            "geolocation": True,
            "device_orientation": "mobile" in user_agent,
        }

        # Feature availability based on user role
        features = {
            "offline_opportunity_browsing": True,
            "offline_application_viewing": True,
            "offline_message_viewing": True,
            "draft_saving": True,
            "background_sync": True,
            "push_notifications": capabilities["push_notifications"],
            "share_opportunities": capabilities["web_share"],
        }

        if user and user.role == "organization":
            features.update(
                {
                    "offline_application_management": True,
                    "offline_volunteer_profiles": True,
                    "opportunity_creation_drafts": True,
                }
            )

        response_data = {
            "capabilities": capabilities,
            "features": features,
            "browser_info": {
                "user_agent": request.headers.get("user-agent"),
                "is_mobile": "mobile" in user_agent,
                "is_pwa": request.headers.get("x-requested-with") == "seraaj-pwa",
            },
            "storage_quota": {
                "estimated": "~50MB",  # This would be calculated dynamically
                "persistent": False,  # Requires permission
            },
        }

        return success_with_data(response_data, "PWA capabilities retrieved")

    except Exception as e:
        logger.error(f"Error getting PWA capabilities: {e}")
        return success_with_data({"error": str(e)})


@router.post("/generate-files")
async def generate_pwa_files(
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    regenerate: bool = Query(False, description="Force regeneration of existing files"),
):
    """Generate PWA static files (admin only)"""

    if user.role != "admin":
        return JSONResponse(content={"error": "Admin access required"}, status_code=403)

    try:
        # Add background task to generate files
        background_tasks.add_task(generate_all_pwa_files, regenerate)

        return success_with_data(
            {"generation_started": True}, "PWA file generation started in background"
        )

    except Exception as e:
        logger.error(f"Error starting PWA file generation: {e}")
        return success_with_data({"error": str(e)})


async def generate_all_pwa_files(regenerate: bool = False):
    """Background task to generate all PWA files"""

    try:
        logger.info("Starting PWA file generation...")

        # Generate manifest files
        from pwa.manifest_generator import save_static_manifests

        save_static_manifests()

        # Generate service worker files
        from pwa.service_worker import save_service_worker_files

        save_service_worker_files()

        # Generate offline storage files
        generate_offline_storage_files()

        logger.info("PWA file generation completed successfully")

    except Exception as e:
        logger.error(f"Error in PWA file generation: {e}")


@router.get("/debug/storage-schema")
async def get_storage_schema(user: Annotated[User, Depends(get_current_user)]):
    """Get IndexedDB storage schema for debugging (dev only)"""

    if settings.environment.value != "development":
        return JSONResponse(
            content={"error": "Only available in development"}, status_code=403
        )

    manager = OfflineStorageManager()
    schema = manager.generate_storage_schema()

    return success_with_data(schema, "Storage schema retrieved")


# Share target handler for PWA
@router.post("/share")
async def handle_shared_content(
    request: Request, user: Annotated[Optional[User], Depends(get_current_user)] = None
):
    """Handle content shared to the PWA"""

    try:
        # Parse shared content
        form_data = await request.form()

        shared_data = {
            "title": form_data.get("title", ""),
            "text": form_data.get("text", ""),
            "url": form_data.get("url", ""),
            "files": [],
        }

        # Handle shared files
        if "images" in form_data:
            images = form_data.getlist("images")
            for image in images:
                if hasattr(image, "filename") and image.filename:
                    shared_data["files"].append(
                        {
                            "name": image.filename,
                            "type": "image",
                            "size": (
                                len(await image.read()) if hasattr(image, "read") else 0
                            ),
                        }
                    )

        # In a real implementation, you would process the shared content
        # For now, just return success with the parsed data

        logger.info(
            f"Received shared content from user {user.id if user else 'anonymous'}"
        )

        return success_with_data(
            {"received": True, "data": shared_data, "redirect_url": "/share/success"},
            "Shared content received",
        )

    except Exception as e:
        logger.error(f"Error handling shared content: {e}")
        return success_with_data({"error": str(e)})


from datetime import datetime
