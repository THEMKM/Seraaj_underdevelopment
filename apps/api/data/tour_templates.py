"""
Pre-built tour templates for different user types
"""
from models.guided_tour import TourType, UserRole, StepType

# Volunteer Onboarding Tour
VOLUNTEER_ONBOARDING = {
    "name": "Volunteer Onboarding",
    "description": "Complete introduction to Seraaj for new volunteers",
    "category": "onboarding",
    "target_role": UserRole.VOLUNTEER,
    "template_data": {
        "title": "Welcome to Seraaj!",
        "description": "Let's get you started with finding and applying to volunteer opportunities",
        "tour_type": TourType.ONBOARDING,
        "entry_url": "/",
        "duration": 8,
        "steps": [
            {
                "step_number": 1,
                "step_type": StepType.MODAL,
                "title": "Welcome to Seraaj! 🌟",
                "content": "Welcome to the MENA region's premier volunteer marketplace! We're excited to help you find meaningful opportunities to make a difference. This quick tour will show you around.",
                "target_selector": None,
                "target_url": "/",
                "position": "center",
                "primary_button_text": "Let's Start!",
                "secondary_button_text": "Skip Tour"
            },
            {
                "step_number": 2,
                "step_type": StepType.HIGHLIGHT,
                "title": "Discover Opportunities",
                "content": "Browse through hundreds of volunteer opportunities from verified organizations across the MENA region. Use filters to find what matches your interests and skills.",
                "target_selector": "#opportunities-section",
                "target_url": "/",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 3,
                "step_type": StepType.NAVIGATION,
                "title": "Explore Your Dashboard",
                "content": "Your personalized dashboard shows your applications, saved opportunities, and recommendations tailored just for you.",
                "target_selector": "#dashboard-link",
                "target_url": "/dashboard",
                "position": "bottom",
                "primary_button_text": "Visit Dashboard",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 4,
                "step_type": StepType.HIGHLIGHT,
                "title": "Track Your Applications",
                "content": "See all your applications in one place. Track their status from submitted to accepted, and communicate with organizations directly.",
                "target_selector": "#applications-card",
                "target_url": "/dashboard",
                "position": "right",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 5,
                "step_type": StepType.HIGHLIGHT,
                "title": "Build Your Profile",
                "content": "Complete your volunteer profile to get better matches. Add your skills, experience, and preferences to help organizations find you.",
                "target_selector": "#profile-completion",
                "target_url": "/dashboard",
                "position": "left",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 6,
                "step_type": StepType.NAVIGATION,
                "title": "Messages & Communication",
                "content": "Stay connected with organizations through our secure messaging system. Get updates about your applications and opportunities.",
                "target_selector": "#messages-link",
                "target_url": "/messages",
                "position": "bottom",
                "primary_button_text": "Check Messages",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 7,
                "step_type": StepType.TOOLTIP,
                "title": "Notifications",
                "content": "Enable push notifications to get instant updates about new opportunities that match your profile and application status changes.",
                "target_selector": "#notifications-bell",
                "target_url": "/messages",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 8,
                "step_type": StepType.MODAL,
                "title": "You're All Set! 🎉",
                "content": "Congratulations! You're ready to start your volunteering journey. Remember, you can always access help and tutorials from the help menu. Happy volunteering!",
                "target_selector": None,
                "target_url": "/messages",
                "position": "center",
                "primary_button_text": "Start Volunteering!",
                "secondary_button_text": None
            }
        ]
    }
}

