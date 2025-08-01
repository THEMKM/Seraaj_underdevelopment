"""
Pre-built demo scenario templates for different use cases
"""
from models.demo_scenario import ScenarioType, DemoUserType, ActionType

# Volunteer Onboarding Demo
VOLUNTEER_ONBOARDING = {
    "name": "Volunteer Onboarding Journey",
    "description": "Complete volunteer journey from registration to first opportunity",
    "category": "onboarding",
    "scenario_type": ScenarioType.FULL_JOURNEY,
    "target_audience": "investors",
    "duration_minutes": 12,
    "difficulty_level": "beginner",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.NAVIGATE,
            "title": "Welcome to Seraaj",
            "description": "Navigate to the Seraaj homepage and explore the platform",
            "target_url": "/",
            "duration_seconds": 4,
            "annotation_text": "Welcome to Seraaj! This is where volunteers and organizations connect for meaningful impact.",
            "demo_user_type": DemoUserType.VISITOR
        },
        {
            "step_number": 2,
            "action_type": ActionType.CREATE_USER,
            "title": "Create Volunteer Account",
            "description": "Register as a new volunteer user",
            "target_element": "#volunteer-signup-btn",
            "duration_seconds": 3,
            "annotation_text": "Let's create a volunteer account to get started",
            "demo_user_type": DemoUserType.VOLUNTEER,
            "user_data": {
                "name": "Sarah Chen",
                "email": "sarah.chen@example.com",
                "location": "San Francisco, CA",
                "skills": ["Teaching", "Event Planning", "Social Media"]
            }
        },
        {
            "step_number": 3,
            "action_type": ActionType.LOGIN,
            "title": "Login to Account",
            "description": "Login with volunteer credentials",
            "target_element": "#login-form",
            "duration_seconds": 2,
            "annotation_text": "Secure login with email verification",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 4,
            "action_type": ActionType.NAVIGATE,
            "title": "Complete Profile",
            "description": "Navigate to profile completion page",
            "target_url": "/profile/complete",
            "duration_seconds": 3,
            "annotation_text": "Complete your profile to get better matches",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 5,
            "action_type": ActionType.FILL_FORM,
            "title": "Add Skills & Interests",
            "description": "Fill out skills, interests, and availability",
            "target_element": "#profile-form",
            "duration_seconds": 5,
            "form_data": {
                "bio": "Passionate educator with 5 years of experience teaching underprivileged children",
                "skills": ["Education", "Mentoring", "Curriculum Development"],
                "interests": ["Education", "Youth Development", "Community Building"],
                "availability": "Weekends, Evenings",
                "location": "San Francisco Bay Area"
            },
            "annotation_text": "Rich profile helps organizations find the perfect match",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 6,
            "action_type": ActionType.UPLOAD_FILE,
            "title": "Upload Profile Photo",
            "description": "Upload a professional profile photo",
            "target_element": "#photo-upload",
            "duration_seconds": 2,
            "annotation_text": "A photo helps build trust with organizations",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 7,
            "action_type": ActionType.NAVIGATE,
            "title": "Discover Opportunities",
            "description": "Browse available volunteer opportunities",
            "target_url": "/opportunities",
            "duration_seconds": 4,
            "annotation_text": "AI-powered matching shows the most relevant opportunities first",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 8,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "View Opportunity Details",
            "description": "Click on an education-focused opportunity",
            "target_element": ".opportunity-card:first-child",
            "duration_seconds": 3,
            "annotation_text": "Detailed opportunity information with organization verification",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 9,
            "action_type": ActionType.SUBMIT_APPLICATION,
            "title": "Apply for Opportunity",
            "description": "Submit application for the education opportunity",
            "target_element": "#apply-btn",
            "duration_seconds": 3,
            "form_data": {
                "motivation": "I'm excited to contribute my teaching skills to help students succeed",
                "experience": "5 years teaching experience, curriculum development background",
                "availability": "Saturdays 9am-2pm, Weekday evenings"
            },
            "annotation_text": "One-click application with pre-filled profile data",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 10,
            "action_type": ActionType.TRIGGER_NOTIFICATION,
            "title": "Application Confirmation",
            "description": "Receive push notification confirming application",
            "duration_seconds": 2,
            "annotation_text": "Instant confirmation and next steps notification",
            "demo_user_type": DemoUserType.VOLUNTEER
        }
    ]
}

