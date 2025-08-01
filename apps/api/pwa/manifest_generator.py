"""
PWA Manifest Generation for Seraaj API
Generates web app manifests for Progressive Web App functionality
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from config.settings import settings


class PWAManifestGenerator:
    """Generate PWA manifest files and configurations"""
    
    def __init__(self):
        self.base_manifest = {
            "name": "Seraaj - Volunteer Marketplace",
            "short_name": "Seraaj",
            "description": "Connect volunteers with meaningful opportunities across the MENA region",
            "start_url": "/",
            "display": "standalone",
            "orientation": "portrait-primary",
            "theme_color": "#2563eb",  # Blue theme
            "background_color": "#ffffff",
            "lang": "en",
            "dir": "ltr",
            "scope": "/",
            "categories": ["social", "productivity", "utilities"],
            "prefer_related_applications": False,
            "protocol_handlers": [
                {
                    "protocol": "web+seraaj",
                    "url": "/app/share?url=%s"
                }
            ]
        }
    
    def generate_manifest(
        self, 
        user_preferences: Optional[Dict[str, Any]] = None,
        organization_branding: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate customized PWA manifest"""
        
        manifest = self.base_manifest.copy()
        
        # Add icons configuration
        manifest["icons"] = self._generate_icon_set()
        
        # Add shortcuts for quick actions
        manifest["shortcuts"] = self._generate_shortcuts()
        
        # Add share target for receiving shared content
        manifest["share_target"] = self._generate_share_target()
        
        # Customize based on user preferences
        if user_preferences:
            manifest = self._apply_user_preferences(manifest, user_preferences)
        
        # Apply organization branding if applicable
        if organization_branding:
            manifest = self._apply_organization_branding(manifest, organization_branding)
        
        # Add environment-specific configurations
        manifest = self._add_environment_config(manifest)
        
        return manifest
    
    def _generate_icon_set(self) -> List[Dict[str, Any]]:
        """Generate icon configurations for different sizes and purposes"""
        
        base_icon_path = "/static/icons"
        icon_sizes = [
            {"size": "72x72", "purpose": "any"},
            {"size": "96x96", "purpose": "any"},
            {"size": "128x128", "purpose": "any"},
            {"size": "144x144", "purpose": "any"},
            {"size": "152x152", "purpose": "any"},
            {"size": "192x192", "purpose": "any"},
            {"size": "384x384", "purpose": "any"},
            {"size": "512x512", "purpose": "any"},
            {"size": "192x192", "purpose": "maskable"},
            {"size": "512x512", "purpose": "maskable"},
        ]
        
        icons = []
        for icon_config in icon_sizes:
            size = icon_config["size"]
            purpose = icon_config["purpose"]
            
            icons.append({
                "src": f"{base_icon_path}/icon-{size}.png",
                "sizes": size,
                "type": "image/png",
                "purpose": purpose
            })
        
        # Add vector icon
        icons.append({
            "src": f"{base_icon_path}/icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any"
        })
        
        return icons
    
    def _generate_shortcuts(self) -> List[Dict[str, Any]]:
        """Generate app shortcuts for quick access to key features"""
        
        return [
            {
                "name": "Find Opportunities",
                "short_name": "Opportunities",
                "description": "Browse available volunteer opportunities",
                "url": "/opportunities",
                "icons": [
                    {
                        "src": "/static/icons/shortcut-opportunities.png",
                        "sizes": "96x96",
                        "type": "image/png"
                    }
                ]
            },
            {
                "name": "My Applications",
                "short_name": "Applications",
                "description": "View your volunteer applications",
                "url": "/applications",
                "icons": [
                    {
                        "src": "/static/icons/shortcut-applications.png",
                        "sizes": "96x96",
                        "type": "image/png"
                    }
                ]
            },
            {
                "name": "Messages",
                "short_name": "Messages",
                "description": "Check your messages",
                "url": "/messages",
                "icons": [
                    {
                        "src": "/static/icons/shortcut-messages.png",
                        "sizes": "96x96",
                        "type": "image/png"
                    }
                ]
            },
            {
                "name": "Calendar",
                "short_name": "Calendar",
                "description": "View your volunteer calendar",
                "url": "/calendar",
                "icons": [
                    {
                        "src": "/static/icons/shortcut-calendar.png",
                        "sizes": "96x96",
                        "type": "image/png"
                    }
                ]
            }
        ]
    
    def _generate_share_target(self) -> Dict[str, Any]:
        """Generate share target configuration for receiving shared content"""
        
        return {
            "action": "/app/share",
            "method": "POST",
            "enctype": "multipart/form-data",
            "params": {
                "title": "title",
                "text": "text",
                "url": "url",
                "files": [
                    {
                        "name": "images",
                        "accept": ["image/*"]
                    },
                    {
                        "name": "documents",
                        "accept": [".pdf", ".doc", ".docx"]
                    }
                ]
            }
        }
    
    def _apply_user_preferences(
        self, 
        manifest: Dict[str, Any], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply user-specific preferences to manifest"""
        
        # Theme customization
        if preferences.get("theme_color"):
            manifest["theme_color"] = preferences["theme_color"]
        
        if preferences.get("background_color"):
            manifest["background_color"] = preferences["background_color"]
        
        # Language and direction
        if preferences.get("language"):
            manifest["lang"] = preferences["language"]
            manifest["dir"] = "rtl" if preferences["language"] in ["ar", "he", "fa"] else "ltr"
        
        # Display mode preference
        if preferences.get("display_mode"):
            available_modes = ["standalone", "fullscreen", "minimal-ui", "browser"]
            if preferences["display_mode"] in available_modes:
                manifest["display"] = preferences["display_mode"]
        
        # Custom start URL based on user role
        if preferences.get("user_role"):
            role_start_urls = {
                "volunteer": "/volunteer/dashboard",
                "organization": "/organization/dashboard",
                "admin": "/admin/dashboard"
            }
            if preferences["user_role"] in role_start_urls:
                manifest["start_url"] = role_start_urls[preferences["user_role"]]
        
        return manifest
    
    def _apply_organization_branding(
        self, 
        manifest: Dict[str, Any], 
        branding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply organization-specific branding to manifest"""
        
        if branding.get("organization_name"):
            manifest["name"] = f"Seraaj - {branding['organization_name']}"
            manifest["short_name"] = branding.get("short_name", manifest["short_name"])
        
        if branding.get("theme_colors"):
            manifest["theme_color"] = branding["theme_colors"].get("primary", manifest["theme_color"])
            manifest["background_color"] = branding["theme_colors"].get("background", manifest["background_color"])
        
        if branding.get("custom_icons"):
            # Override default icons with organization-specific ones
            manifest["icons"] = branding["custom_icons"]
        
        return manifest
    
    def _add_environment_config(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Add environment-specific configurations"""
        
        # Development vs production settings
        if settings.environment.value == "development":
            manifest["start_url"] = f"http://localhost:{settings.port}/"
            manifest["scope"] = f"http://localhost:{settings.port}/"
        else:
            # Production settings would use actual domain
            manifest["start_url"] = "https://seraaj.org/"
            manifest["scope"] = "https://seraaj.org/"
        
        # Add version info
        manifest["version"] = settings.api.version
        manifest["generated_at"] = datetime.now(datetime.timezone.utc).isoformat()
        
        return manifest
    
    def generate_role_specific_manifest(self, user_role: str) -> Dict[str, Any]:
        """Generate role-specific PWA manifest"""
        
        role_configs = {
            "volunteer": {
                "name": "Seraaj Volunteer",
                "short_name": "Volunteer",
                "description": "Find and apply for volunteer opportunities",
                "theme_color": "#10b981",  # Green for volunteers
                "start_url": "/volunteer/dashboard",
                "shortcuts": [
                    {
                        "name": "Browse Opportunities",
                        "url": "/opportunities",
                        "icons": [{"src": "/static/icons/opportunities.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "My Applications",
                        "url": "/volunteer/applications",
                        "icons": [{"src": "/static/icons/applications.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "My Calendar",
                        "url": "/volunteer/calendar",
                        "icons": [{"src": "/static/icons/calendar.png", "sizes": "96x96"}]
                    }
                ]
            },
            "organization": {
                "name": "Seraaj Organization",
                "short_name": "Organization",
                "description": "Manage volunteers and opportunities",
                "theme_color": "#3b82f6",  # Blue for organizations
                "start_url": "/organization/dashboard",
                "shortcuts": [
                    {
                        "name": "Create Opportunity",
                        "url": "/organization/opportunities/create",
                        "icons": [{"src": "/static/icons/create.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "Manage Applications",
                        "url": "/organization/applications",
                        "icons": [{"src": "/static/icons/manage.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "Analytics",
                        "url": "/organization/analytics",
                        "icons": [{"src": "/static/icons/analytics.png", "sizes": "96x96"}]
                    }
                ]
            },
            "admin": {
                "name": "Seraaj Admin",
                "short_name": "Admin",
                "description": "Administer the Seraaj platform",
                "theme_color": "#dc2626",  # Red for admin
                "start_url": "/admin/dashboard",
                "shortcuts": [
                    {
                        "name": "User Management",
                        "url": "/admin/users",
                        "icons": [{"src": "/static/icons/users.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "System Health",
                        "url": "/admin/system",
                        "icons": [{"src": "/static/icons/system.png", "sizes": "96x96"}]
                    },
                    {
                        "name": "Analytics",
                        "url": "/admin/analytics",
                        "icons": [{"src": "/static/icons/analytics.png", "sizes": "96x96"}]
                    }
                ]
            }
        }
        
        base_manifest = self.generate_manifest()
        role_config = role_configs.get(user_role, {})
        
        # Merge role-specific config with base manifest
        for key, value in role_config.items():
            base_manifest[key] = value
        
        return base_manifest
    
    def save_manifest_file(self, manifest: Dict[str, Any], file_path: str) -> bool:
        """Save manifest to file"""
        
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write manifest file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving manifest file: {e}")
            return False
    
    def generate_offline_page_manifest(self) -> Dict[str, Any]:
        """Generate manifest for offline fallback page"""
        
        return {
            "name": "Seraaj Offline",
            "short_name": "Offline",
            "description": "Seraaj offline functionality",
            "start_url": "/offline",
            "display": "standalone",
            "theme_color": "#6b7280",
            "background_color": "#f9fafb",
            "icons": [
                {
                    "src": "/static/icons/offline-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }
            ]
        }


def generate_pwa_manifest(
    user_role: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None,
    organization_branding: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate PWA manifest with optional customizations"""
    
    generator = PWAManifestGenerator()
    
    if user_role:
        return generator.generate_role_specific_manifest(user_role)
    else:
        return generator.generate_manifest(user_preferences, organization_branding)


def save_static_manifests():
    """Generate and save static manifest files for different user types"""
    
    generator = PWAManifestGenerator()
    static_dir = Path("static/manifests")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate manifests for each user role
    for role in ["volunteer", "organization", "admin"]:
        manifest = generator.generate_role_specific_manifest(role)
        generator.save_manifest_file(
            manifest, 
            str(static_dir / f"manifest-{role}.json")
        )
    
    # Generate default manifest
    default_manifest = generator.generate_manifest()
    generator.save_manifest_file(
        default_manifest,
        str(static_dir / "manifest.json")
    )
    
    # Generate offline manifest
    offline_manifest = generator.generate_offline_page_manifest()
    generator.save_manifest_file(
        offline_manifest,
        str(static_dir / "manifest-offline.json")
    )
    
    print("Static PWA manifests generated successfully!")