# Organization Onboarding Tour
ORGANIZATION_ONBOARDING = {
    "name": "Organization Onboarding",
    "description": "Complete guide for organizations to post opportunities and manage volunteers",
    "category": "onboarding", 
    "target_role": UserRole.ORGANIZATION,
    "template_data": {
        "title": "Welcome to Seraaj Organizations!",
        "description": "Learn how to post opportunities, manage applications, and build your volunteer team",
        "tour_type": TourType.ONBOARDING,
        "entry_url": "/",
        "duration": 10,
        "steps": [
            {
                "step_number": 1,
                "step_type": StepType.MODAL,
                "title": "Welcome to Seraaj! 🏢",
                "content": "Welcome to Seraaj's organization portal! We're here to help you connect with passionate volunteers across the MENA region. Let's explore how to make the most of our platform.",
                "target_selector": None,
                "target_url": "/",
                "position": "center",
                "primary_button_text": "Get Started",
                "secondary_button_text": "Skip Tour"
            },
            {
                "step_number": 2,
                "step_type": StepType.NAVIGATION,
                "title": "Your Organization Dashboard",
                "content": "Your dashboard is mission control for all volunteer activities. Here you'll manage opportunities, review applications, and track your impact.",
                "target_selector": "#dashboard-link",
                "target_url": "/dashboard",
                "position": "bottom",
                "primary_button_text": "View Dashboard",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 3,
                "step_type": StepType.HIGHLIGHT,
                "title": "Post New Opportunities",
                "content": "Create compelling volunteer opportunities that attract the right volunteers. Include clear descriptions, requirements, and impact information.",
                "target_selector": "#create-opportunity-btn",
                "target_url": "/dashboard",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 4,
                "step_type": StepType.HIGHLIGHT,
                "title": "Manage Applications",
                "content": "Review volunteer applications, schedule interviews, and make decisions. Our smart matching helps surface the best candidates first.",
                "target_selector": "#applications-management",
                "target_url": "/dashboard",
                "position": "right",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 5,
                "step_type": StepType.HIGHLIGHT,
                "title": "Your Volunteer Team",
                "content": "Keep track of your active volunteers, their contributions, and maintain ongoing relationships for future opportunities.",
                "target_selector": "#volunteers-team",
                "target_url": "/dashboard",
                "position": "left",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 6,
                "step_type": StepType.NAVIGATION,
                "title": "Communication Hub",
                "content": "Communicate with volunteers through our secure messaging system. Send updates, coordinate activities, and build relationships.",
                "target_selector": "#messages-link",
                "target_url": "/messages",
                "position": "bottom",
                "primary_button_text": "Open Messages",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 7,
                "step_type": StepType.HIGHLIGHT,
                "title": "Organization Profile",
                "content": "Complete your organization profile to build trust with volunteers. Add your mission, photos, and verification badges.",
                "target_selector": "#org-profile-card",
                "target_url": "/profile",
                "position": "top",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 8,
                "step_type": StepType.HIGHLIGHT,
                "title": "Analytics & Impact",
                "content": "Track your volunteer program's success with detailed analytics. See applications, volunteer hours, and community impact metrics.",
                "target_selector": "#analytics-section",
                "target_url": "/analytics",
                "position": "top",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 9,
                "step_type": StepType.TOOLTIP,
                "title": "Payment & Donations",
                "content": "Accept donations from supporters and manage any fees for premium volunteer programs through our secure payment system.",
                "target_selector": "#payments-menu",
                "target_url": "/analytics",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 10,
                "step_type": StepType.MODAL,
                "title": "Ready to Make an Impact! 🚀",
                "content": "You're all set to start building your volunteer community! Post your first opportunity and watch passionate volunteers apply. Need help? Check our resource center anytime.",
                "target_selector": None,
                "target_url": "/analytics",
                "position": "center",
                "primary_button_text": "Post First Opportunity",
                "secondary_button_text": None
            }
        ]
    }
}

# Feature Introduction Tours
APPLICATION_PROCESS_TOUR = {
    "name": "Application Process Guide",
    "description": "Learn how to apply to opportunities effectively",
    "category": "feature_guide",
    "target_role": UserRole.VOLUNTEER,
    "template_data": {
        "title": "Master the Application Process",
        "description": "Learn how to create compelling applications that get you selected",
        "tour_type": TourType.FEATURE_INTRO,
        "entry_url": "/opportunities",
        "duration": 5,
        "steps": [
            {
                "step_number": 1,
                "step_type": StepType.HIGHLIGHT,
                "title": "Find the Right Opportunity",
                "content": "Look for opportunities that match your skills, interests, and availability. Pay attention to the requirements and time commitment.",
                "target_selector": "#opportunity-card",
                "target_url": "/opportunities",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 2,
                "step_type": StepType.HIGHLIGHT,
                "title": "Read the Details",
                "content": "Click on opportunities to read full descriptions, requirements, and learn about the organization. This helps you write a better application.",
                "target_selector": "#opportunity-details",
                "target_url": "/opportunities/1",
                "position": "right",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 3,
                "step_type": StepType.FORM_FILL,
                "title": "Craft Your Application",
                "content": "Write a compelling cover letter that shows your passion and relevant experience. Be specific about why you're interested and what you can contribute.",
                "target_selector": "#application-form",
                "target_url": "/opportunities/1/apply",
                "position": "top",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 4,
                "step_type": StepType.HIGHLIGHT,
                "title": "Upload Supporting Documents",
                "content": "If required, upload your CV, certificates, or portfolio. Make sure files are clear and relevant to the opportunity.",
                "target_selector": "#file-upload",
                "target_url": "/opportunities/1/apply",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 5,
                "step_type": StepType.MODAL,
                "title": "Application Submitted! ✅",
                "content": "Great job! Your application has been submitted. You'll receive updates via email and notifications. Organizations typically respond within 5-7 days.",
                "target_selector": None,
                "target_url": "/opportunities/1/apply",
                "position": "center",
                "primary_button_text": "View My Applications",
                "secondary_button_text": None
            }
        ]
    }
}