# Organization Onboarding Demo
ORGANIZATION_ONBOARDING = {
    "name": "Organization Onboarding Journey",
    "description": "Complete organization journey from registration to volunteer matching",
    "category": "onboarding",
    "scenario_type": ScenarioType.FULL_JOURNEY,
    "target_audience": "investors",
    "duration_minutes": 15,
    "difficulty_level": "intermediate",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.NAVIGATE,
            "title": "Organization Portal",
            "description": "Navigate to organization registration",
            "target_url": "/organizations/register",
            "duration_seconds": 3,
            "annotation_text": "Dedicated portal for nonprofit organizations",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 2,
            "action_type": ActionType.CREATE_USER,
            "title": "Create Organization Account",
            "description": "Register organization with verification",
            "target_element": "#org-signup-form",
            "duration_seconds": 4,
            "annotation_text": "Verified organization accounts build volunteer trust",
            "demo_user_type": DemoUserType.ORGANIZATION,
            "user_data": {
                "name": "SF Education Foundation",
                "email": "coordinator@sfeducation.org",
                "type": "Education",
                "size": "50-100 employees",
                "ein": "12-3456789",
                "website": "https://sfeducation.org"
            }
        },
        {
            "step_number": 3,
            "action_type": ActionType.UPLOAD_FILE,
            "title": "Upload Verification Documents",
            "description": "Upload 501(c)(3) documentation",
            "target_element": "#verification-upload",
            "duration_seconds": 3,
            "annotation_text": "Document verification ensures legitimate organizations",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 4,
            "action_type": ActionType.LOGIN,
            "title": "Access Organization Dashboard",
            "description": "Login to organization dashboard",
            "target_element": "#org-login",
            "duration_seconds": 2,
            "annotation_text": "Comprehensive dashboard for managing volunteers",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 5,
            "action_type": ActionType.CREATE_OPPORTUNITY,
            "title": "Create First Opportunity",
            "description": "Create a new volunteer opportunity",
            "target_url": "/opportunities/create",
            "duration_seconds": 6,
            "form_data": {
                "title": "After-School Tutoring Program",
                "description": "Help students grades 3-8 with homework and reading skills",
                "category": "Education",
                "skills_required": ["Teaching", "Patience", "Math", "Reading"],
                "time_commitment": "2-3 hours per week",
                "location": "Mission District Community Center",
                "start_date": "2024-02-01",
                "volunteers_needed": 8
            },
            "annotation_text": "Rich opportunity creation with skills matching",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 6,
            "action_type": ActionType.NAVIGATE,
            "title": "Review Applications",
            "description": "Check volunteer applications",
            "target_url": "/organizations/applications",
            "duration_seconds": 4,
            "annotation_text": "AI pre-screens and ranks applications by fit",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 7,
            "action_type": ActionType.REVIEW_APPLICATION,
            "title": "Review Top Candidate",
            "description": "Review volunteer application and profile",
            "target_element": ".application-card:first-child",
            "duration_seconds": 4,
            "annotation_text": "Detailed volunteer profiles with verification badges",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 8,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "Accept Volunteer",
            "description": "Accept volunteer application",
            "target_element": "#accept-application-btn",
            "duration_seconds": 2,
            "annotation_text": "One-click acceptance with automatic notifications",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 9,
            "action_type": ActionType.SEND_MESSAGE,
            "title": "Send Welcome Message",
            "description": "Send personalized welcome message to volunteer",
            "target_element": "#message-compose",
            "duration_seconds": 3,
            "form_data": {
                "message": "Welcome to SF Education Foundation! We're excited to have you join our tutoring program. Your first session is this Saturday at 10am."
            },
            "annotation_text": "Built-in messaging for seamless communication",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 10,
            "action_type": ActionType.NAVIGATE,
            "title": "Schedule Coordination",
            "description": "Use calendar integration for scheduling",
            "target_url": "/organizations/calendar",
            "duration_seconds": 3,
            "annotation_text": "Calendar integration simplifies volunteer coordination",
            "demo_user_type": DemoUserType.ORGANIZATION
        },
        {
            "step_number": 11,
            "action_type": ActionType.GENERATE_REPORT,
            "title": "View Impact Metrics",
            "description": "Generate volunteer impact report",
            "target_element": "#generate-report-btn",
            "duration_seconds": 3,
            "annotation_text": "Comprehensive analytics track volunteer impact",
            "demo_user_type": DemoUserType.ORGANIZATION
        }
    ]
}

# PWA Features Showcase
PWA_FEATURES_DEMO = {
    "name": "Progressive Web App Features",
    "description": "Showcase offline capabilities and mobile features",
    "category": "features",
    "scenario_type": ScenarioType.FEATURE_SHOWCASE,
    "target_audience": "technical",
    "duration_minutes": 8,
    "difficulty_level": "intermediate",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.NAVIGATE,
            "title": "Install PWA",
            "description": "Show PWA installation prompt",
            "target_url": "/",
            "duration_seconds": 3,
            "annotation_text": "One-click installation as native app",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 2,
            "action_type": ActionType.TRIGGER_NOTIFICATION,
            "title": "Push Notifications",
            "description": "Demonstrate push notifications",
            "duration_seconds": 2,
            "annotation_text": "Native push notifications work even when app is closed",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 3,
            "action_type": ActionType.SIMULATE_OFFLINE,
            "title": "Offline Mode",
            "description": "Demonstrate offline functionality",
            "duration_seconds": 4,
            "annotation_text": "App works seamlessly offline with data sync when online",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 4,
            "action_type": ActionType.NAVIGATE,
            "title": "Cached Content",
            "description": "Show cached opportunities and profiles",
            "target_url": "/opportunities",
            "duration_seconds": 3,
            "annotation_text": "Previously viewed content available offline",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 5,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "Background Sync",
            "description": "Demonstrate background sync when online",
            "target_element": "#sync-btn",
            "duration_seconds": 3,
            "annotation_text": "Automatic sync when connection restored",
            "demo_user_type": DemoUserType.VOLUNTEER
        }
    ]
}

# Payment Integration Demo
PAYMENT_INTEGRATION_DEMO = {
    "name": "Donation & Payment Features",
    "description": "Showcase payment processing and donation features",
    "category": "features",
    "scenario_type": ScenarioType.FEATURE_SHOWCASE,
    "target_audience": "investors",
    "duration_minutes": 6,
    "difficulty_level": "intermediate",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.NAVIGATE,
            "title": "Organization Profile",
            "description": "View organization seeking donations",
            "target_url": "/organizations/sf-education-foundation",
            "duration_seconds": 3,
            "annotation_text": "Verified organizations can receive donations",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 2,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "Make Donation",
            "description": "Click donate button",
            "target_element": "#donate-btn",
            "duration_seconds": 2,
            "annotation_text": "Secure donation processing with multiple payment options",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 3,
            "action_type": ActionType.FILL_FORM,
            "title": "Donation Amount",
            "description": "Select donation amount and frequency",
            "target_element": "#donation-form",
            "duration_seconds": 3,
            "form_data": {
                "amount": 50,
                "frequency": "monthly",
                "designation": "After-School Program"
            },
            "annotation_text": "Flexible donation options including recurring payments",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 4,
            "action_type": ActionType.MAKE_PAYMENT,
            "title": "Process Payment",
            "description": "Complete secure payment",
            "target_element": "#payment-form",
            "duration_seconds": 4,
            "annotation_text": "Stripe integration ensures secure, PCI-compliant payments",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 5,
            "action_type": ActionType.GENERATE_REPORT,
            "title": "Donation Receipt",
            "description": "Generate tax-deductible receipt",
            "duration_seconds": 2,
            "annotation_text": "Automatic tax receipts for all donations",
            "demo_user_type": DemoUserType.VOLUNTEER
        }
    ]
}

# Admin Dashboard Demo
ADMIN_DASHBOARD_DEMO = {
    "name": "Admin Dashboard Overview",
    "description": "Comprehensive admin features and analytics",
    "category": "admin",
    "scenario_type": ScenarioType.FEATURE_SHOWCASE,
    "target_audience": "team",
    "duration_minutes": 10,
    "difficulty_level": "advanced",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.LOGIN,
            "title": "Admin Login",
            "description": "Login as platform administrator",
            "target_element": "#admin-login",
            "duration_seconds": 2,
            "annotation_text": "Secure admin access with multi-factor authentication",
            "demo_user_type": DemoUserType.ADMIN
        },
        {
            "step_number": 2,
            "action_type": ActionType.NAVIGATE,
            "title": "Dashboard Overview",
            "description": "View comprehensive platform analytics",
            "target_url": "/admin/dashboard",
            "duration_seconds": 4,
            "annotation_text": "Real-time platform metrics and KPIs",
            "demo_user_type": DemoUserType.ADMIN
        },
        {
            "step_number": 3,
            "action_type": ActionType.NAVIGATE,
            "title": "User Management",
            "description": "Manage volunteers and organizations",
            "target_url": "/admin/users",
            "duration_seconds": 3,
            "annotation_text": "Comprehensive user management with verification tools",
            "demo_user_type": DemoUserType.ADMIN
        },
        {
            "step_number": 4,
            "action_type": ActionType.VERIFY_SKILL,
            "title": "Verify Organization",
            "description": "Verify organization credentials",
            "target_element": ".pending-verification:first-child",
            "duration_seconds": 3,
            "annotation_text": "Streamlined verification process with document review",
            "demo_user_type": DemoUserType.ADMIN
        },
        {
            "step_number": 5,
            "action_type": ActionType.NAVIGATE,
            "title": "Content Moderation",
            "description": "Review flagged content and reports",
            "target_url": "/admin/moderation",
            "duration_seconds": 3,
            "annotation_text": "AI-assisted content moderation with human review",
            "demo_user_type": DemoUserType.ADMIN
        },
        {
            "step_number": 6,
            "action_type": ActionType.GENERATE_REPORT,
            "title": "Platform Analytics",
            "description": "Generate comprehensive platform report",
            "target_element": "#generate-analytics-btn",
            "duration_seconds": 4,
            "annotation_text": "Detailed analytics for growth and engagement tracking",
            "demo_user_type": DemoUserType.ADMIN
        }
    ]
}