# Advanced Features Tour
PWA_FEATURES_TOUR = {
    "name": "Mobile & Offline Features",
    "description": "Discover Seraaj's mobile app-like features",
    "category": "advanced_features",
    "target_role": UserRole.ALL,
    "template_data": {
        "title": "Seraaj Mobile Experience",
        "description": "Learn about offline capabilities, push notifications, and mobile features",
        "tour_type": TourType.ADVANCED_FEATURES,
        "entry_url": "/",
        "duration": 4,
        "steps": [
            {
                "step_number": 1,
                "step_type": StepType.MODAL,
                "title": "Install Seraaj App 📱",
                "content": "Did you know Seraaj works like a mobile app? Install it on your phone or desktop for quick access and better performance!",
                "target_selector": None,
                "target_url": "/",
                "position": "center",
                "primary_button_text": "Learn How",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 2,
                "step_type": StepType.TOOLTIP,
                "title": "Push Notifications",
                "content": "Enable notifications to get instant updates about new opportunities, application status changes, and messages - even when the app is closed!",
                "target_selector": "#notification-settings",
                "target_url": "/settings",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 3,
                "step_type": StepType.HIGHLIGHT,
                "title": "Work Offline",
                "content": "Browse opportunities, read messages, and draft applications even without internet. Your changes sync automatically when you're back online.",
                "target_selector": "#offline-indicator",
                "target_url": "/opportunities",
                "position": "top",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 4,
                "step_type": StepType.MODAL,
                "title": "Enhanced Mobile Experience! 🌟",
                "content": "You now know how to make the most of Seraaj's mobile features. Enjoy faster loading, offline access, and instant notifications!",
                "target_selector": None,
                "target_url": "/opportunities",
                "position": "center",
                "primary_button_text": "Awesome!",
                "secondary_button_text": None
            }
        ]
    }
}

# Troubleshooting Tours
COMMON_ISSUES_TOUR = {
    "name": "Troubleshooting Common Issues",
    "description": "Solutions to frequently encountered problems",
    "category": "troubleshooting",
    "target_role": UserRole.ALL,
    "template_data": {
        "title": "Troubleshooting Guide",
        "description": "Quick solutions to common questions and issues",
        "tour_type": TourType.TROUBLESHOOTING,
        "entry_url": "/help",
        "duration": 3,
        "steps": [
            {
                "step_number": 1,
                "step_type": StepType.HIGHLIGHT,
                "title": "Application Status Questions",
                "content": "If you're wondering about your application status, check your dashboard. Organizations have up to 7 days to respond, and you'll get notified of any updates.",
                "target_selector": "#application-status-help",
                "target_url": "/help",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 2,
                "step_type": StepType.HIGHLIGHT,
                "title": "Profile Completion Issues",
                "content": "Having trouble completing your profile? Make sure all required fields are filled and your profile photo meets our guidelines (JPG/PNG, under 5MB).",
                "target_selector": "#profile-help",
                "target_url": "/help",
                "position": "bottom",
                "primary_button_text": "Next",
                "secondary_button_text": "Skip"
            },
            {
                "step_number": 3,
                "step_type": StepType.MODAL,
                "title": "Still Need Help? 💬",
                "content": "Can't find what you're looking for? Our support team is here to help! Use the chat button or email us at support@seraaj.org.",
                "target_selector": None,
                "target_url": "/help",
                "position": "center",
                "primary_button_text": "Contact Support",
                "secondary_button_text": "Close"
            }
        ]
    }
}

# All templates
ALL_TEMPLATES = [
    VOLUNTEER_ONBOARDING,
    ORGANIZATION_ONBOARDING,
    APPLICATION_PROCESS_TOUR,
    PWA_FEATURES_TOUR,
    COMMON_ISSUES_TOUR
]