# ML Matching Algorithm Demo
ML_MATCHING_DEMO = {
    "name": "AI-Powered Volunteer Matching",
    "description": "Showcase machine learning matching algorithm",
    "category": "features",
    "scenario_type": ScenarioType.FEATURE_SHOWCASE,
    "target_audience": "technical",
    "duration_minutes": 7,
    "difficulty_level": "advanced",
    "steps": [
        {
            "step_number": 1,
            "action_type": ActionType.NAVIGATE,
            "title": "Volunteer Profile",
            "description": "View volunteer with rich skill profile",
            "target_url": "/volunteers/sarah-chen",
            "duration_seconds": 3,
            "annotation_text": "Comprehensive skill and interest profiling",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 2,
            "action_type": ActionType.NAVIGATE,
            "title": "Smart Recommendations",
            "description": "View AI-generated opportunity recommendations",
            "target_url": "/opportunities/recommended",
            "duration_seconds": 4,
            "annotation_text": "ML algorithm considers skills, interests, location, and availability",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 3,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "Match Score Details",
            "description": "View detailed match scoring",
            "target_element": ".match-score:first-child",
            "duration_seconds": 3,
            "annotation_text": "Transparent scoring shows why opportunities match",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 4,
            "action_type": ActionType.NAVIGATE,
            "title": "Learning Algorithm",
            "description": "Show how algorithm learns from interactions",
            "target_url": "/profile/preferences",
            "duration_seconds": 3,
            "annotation_text": "Algorithm improves recommendations based on user feedback",
            "demo_user_type": DemoUserType.VOLUNTEER
        },
        {
            "step_number": 5,
            "action_type": ActionType.CLICK_BUTTON,
            "title": "Feedback Integration",
            "description": "Provide feedback on recommendations",
            "target_element": "#preference-feedback",
            "duration_seconds": 2,
            "annotation_text": "Continuous learning from user preferences",
            "demo_user_type": DemoUserType.VOLUNTEER
        }
    ]
}

# All available templates
DEMO_TEMPLATES = {
    "volunteer_onboarding": VOLUNTEER_ONBOARDING,
    "organization_onboarding": ORGANIZATION_ONBOARDING,
    "pwa_features": PWA_FEATURES_DEMO,
    "payment_integration": PAYMENT_INTEGRATION_DEMO,
    "admin_dashboard": ADMIN_DASHBOARD_DEMO,
    "ml_matching": ML_MATCHING_DEMO
}

# Categories for filtering
TEMPLATE_CATEGORIES = {
    "onboarding": ["volunteer_onboarding", "organization_onboarding"],
    "features": ["pwa_features", "payment_integration", "ml_matching"],
    "admin": ["admin_dashboard"],
    "technical": ["pwa_features", "ml_matching"]
}

# Template metadata for easier management
TEMPLATE_METADATA = [
    {
        "id": "volunteer_onboarding",
        "name": "Volunteer Onboarding Journey",
        "description": "Complete volunteer experience from registration to first opportunity",
        "category": "onboarding",
        "target_audience": "investors",
        "duration": 12,
        "step_count": 10,
        "featured": True
    },
    {
        "id": "organization_onboarding", 
        "name": "Organization Onboarding Journey",
        "description": "Full organization experience from signup to volunteer management",
        "category": "onboarding",
        "target_audience": "investors",
        "duration": 15,
        "step_count": 11,
        "featured": True
    },
    {
        "id": "pwa_features",
        "name": "Progressive Web App Features",
        "description": "Showcase mobile and offline capabilities",
        "category": "features",
        "target_audience": "technical",
        "duration": 8,
        "step_count": 5,
        "featured": False
    },
    {
        "id": "payment_integration",
        "name": "Donation & Payment Features",
        "description": "Secure payment processing and donation management",
        "category": "features", 
        "target_audience": "investors",
        "duration": 6,
        "step_count": 5,
        "featured": True
    },
    {
        "id": "admin_dashboard",
        "name": "Admin Dashboard Overview",
        "description": "Platform administration and analytics tools",
        "category": "admin",
        "target_audience": "team",
        "duration": 10,
        "step_count": 6,
        "featured": False
    },
    {
        "id": "ml_matching",
        "name": "AI-Powered Volunteer Matching",
        "description": "Machine learning matching algorithm demonstration",
        "category": "features",
        "target_audience": "technical", 
        "duration": 7,
        "step_count": 5,
        "featured": True
    }
]