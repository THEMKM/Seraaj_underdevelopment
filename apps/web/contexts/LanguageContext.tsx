"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';

type Language = 'en' | 'ar';
type Direction = 'ltr' | 'rtl';

interface LanguageContextType {
  language: Language;
  direction: Direction;
  toggleLanguage: () => void;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

// Translation dictionary
const translations = {
  en: {
    // Header & Navigation
    'nav.login': 'LOG IN',
    'nav.signup': 'SIGN UP',
    'nav.feed': 'FEED',
    'nav.applications': 'APPLICATIONS', 
    'nav.messages': 'MESSAGES',
    'nav.profile': 'PROFILE',
    'nav.dashboard': 'DASHBOARD',
    'nav.opportunities': 'OPPORTUNITIES',
    'nav.candidates': 'CANDIDATES',
    'nav.analytics': 'ANALYTICS',
    'nav.settings': 'SETTINGS',
    
    // Landing Page
    'landing.title': 'TURN GOODWILL INTO IMPACT',
    'landing.subtitle': 'Two-sided volunteer marketplace connecting passionate volunteers with under-resourced nonprofits across the MENA region.',
    'landing.cta.volunteer': 'FIND OPPORTUNITIES',
    'landing.cta.org': 'POST A ROLE',
    'landing.feature.volunteers.title': 'FOR VOLUNTEERS',
    'landing.feature.volunteers.desc': 'Personalized discovery feed, one-click applications, and in-app chat to connect with causes you care about.',
    'landing.feature.ngos.title': 'FOR NGOs',
    'landing.feature.ngos.desc': 'Lean applicant-tracking with ML-driven fit scores. See your "Recommended" volunteer within 10 seconds.',
    'landing.feature.impact.title': 'FOR IMPACT',
    'landing.feature.impact.desc': 'Platform moderation tools and analytics to ensure quality connections and measurable outcomes.',
    'landing.ready.title': 'READY TO MAKE A DIFFERENCE?',
    'landing.ready.desc': 'Join thousands of volunteers and nonprofits creating positive change.',
    'landing.ready.cta': 'GET STARTED NOW',
    'landing.search.title': 'FIND YOUR PERFECT MATCH',
    'landing.search.subtitle': 'Search thousands of volunteer opportunities in the MENA region',
    'landing.search.placeholder': 'Search by role, organization, or skill...',
    'landing.search.popular': 'POPULAR CAUSES:',
    'landing.search.stats.opportunities': 'Opportunities',
    'landing.search.stats.organizations': 'Organizations',
    'landing.search.stats.countries': 'Countries',
    
    // Feed Page
    'feed.title': 'YOUR PERSONALIZED FEED',
    'feed.subtitle': 'Opportunities matched to your skills, interests, and availability.',
    'feed.view.cards': '📋 CARDS',
    'feed.view.swipe': '🔥 SWIPE',
    'feed.badge.matches': 'NEW MATCHES',
    'feed.badge.pending': 'APPLICATIONS PENDING',
    'feed.causes': 'CAUSES:',
    'feed.skills': 'SKILLS:',
    'feed.apply': 'APPLY NOW',
    'feed.learn': 'LEARN MORE',
    'feed.save': 'SAVE FOR LATER',
    'feed.load': 'LOAD MORE OPPORTUNITIES',
    'feed.loading': 'LOADING...',
    'feed.match': 'MATCH',
    
    // Onboarding
    'onboarding.step': 'STEP',
    'onboarding.skip': 'SKIP FOR NOW',
    'onboarding.complete': 'COMPLETE SETUP',
    'onboarding.welcome.title': 'WELCOME TO SERAAJ',
    'onboarding.welcome.header': 'SERAAJ',
    'onboarding.welcome.subtitle': 'Turn Goodwill Into Impact',
    'onboarding.welcome.feature1.title': 'SMART MATCHING',
    'onboarding.welcome.feature1.desc': 'AI-powered matches based on your interests',
    'onboarding.welcome.feature2.title': 'INSTANT APPLY',
    'onboarding.welcome.feature2.desc': 'One-click applications with in-app chat',
    'onboarding.welcome.feature3.title': 'REAL IMPACT',
    'onboarding.welcome.feature3.desc': 'Track your contributions and see results',
    'onboarding.welcome.cta': 'Let\'s get you set up in just 5 quick steps!',
    'onboarding.welcome.start': 'GET STARTED',
    'onboarding.userType.title': 'CHOOSE YOUR PATH',
    'onboarding.userType.question': 'How would you like to use Seraaj?',
    'onboarding.userType.volunteer.title': 'VOLUNTEER',
    'onboarding.userType.volunteer.desc': 'Find meaningful opportunities to make a difference',
    'onboarding.userType.volunteer.feature1': 'Personalized opportunity feed',
    'onboarding.userType.volunteer.feature2': 'One-click applications',
    'onboarding.userType.volunteer.feature3': 'Direct messaging with organizations',
    'onboarding.userType.org.title': 'ORGANIZATION',
    'onboarding.userType.org.desc': 'Find passionate volunteers for your mission',
    'onboarding.userType.org.feature1': 'Post volunteer opportunities',
    'onboarding.userType.org.feature2': 'AI-powered candidate matching',
    'onboarding.userType.org.feature3': 'Streamlined applicant tracking',
    'onboarding.userType.features': 'What you get',
    'onboarding.userType.selected': 'SELECTED',
    'onboarding.userType.note': 'Don\'t worry, you can always change this later!',
    'onboarding.profile.title': 'TELL US ABOUT YOURSELF',
    'onboarding.profile.intro.volunteer': 'Help us create your volunteer profile so organizations can find you!',
    'onboarding.profile.intro.org': 'Set up your organization profile to attract the right volunteers.',
    'onboarding.profile.name': 'Full Name',
    'onboarding.profile.namePlaceholder': 'Your full name',
    'onboarding.profile.contactName': 'Contact Person',
    'onboarding.profile.contactNamePlaceholder': 'Primary contact name',
    'onboarding.profile.email': 'Email Address',
    'onboarding.profile.emailPlaceholder': 'your.email@example.com',
    'onboarding.profile.location': 'Location',
    'onboarding.profile.locationPlaceholder': 'Select your city',
    'onboarding.profile.bio': 'Tell us about yourself',
    'onboarding.profile.bioPlaceholder': 'Share your background, interests, and what motivates you to volunteer...',
    'onboarding.profile.orgName': 'Organization Name',
    'onboarding.profile.orgNamePlaceholder': 'Your organization\'s name',
    'onboarding.profile.orgDesc': 'Organization Description',
    'onboarding.profile.orgDescPlaceholder': 'Describe your organization\'s mission and impact...',
    'onboarding.profile.orgType': 'Organization Type',
    'onboarding.profile.orgTypePlaceholder': 'Select organization type',
    'onboarding.profile.orgTypes.nonprofit': 'Non-Profit Organization',
    'onboarding.profile.orgTypes.charity': 'Charitable Foundation',
    'onboarding.profile.orgTypes.ngo': 'NGO',
    'onboarding.profile.orgTypes.socialEnterprise': 'Social Enterprise',
    'onboarding.profile.orgTypes.communityGroup': 'Community Group',
    'onboarding.profile.orgSize': 'Organization Size',
    'onboarding.profile.orgSizePlaceholder': 'Select team size',
    'onboarding.profile.orgSizes.small': '1-5 people',
    'onboarding.profile.orgSizes.medium': '6-20 people',
    'onboarding.profile.orgSizes.large': '21-50 people',
    'onboarding.profile.orgSizes.xlarge': '50+ people',
    'onboarding.preferences.title': 'YOUR PREFERENCES',
    'onboarding.preferences.intro.volunteer': 'Help us understand what causes and types of work matter most to you.',
    'onboarding.preferences.intro.org': 'Tell us about the causes your organization focuses on.',
    'onboarding.preferences.causes.title': 'Causes You Care About',
    'onboarding.preferences.causes.desc.volunteer': 'Select the causes you\'re passionate about (choose at least one)',
    'onboarding.preferences.causes.desc.org': 'Select the causes your organization works on',
    'onboarding.preferences.skills.title': 'Your Skills & Expertise',
    'onboarding.preferences.skills.desc': 'What can you offer to organizations?',
    'onboarding.preferences.interests.title': 'Types of Volunteer Work',
    'onboarding.preferences.interests.desc': 'What kinds of volunteer activities interest you?',
    'onboarding.preferences.availability.title': 'Time Commitment',
    'onboarding.preferences.availability.desc': 'How many hours per week can you typically volunteer?',
    'onboarding.preferences.availability.hours': 'hours/week',
    'onboarding.preferences.availability.minimal': 'Perfect for busy schedules',
    'onboarding.preferences.availability.moderate': 'Regular commitment',
    'onboarding.preferences.availability.significant': 'Strong involvement',
    'onboarding.preferences.availability.extensive': 'Deep engagement',
    'onboarding.preferences.note': 'You can always update these preferences later in your profile.',
    'onboarding.completion.title': 'YOU\'RE ALL SET!',
    'onboarding.completion.success': 'Profile Complete!',
    'onboarding.completion.message.volunteer': 'Your volunteer profile is ready! We\'ll start showing you personalized opportunities.',
    'onboarding.completion.message.org': 'Your organization profile is ready! You can now start posting volunteer opportunities.',
    'onboarding.completion.summary': 'Profile Summary',
    'onboarding.completion.nextSteps.title': 'What\'s Next?',
    'onboarding.completion.nextSteps.volunteer.step1': 'Browse your personalized opportunity feed',
    'onboarding.completion.nextSteps.volunteer.step2': 'Apply to opportunities that interest you',
    'onboarding.completion.nextSteps.volunteer.step3': 'Connect with organizations via in-app messaging',
    'onboarding.completion.nextSteps.org.step1': 'Create your first volunteer opportunity posting',
    'onboarding.completion.nextSteps.org.step2': 'Review applications and connect with volunteers',
    'onboarding.completion.nextSteps.org.step3': 'Track your impact through our analytics dashboard',

    // Search & Filtering
    'search.placeholder': 'Search opportunities, organizations, or keywords...',
    'search.filters': 'FILTERS',
    'search.search': 'SEARCH',
    'search.advanced.title': 'Advanced Filters',
    'search.clearAll': 'CLEAR ALL',
    'search.location': 'Location',
    'search.anyLocation': 'Any Location',
    'search.remoteWork': 'Remote Work Available',
    'search.sortBy': 'Sort By',
    'search.sort.relevance': 'Relevance',
    'search.sort.date': 'Date Posted',
    'search.sort.matchScore': 'Match Score',
    'search.sort.timeCommitment': 'Time Commitment',
    'search.datePosted': 'Date Posted',
    'search.date.any': 'Anytime',
    'search.date.today': 'Today',
    'search.date.week': 'Past Week',
    'search.date.month': 'Past Month',
    'search.causes': 'Causes',
    'search.skills': 'Skills Required',
    'search.timeCommitment': 'Time Commitment',
    'search.opportunityType': 'Opportunity Type',
    'search.noFilters': 'No filters applied',
    'search.activeFilters': '{count} filters active',
    'search.applyFilters': 'APPLY FILTERS',
    'search.results.found': '{count} opportunities found',
    'search.results.for': 'for',
    'search.sortedBy': 'Sorted by',
    'search.featured': 'FEATURED',
    'search.remote': 'Remote',
    'search.urgency.high': 'URGENT',
    'search.urgency.medium': 'PRIORITY',
    'search.posted.today': 'Posted today',
    'search.posted.days': 'Posted {days} days ago',
    'search.posted.weeks': 'Posted {weeks} weeks ago',
    'search.posted.months': 'Posted {months} months ago',
    'search.applicants': '{count} applicants',
    'search.match': 'MATCH',
    'search.compatibility': 'Compatibility',
    'search.apply': 'APPLY NOW',
    'search.save': 'SAVE',
    'search.type': 'Type',
    'search.loading': 'LOADING...',
    'search.loadMore': 'LOAD MORE RESULTS',
    'search.noResults.title': 'No Opportunities Found',
    'search.noResults.withQuery': 'No results found for "{query}"',
    'search.noResults.general': 'Try adjusting your search criteria or filters',
    'search.noResults.tip1': 'Check your spelling and try different keywords',
    'search.noResults.tip2': 'Remove some filters to broaden your search',
    'search.noResults.tip3': 'Try searching for related causes or skills',
    'search.saved.title': 'Saved Searches',
    'search.saved.save': 'SAVE SEARCH',
    'search.saved.empty.title': 'No Saved Searches',
    'search.saved.empty.desc': 'Save your frequent searches to quickly find new opportunities',
    'search.saved.saveFirst': 'SAVE THIS SEARCH',
    'search.saved.newResults': 'new',
    'search.saved.alertOn': 'Alert notifications enabled',
    'search.saved.alertOff': 'Alert notifications disabled',
    'search.saved.delete': 'Delete saved search',
    'search.saved.lastRun': 'Last run',
    'search.saved.created': 'Created',
    'search.saved.today': 'today',
    'search.saved.daysAgo': '{days} days ago',
    'search.saved.weeksAgo': '{weeks} weeks ago',
    'search.saved.modal.title': 'Save Search',
    'search.saved.modal.desc': 'Save this search to quickly access it later and get notifications for new results.',
    'search.saved.modal.name': 'Search Name',
    'search.saved.modal.placeholder': 'e.g., "Education opportunities in Amman"',
    'search.saved.modal.preview': 'Search Preview',
    'search.saved.modal.save': 'SAVE SEARCH',

    // Profile Management
    'profile.tabs.edit': 'EDIT',
    'profile.tabs.preview': 'PREVIEW',
    'profile.tabs.history': 'HISTORY',
    'profile.completion.complete': 'COMPLETE',
    'profile.completion.good': 'STRONG',
    'profile.completion.basic': 'BASIC',
    'profile.completion.incomplete': 'INCOMPLETE',
    'profile.completion.score': 'Profile Score',
    'profile.completion.title': 'Profile Completion',
    'profile.completion.improve': 'Complete more sections to improve your profile score',
    'profile.completion.perfect': 'Your profile is complete! Great job!',
    'profile.verification.pending': 'PENDING',
    'profile.verification.premium': 'PREMIUM',
    'profile.verification.verified': 'VERIFIED',
    'profile.verification.basic': 'BASIC',
    'profile.lastUpdated': 'Last updated',
    'profile.save': 'SAVE CHANGES',
    'profile.edit': 'EDIT PROFILE',
    'profile.publicView': 'PUBLIC VIEW',
    'profile.publicView.title': 'Public Profile View',
    'profile.unsavedChanges': 'You have unsaved changes',
    'profile.unsavedChanges.desc': 'Your changes will be lost if you navigate away without saving',
    'profile.sections.basic': 'Basic Information',
    'profile.sections.skillsExpertise': 'Skills & Expertise',
    'profile.sections.interestsCauses': 'Interests & Causes',
    'profile.sections.organizationDetails': 'Organization Details',
    'profile.sections.privacy': 'Privacy Settings',
    'profile.fields.name': 'Full Name',
    'profile.fields.contactName': 'Contact Name',
    'profile.fields.email': 'Email Address',
    'profile.fields.location': 'Location',
    'profile.fields.bio': 'About You',
    'profile.fields.bio.placeholder': 'Tell us about yourself, your background, and what motivates you...',
    'profile.fields.organizationName': 'Organization Name',
    'profile.fields.organizationDescription': 'Organization Description',
    'profile.fields.organizationDescription.placeholder': 'Describe your organization\'s mission, impact, and goals...',
    'profile.fields.organizationType': 'Organization Type',
    'profile.fields.organizationType.placeholder': 'Select organization type',
    'profile.fields.website': 'Website',
    'profile.fields.founded': 'Founded Year',
    'profile.fields.organizationSize': 'Organization Size',
    'profile.fields.organizationSize.placeholder': 'Select team size',
    'profile.fields.people': 'people',
    'profile.fields.skills': 'Skills',
    'profile.fields.skills.selected': '{count} skills selected',
    'profile.fields.causes': 'Causes',
    'profile.fields.causes.selected': '{count} causes selected',
    'profile.fields.interests': 'Volunteer Interests',
    'profile.fields.interests.selected': '{count} interests selected',
    'profile.fields.focusAreas': 'Focus Areas',
    'profile.fields.focusAreas.selected': '{count} focus areas selected',
    'profile.fields.availability': 'Availability',
    'profile.fields.availability.placeholder': 'Select your availability',
    'profile.fields.hoursPerWeek': 'hours/week',
    'profile.fields.flexible': 'Flexible schedule',
    'profile.fields.languages': 'Languages',
    'profile.fields.experience': 'Volunteer Experience',
    'profile.fields.experience.placeholder': 'Share your volunteer experience, achievements, and memorable projects...',
    'profile.fields.characters': 'characters',
    'profile.fields.isPublic': 'Public Profile',
    'profile.orgTypes.nonprofit': 'Non-Profit Organization',
    'profile.orgTypes.charity': 'Charitable Foundation',
    'profile.orgTypes.ngo': 'NGO',
    'profile.orgTypes.socialEnterprise': 'Social Enterprise',
    'profile.orgTypes.communityGroup': 'Community Group',
    'profile.privacy.publicProfile': 'Public Profile',
    'profile.privacy.publicProfile.desc': 'Allow others to discover and contact you',
    'profile.preview.private.title': 'Private Profile',
    'profile.preview.private.desc': 'This profile is set to private and not visible to others',
    'profile.preview.makePublic': 'MAKE PUBLIC',
    'profile.actions.contact': 'CONTACT',
    'profile.actions.viewOpportunities': 'VIEW OPPORTUNITIES',
    'profile.actions.save': 'SAVE',
    'profile.actions.message': 'MESSAGE',
    'profile.cta.volunteer.title': 'Interested in working together?',
    'profile.cta.volunteer.desc': 'Send a message to connect with this volunteer',
    'profile.cta.volunteer.action': 'INVITE TO OPPORTUNITY',
    'profile.cta.organization.title': 'Want to volunteer?',
    'profile.cta.organization.desc': 'Explore opportunities with this organization',
    'profile.cta.organization.action': 'VIEW OPPORTUNITIES',
    'profile.history.title': 'Profile History',
    'profile.history.subtitle': '{count} versions available',
    'profile.history.version': 'Version',
    'profile.history.current': 'CURRENT',
    'profile.history.recent': 'RECENT',
    'profile.history.thisWeek': 'THIS WEEK',
    'profile.history.older': 'OLDER',
    'profile.history.today': 'today',
    'profile.history.daysAgo': '{days} days ago',
    'profile.history.weeksAgo': '{weeks} weeks ago',
    'profile.history.changes': 'changes',
    'profile.history.moreChanges': 'more changes',
    'profile.history.revert': 'REVERT',
    'profile.history.view': 'VIEW',
    'profile.history.versionDetails': 'Version {version} Details',
    'profile.history.updatedBy': 'Updated by',
    'profile.history.allChanges': 'All Changes',
    'profile.history.profileData': 'Profile Data',
    'profile.history.revertToThis': 'REVERT TO THIS VERSION',
    'profile.history.revertConfirm.title': 'Confirm Revert',
    'profile.history.revertConfirm.warning': 'Are you sure?',
    'profile.history.revertConfirm.desc': 'This will replace your current profile with the selected version. This action cannot be undone.',
    'profile.history.revertingTo': 'Reverting to',
    'profile.history.confirmRevert': 'CONFIRM REVERT',
    'profile.history.empty.title': 'No Version History',
    'profile.history.empty.desc': 'Profile versions will appear here as you make changes',

    // Messaging & Notifications
    'messaging.conversations': 'Conversations',
    'messaging.active': 'active',
    'messaging.noConversations': 'No conversations yet',
    'messaging.online': 'Online',
    'messaging.offline': 'Offline',
    'messaging.lastSeen.minutes': '{minutes}m ago',
    'messaging.lastSeen.hours': '{hours}h ago',
    'messaging.lastSeen.days': '{days}d ago',
    'messaging.noMessages': 'No messages yet',
    'messaging.call': 'CALL',
    'messaging.startConversation': 'Start a conversation',
    'messaging.firstMessage': 'Send your first message to begin the conversation',
    'messaging.typeMessage': 'Type a message...',
    'messaging.selectConversation': 'Select a conversation',
    'messaging.selectConversation.desc': 'Choose a conversation from the list to start messaging',
    'notifications.title': 'Notifications',
    'notifications.unreadCount': '{count} unread notifications',
    'notifications.allRead': 'All notifications read',
    'notifications.markAllRead': 'MARK ALL READ',
    'notifications.justNow': 'Just now',
    'notifications.minutesAgo': '{minutes}m ago',
    'notifications.hoursAgo': '{hours}h ago',
    'notifications.daysAgo': '{days}d ago',
    'notifications.filter.all': 'All',
    'notifications.filter.unread': 'Unread',
    'notifications.filter.messages': 'Messages',
    'notifications.filter.applications': 'Applications',
    'notifications.filter.matches': 'Matches',
    'notifications.noUnread.title': 'All caught up!',
    'notifications.noUnread.desc': 'No unread notifications at the moment',
    'notifications.noNotifications.title': 'No notifications',
    'notifications.noNotifications.desc': 'Notifications will appear here when you receive them',
    'notifications.showing': 'Showing {count} of {total}',
    'notifications.type.message': 'Message',
    'notifications.type.application': 'Application',
    'notifications.type.match': 'Match',
    'notifications.type.system': 'System',
    
    // Activity Feed
    'activity.title': 'Live Activity',
    'activity.live': 'LIVE',
    'activity.viewAll': 'VIEW ALL',
    'activity.noActivity': 'No recent activity',
    'activity.new': 'NEW',
    'activity.justNow': 'Just now',
    'activity.minutesAgo': '{minutes}m ago',
    'activity.hoursAgo': '{hours}h ago',
    'activity.daysAgo': '{days}d ago',
    'activity.userType.volunteer': 'Volunteer',
    'activity.userType.organization': 'Organization',
    'activity.lastUpdated': 'Last updated',
    'activity.refresh': 'REFRESH',

    // Common
    'common.or': 'or',
    'common.and': 'and',
    'common.of': 'of',
    'common.more': 'more',
    'common.next': 'NEXT',
    'common.close': 'Close',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.view': 'View',
    'common.back': 'BACK',
    
    // Analytics
    'analytics.title': 'Analytics Dashboard',
    'analytics.pageTitle': 'Analytics Dashboard',
    'analytics.pageSubtitle': 'Comprehensive insights into platform performance and user engagement',
    'analytics.subtitle.admin': 'Comprehensive platform insights and performance metrics',
    'analytics.subtitle.organization': 'Track your volunteer opportunities and applications',
    'analytics.subtitle.volunteer': 'Monitor your volunteer journey and impact',
    'analytics.export': 'EXPORT DATA',
    'analytics.demo.volunteer': 'Volunteer View',
    'analytics.demo.organization': 'Organization View',
    'analytics.demo.admin': 'Admin View',
    
    // Analytics Time Range
    'analytics.timeRange.7d': '7 Days',
    'analytics.timeRange.30d': '30 Days',
    'analytics.timeRange.90d': '90 Days',
    'analytics.timeRange.1y': '1 Year',
    
    // Analytics Tabs
    'analytics.tabs.overview': 'Overview',
    'analytics.tabs.growth': 'Growth',
    'analytics.tabs.engagement': 'Engagement',
    'analytics.tabs.performance': 'Performance',
    
    // Analytics Metrics
    'analytics.metrics.totalVolunteers': 'Total Volunteers',
    'analytics.metrics.totalOrganizations': 'Total Organizations',
    'analytics.metrics.totalOpportunities': 'Total Opportunities',
    'analytics.metrics.totalMatches': 'Total Matches',
    'analytics.metrics.newVolunteersMonth': 'New Volunteers This Month',
    'analytics.metrics.newOpportunitiesMonth': 'New Opportunities This Month',
    'analytics.metrics.growthRate': 'Growth Rate',
    'analytics.metrics.messagesSent': 'Messages Sent',
    'analytics.metrics.profileViews': 'Profile Views',
    'analytics.metrics.searchesPerformed': 'Searches Performed',
    'analytics.metrics.applicationsSubmitted': 'Applications Submitted',
    'analytics.metrics.applicationSuccessRate': 'Application Success Rate',
    'analytics.metrics.averageMatchScore': 'Average Match Score',
    'analytics.metrics.responseTime': 'Response Time',
    'analytics.metrics.retentionRate': 'Retention Rate',
    
    // Analytics Charts
    'analytics.charts.topCities': 'Top Cities',
    'analytics.charts.popularCauses': 'Popular Causes',
    'analytics.charts.growthTrend': 'Growth Trend',
    'analytics.charts.activityByHour': 'Activity by Hour',
    'analytics.charts.activityByHour.desc': 'Peak activity hours (24-hour format)',
    
    // Analytics Legend
    'analytics.legend.volunteers': 'Volunteers',
    'analytics.legend.organizations': 'Organizations',
    
    // Analytics Performance
    'analytics.performance.satisfactionScore': 'User Satisfaction Score',
    'analytics.performance.satisfactionScore.desc': 'Based on user feedback and ratings',
    'analytics.performance.systemHealth': 'System Health',
    'analytics.performance.uptime': 'Uptime',
    'analytics.performance.apiResponse': 'API Response Time',
    'analytics.performance.errorRate': 'Error Rate',
    
    // Admin Console
    'admin.title': 'Admin Console',
    'admin.subtitle': 'Comprehensive platform management and monitoring tools',
    'admin.auth.title': 'Admin Access Required',
    'admin.auth.subtitle': 'Enter your admin code to access the console',
    'admin.auth.placeholder': 'Enter admin code...',
    'admin.auth.submit': 'ACCESS CONSOLE',
    'admin.auth.demo': 'Demo Code',
    
    // Admin Tabs
    'admin.tabs.overview': 'Overview',
    'admin.tabs.users': 'Users',
    'admin.tabs.reports': 'Reports',
    'admin.tabs.content': 'Content',
    'admin.tabs.system': 'System',
    
    // Admin Stats
    'admin.stats.totalUsers': 'Total Users',
    'admin.stats.pendingReports': 'Pending Reports',
    'admin.stats.suspendedUsers': 'Suspended Users',
    'admin.stats.systemUptime': 'System Uptime',
    
    // Admin Activity & Alerts
    'admin.recentActivity': 'Recent Activity',
    'admin.systemAlerts': 'System Alerts',
    
    // Admin Users
    'admin.searchUsers': 'Search users...',
    'admin.userDetails': 'User Details',
    'admin.exportLogs': 'EXPORT LOGS',
    
    // Admin Filters
    'admin.filters.all': 'All',
    'admin.filters.volunteers': 'Volunteers',
    'admin.filters.organizations': 'Organizations',
    
    // Admin Table Headers
    'admin.table.name': 'Name',
    'admin.table.type': 'Type',
    'admin.table.status': 'Status',
    'admin.table.joinDate': 'Join Date',
    'admin.table.reports': 'Reports',
    'admin.table.actions': 'Actions',
    
    // Admin User Types
    'admin.userType.volunteer': 'Volunteer',
    'admin.userType.organization': 'Organization',
    
    // Admin Status
    'admin.status.active': 'Active',
    'admin.status.suspended': 'Suspended',
    'admin.status.pending': 'Pending',
    'admin.status.online': 'ONLINE',
    
    // Admin Actions
    'admin.actions.view': 'View',
    'admin.actions.suspend': 'Suspend',
    'admin.actions.review': 'Review',
    'admin.actions.resolve': 'Resolve',
    'admin.actions.dismiss': 'Dismiss',
    
    // Admin Reports
    'admin.priority.high': 'HIGH',
    'admin.priority.medium': 'MEDIUM',
    'admin.priority.low': 'LOW',
    'admin.priority.critical': 'CRITICAL',
    
    'admin.reportType.user': 'User',
    'admin.reportType.opportunity': 'Opportunity',
    'admin.reportType.message': 'Message',
    
    // Admin System
    'admin.system.maintenance': 'Maintenance Mode',
    'admin.system.monitoring': 'System Monitoring',
    'admin.system.enableMaintenance': 'Enable Maintenance Mode', 
    'admin.system.clearCache': 'Clear System Cache',
    'admin.system.backupDatabase': 'Backup Database',
    'admin.system.serverStatus': 'Server Status',
    'admin.system.databaseStatus': 'Database Status',
    'admin.system.queueStatus': 'Queue Status',
    
    // Demo Seed Data
    'demo.seedData.title': 'Demo Data Generator',
    'demo.seedData.description': 'Generate comprehensive demo data to showcase Seraaj v2 features',
    'demo.seedData.generate': 'GENERATE DEMO DATA',
    'demo.seedData.loading': 'GENERATING...',
    'demo.seedData.clear': 'CLEAR DATA',
    'demo.seedData.loaded': 'Demo data loaded on',
  },
  ar: {
    // Header & Navigation  
    'nav.login': 'تسجيل الدخول',
    'nav.signup': 'إنشاء حساب',
    'nav.feed': 'التغذية',
    'nav.applications': 'الطلبات',
    'nav.messages': 'الرسائل',
    'nav.profile': 'الملف الشخصي',
    'nav.dashboard': 'لوحة التحكم',
    'nav.opportunities': 'الفرص',
    'nav.candidates': 'المرشحون',
    'nav.analytics': 'التحليلات',
    'nav.settings': 'الإعدادات',
    
    // Landing Page
    'landing.title': 'حوّل النوايا الحسنة إلى تأثير',
    'landing.subtitle': 'منصة تطوع ثنائية الاتجاه تربط المتطوعين المتحمسين بالمنظمات غير الربحية ذات الموارد المحدودة في منطقة الشرق الأوسط وشمال أفريقيا.',
    'landing.cta.volunteer': 'ابحث عن الفرص',
    'landing.cta.org': 'انشر دوراً',
    'landing.feature.volunteers.title': 'للمتطوعين',
    'landing.feature.volunteers.desc': 'تغذية اكتشاف مخصصة، تطبيقات بنقرة واحدة، ودردشة داخل التطبيق للتواصل مع القضايا التي تهتم بها.',
    'landing.feature.ngos.title': 'للمنظمات',
    'landing.feature.ngos.desc': 'تتبع سهل للمتقدمين مع درجات ملاءمة مدفوعة بالذكاء الاصطناعي. شاهد متطوعك "الموصى به" خلال 10 ثوانٍ.',
    'landing.feature.impact.title': 'للتأثير',
    'landing.feature.impact.desc': 'أدوات إشراف المنصة والتحليلات لضمان اتصالات عالية الجودة ونتائج قابلة للقياس.',
    'landing.ready.title': 'مستعد لإحداث فرق؟',
    'landing.ready.desc': 'انضم إلى آلاف المتطوعين والمنظمات غير الربحية التي تخلق تغييراً إيجابياً.',
    'landing.ready.cta': 'ابدأ الآن',
    'landing.search.title': 'ابحث عن التطابق المثالي',
    'landing.search.subtitle': 'ابحث في آلاف فرص التطوع في منطقة الشرق الأوسط وشمال أفريقيا',
    'landing.search.placeholder': 'ابحث حسب الدور أو المنظمة أو المهارة...',
    'landing.search.popular': 'القضايا الشائعة:',
    'landing.search.stats.opportunities': 'الفرص',
    'landing.search.stats.organizations': 'المنظمات',
    'landing.search.stats.countries': 'البلدان',
    
    // Feed Page
    'feed.title': 'تغذيتك المخصصة',
    'feed.subtitle': 'فرص تتناسب مع مهاراتك واهتماماتك وتوافرك.',
    'feed.view.cards': '📋 البطاقات',
    'feed.view.swipe': '🔥 السحب',
    'feed.badge.matches': 'تطابقات جديدة',
    'feed.badge.pending': 'طلبات معلقة',
    'feed.causes': 'القضايا:',
    'feed.skills': 'المهارات:',
    'feed.apply': 'تقدم الآن',
    'feed.learn': 'اعرف المزيد',
    'feed.save': 'احفظ للاحقاً',
    'feed.load': 'تحميل المزيد من الفرص',
    'feed.loading': 'جاري التحميل...',
    'feed.match': 'تطابق',
    
    // Onboarding
    'onboarding.step': 'الخطوة',
    'onboarding.skip': 'تخطي الآن',
    'onboarding.complete': 'إكمال الإعداد',
    'onboarding.welcome.title': 'مرحباً بك في سراج',
    'onboarding.welcome.header': 'سراج',
    'onboarding.welcome.subtitle': 'حوّل النوايا الحسنة إلى تأثير',
    'onboarding.welcome.feature1.title': 'المطابقة الذكية',
    'onboarding.welcome.feature1.desc': 'مطابقات مدفوعة بالذكاء الاصطناعي حسب اهتماماتك',
    'onboarding.welcome.feature2.title': 'التقديم الفوري',
    'onboarding.welcome.feature2.desc': 'تطبيقات بنقرة واحدة مع الدردشة داخل التطبيق',
    'onboarding.welcome.feature3.title': 'التأثير الحقيقي',
    'onboarding.welcome.feature3.desc': 'تتبع مساهماتك وشاهد النتائج',
    'onboarding.welcome.cta': 'دعنا نساعدك في الإعداد في 5 خطوات سريعة فقط!',
    'onboarding.welcome.start': 'ابدأ الآن',
    'onboarding.userType.title': 'اختر مسارك',
    'onboarding.userType.question': 'كيف تريد استخدام سراج؟',
    'onboarding.userType.volunteer.title': 'متطوع',
    'onboarding.userType.volunteer.desc': 'ابحث عن فرص ذات معنى لإحداث فرق',
    'onboarding.userType.volunteer.feature1': 'تغذية فرص مخصصة',
    'onboarding.userType.volunteer.feature2': 'تطبيقات بنقرة واحدة',
    'onboarding.userType.volunteer.feature3': 'التراسل المباشر مع المنظمات',
    'onboarding.userType.org.title': 'منظمة',
    'onboarding.userType.org.desc': 'ابحث عن متطوعين متحمسين لمهمتك',
    'onboarding.userType.org.feature1': 'نشر فرص التطوع',
    'onboarding.userType.org.feature2': 'مطابقة المرشحين بالذكاء الاصطناعي',
    'onboarding.userType.org.feature3': 'تتبع مبسط للمتقدمين',
    'onboarding.userType.features': 'ما ستحصل عليه',
    'onboarding.userType.selected': 'محدد',
    'onboarding.userType.note': 'لا تقلق، يمكنك دائماً تغيير هذا لاحقاً!',
    'onboarding.profile.title': 'أخبرنا عن نفسك',
    'onboarding.profile.intro.volunteer': 'ساعدنا في إنشاء ملفك التطوعي حتى تتمكن المنظمات من العثور عليك!',
    'onboarding.profile.intro.org': 'أعد ملف منظمتك لجذب المتطوعين المناسبين.',
    'onboarding.profile.name': 'الاسم الكامل',
    'onboarding.profile.namePlaceholder': 'اسمك الكامل',
    'onboarding.profile.contactName': 'شخص الاتصال',
    'onboarding.profile.contactNamePlaceholder': 'اسم جهة الاتصال الأساسية',
    'onboarding.profile.email': 'عنوان البريد الإلكتروني',
    'onboarding.profile.emailPlaceholder': 'your.email@example.com',
    'onboarding.profile.location': 'الموقع',
    'onboarding.profile.locationPlaceholder': 'اختر مدينتك',
    'onboarding.profile.bio': 'أخبرنا عن نفسك',
    'onboarding.profile.bioPlaceholder': 'شارك خلفيتك واهتماماتك وما يحفزك للتطوع...',
    'onboarding.profile.orgName': 'اسم المنظمة',
    'onboarding.profile.orgNamePlaceholder': 'اسم منظمتك',
    'onboarding.profile.orgDesc': 'وصف المنظمة',
    'onboarding.profile.orgDescPlaceholder': 'صف مهمة منظمتك وتأثيرها...',
    'onboarding.profile.orgType': 'نوع المنظمة',
    'onboarding.profile.orgTypePlaceholder': 'اختر نوع المنظمة',
    'onboarding.profile.orgTypes.nonprofit': 'منظمة غير ربحية',
    'onboarding.profile.orgTypes.charity': 'مؤسسة خيرية',
    'onboarding.profile.orgTypes.ngo': 'منظمة غير حكومية',
    'onboarding.profile.orgTypes.socialEnterprise': 'مؤسسة اجتماعية',
    'onboarding.profile.orgTypes.communityGroup': 'مجموعة مجتمعية',
    'onboarding.profile.orgSize': 'حجم المنظمة',
    'onboarding.profile.orgSizePlaceholder': 'اختر حجم الفريق',
    'onboarding.profile.orgSizes.small': '1-5 أشخاص',
    'onboarding.profile.orgSizes.medium': '6-20 شخص',
    'onboarding.profile.orgSizes.large': '21-50 شخص',
    'onboarding.profile.orgSizes.xlarge': '50+ شخص',
    'onboarding.preferences.title': 'تفضيلاتك',
    'onboarding.preferences.intro.volunteer': 'ساعدنا في فهم القضايا وأنواع العمل الأكثر أهمية بالنسبة لك.',
    'onboarding.preferences.intro.org': 'أخبرنا عن القضايا التي تركز عليها منظمتك.',
    'onboarding.preferences.causes.title': 'القضايا التي تهتم بها',
    'onboarding.preferences.causes.desc.volunteer': 'اختر القضايا التي تتحمس لها (اختر واحدة على الأقل)',
    'onboarding.preferences.causes.desc.org': 'اختر القضايا التي تعمل عليها منظمتك',
    'onboarding.preferences.skills.title': 'مهاراتك وخبراتك',
    'onboarding.preferences.skills.desc': 'ما الذي يمكنك تقديمه للمنظمات؟',
    'onboarding.preferences.interests.title': 'أنواع العمل التطوعي',
    'onboarding.preferences.interests.desc': 'ما أنواع الأنشطة التطوعية التي تهمك؟',
    'onboarding.preferences.availability.title': 'الالتزام الزمني',
    'onboarding.preferences.availability.desc': 'كم ساعة في الأسبوع يمكنك التطوع عادة؟',
    'onboarding.preferences.availability.hours': 'ساعة/أسبوع',
    'onboarding.preferences.availability.minimal': 'مثالي للجداول المزدحمة',
    'onboarding.preferences.availability.moderate': 'التزام منتظم',
    'onboarding.preferences.availability.significant': 'مشاركة قوية',
    'onboarding.preferences.availability.extensive': 'انخراط عميق',
    'onboarding.preferences.note': 'يمكنك دائماً تحديث هذه التفضيلات لاحقاً في ملفك الشخصي.',
    'onboarding.completion.title': 'انتهيت!',
    'onboarding.completion.success': 'الملف الشخصي مكتمل!',
    'onboarding.completion.message.volunteer': 'ملفك التطوعي جاهز! سنبدأ في عرض الفرص المخصصة لك.',
    'onboarding.completion.message.org': 'ملف منظمتك جاهز! يمكنك الآن البدء في نشر فرص التطوع.',
    'onboarding.completion.summary': 'ملخص الملف الشخصي',
    'onboarding.completion.nextSteps.title': 'ما التالي؟',
    'onboarding.completion.nextSteps.volunteer.step1': 'تصفح تغذية الفرص المخصصة لك',
    'onboarding.completion.nextSteps.volunteer.step2': 'تقدم للفرص التي تهمك',
    'onboarding.completion.nextSteps.volunteer.step3': 'تواصل مع المنظمات عبر الرسائل داخل التطبيق',
    'onboarding.completion.nextSteps.org.step1': 'أنشئ أول منشور فرصة تطوع',
    'onboarding.completion.nextSteps.org.step2': 'راجع الطلبات وتواصل مع المتطوعين',
    'onboarding.completion.nextSteps.org.step3': 'تتبع تأثيرك من خلال لوحة التحليلات',

    // Search & Filtering
    'search.placeholder': 'ابحث عن الفرص أو المنظمات أو الكلمات المفتاحية...',
    'search.filters': 'المرشحات',
    'search.search': 'بحث',
    'search.advanced.title': 'المرشحات المتقدمة',
    'search.clearAll': 'مسح الكل',
    'search.location': 'الموقع',
    'search.anyLocation': 'أي موقع',
    'search.remoteWork': 'العمل عن بُعد متاح',
    'search.sortBy': 'ترتيب حسب',
    'search.sort.relevance': 'الصلة',
    'search.sort.date': 'تاريخ النشر',
    'search.sort.matchScore': 'درجة التطابق',
    'search.sort.timeCommitment': 'الالتزام الزمني',
    'search.datePosted': 'تاريخ النشر',
    'search.date.any': 'أي وقت',
    'search.date.today': 'اليوم',
    'search.date.week': 'الأسبوع الماضي',
    'search.date.month': 'الشهر الماضي',
    'search.causes': 'القضايا',
    'search.skills': 'المهارات المطلوبة',
    'search.timeCommitment': 'الالتزام الزمني',
    'search.opportunityType': 'نوع الفرصة',
    'search.noFilters': 'لم يتم تطبيق مرشحات',
    'search.activeFilters': '{count} مرشحات نشطة',
    'search.applyFilters': 'تطبيق المرشحات',
    'search.results.found': 'تم العثور على {count} فرصة',
    'search.results.for': 'لـ',
    'search.sortedBy': 'مرتب حسب',
    'search.featured': 'مميز',
    'search.remote': 'عن بُعد',
    'search.urgency.high': 'عاجل',
    'search.urgency.medium': 'أولوية',
    'search.posted.today': 'نُشر اليوم',
    'search.posted.days': 'نُشر منذ {days} أيام',
    'search.posted.weeks': 'نُشر منذ {weeks} أسابيع',
    'search.posted.months': 'نُشر منذ {months} شهور',
    'search.applicants': '{count} متقدم',
    'search.match': 'تطابق',
    'search.compatibility': 'التوافق',
    'search.apply': 'تقدم الآن',
    'search.save': 'حفظ',
    'search.type': 'النوع',
    'search.loading': 'جاري التحميل...',
    'search.loadMore': 'تحميل المزيد من النتائج',
    'search.noResults.title': 'لم يتم العثور على فرص',
    'search.noResults.withQuery': 'لم يتم العثور على نتائج لـ "{query}"',
    'search.noResults.general': 'جرب تعديل معايير البحث أو المرشحات',
    'search.noResults.tip1': 'تحقق من الإملاء وجرب كلمات مفتاحية مختلفة',
    'search.noResults.tip2': 'أزل بعض المرشحات لتوسيع البحث',
    'search.noResults.tip3': 'جرب البحث عن قضايا أو مهارات ذات صلة',
    'search.saved.title': 'عمليات البحث المحفوظة',
    'search.saved.save': 'حفظ البحث',
    'search.saved.empty.title': 'لا توجد عمليات بحث محفوظة',
    'search.saved.empty.desc': 'احفظ عمليات البحث المتكررة للعثور بسرعة على فرص جديدة',
    'search.saved.saveFirst': 'احفظ هذا البحث',
    'search.saved.newResults': 'جديد',
    'search.saved.alertOn': 'إشعارات التنبيه مفعلة',
    'search.saved.alertOff': 'إشعارات التنبيه معطلة',
    'search.saved.delete': 'حذف البحث المحفوظ',
    'search.saved.lastRun': 'آخر تشغيل',
    'search.saved.created': 'تم الإنشاء',
    'search.saved.today': 'اليوم',
    'search.saved.daysAgo': 'منذ {days} أيام',
    'search.saved.weeksAgo': 'منذ {weeks} أسابيع',
    'search.saved.modal.title': 'حفظ البحث',
    'search.saved.modal.desc': 'احفظ هذا البحث للوصول إليه بسرعة لاحقاً والحصول على إشعارات للنتائج الجديدة.',
    'search.saved.modal.name': 'اسم البحث',
    'search.saved.modal.placeholder': 'مثال: "فرص التعليم في عمان"',
    'search.saved.modal.preview': 'معاينة البحث',
    'search.saved.modal.save': 'حفظ البحث',

    // Messaging & Notifications
    'messaging.conversations': 'المحادثات',
    'messaging.active': 'نشط',
    'messaging.noConversations': 'لا توجد محادثات بعد',
    'messaging.online': 'متصل',
    'messaging.offline': 'غير متصل',
    'messaging.lastSeen.minutes': 'منذ {minutes} دقيقة',
    'messaging.lastSeen.hours': 'منذ {hours} ساعة',
    'messaging.lastSeen.days': 'منذ {days} يوم',
    'messaging.noMessages': 'لا توجد رسائل بعد',
    'messaging.call': 'اتصال',
    'messaging.startConversation': 'بدء محادثة',
    'messaging.firstMessage': 'أرسل رسالتك الأولى لبدء المحادثة',
    'messaging.typeMessage': 'اكتب رسالة...',
    'messaging.selectConversation': 'اختر محادثة',
    'messaging.selectConversation.desc': 'اختر محادثة من القائمة لبدء المراسلة',
    'notifications.title': 'الإشعارات',
    'notifications.unreadCount': '{count} إشعارات غير مقروءة',
    'notifications.allRead': 'جميع الإشعارات مقروءة',
    'notifications.markAllRead': 'تحديد الكل كمقروء',
    'notifications.justNow': 'للتو',
    'notifications.minutesAgo': 'منذ {minutes} دقيقة',
    'notifications.hoursAgo': 'منذ {hours} ساعة',
    'notifications.daysAgo': 'منذ {days} يوم',
    'notifications.filter.all': 'الكل',
    'notifications.filter.unread': 'غير مقروء',
    'notifications.filter.messages': 'الرسائل',
    'notifications.filter.applications': 'الطلبات',
    'notifications.filter.matches': 'التطابقات',
    'notifications.noUnread.title': 'لا شيء جديد!',
    'notifications.noUnread.desc': 'لا توجد إشعارات غير مقروءة في الوقت الحالي',
    'notifications.noNotifications.title': 'لا توجد إشعارات',
    'notifications.noNotifications.desc': 'ستظهر الإشعارات هنا عند استلامها',
    'notifications.showing': 'عرض {count} من {total}',
    'notifications.type.message': 'رسالة',
    'notifications.type.application': 'طلب',
    'notifications.type.match': 'تطابق',
    'notifications.type.system': 'النظام',
    
    // Activity Feed
    'activity.title': 'النشاط المباشر',
    'activity.live': 'مباشر',
    'activity.viewAll': 'عرض الكل',
    'activity.noActivity': 'لا يوجد نشاط حديث',
    'activity.new': 'جديد',
    'activity.justNow': 'للتو',
    'activity.minutesAgo': 'منذ {minutes} دقيقة',
    'activity.hoursAgo': 'منذ {hours} ساعة',
    'activity.daysAgo': 'منذ {days} يوم',
    'activity.userType.volunteer': 'متطوع',
    'activity.userType.organization': 'منظمة',
    'activity.lastUpdated': 'آخر تحديث',
    'activity.refresh': 'تحديث',

    // Common
    'common.or': 'أو',
    'common.and': 'و',
    'common.of': 'من',
    'common.more': 'المزيد',
    'common.next': 'التالي',
    'common.close': 'إغلاق',
    'common.save': 'حفظ',
    'common.cancel': 'إلغاء',
    'common.confirm': 'تأكيد',
    'common.delete': 'حذف',
    'common.edit': 'تعديل',
    'common.view': 'عرض',
    'common.back': 'رجوع',
    
    // Analytics
    'analytics.title': 'لوحة التحليلات',
    'analytics.pageTitle': 'لوحة التحليلات',
    'analytics.pageSubtitle': 'رؤى شاملة حول أداء المنصة ومشاركة المستخدمين',
    'analytics.subtitle.admin': 'رؤى شاملة للمنصة ومقاييس الأداء',
    'analytics.subtitle.organization': 'تتبع فرص التطوع والطلبات الخاصة بك',
    'analytics.subtitle.volunteer': 'راقب رحلة التطوع والتأثير الخاص بك',
    'analytics.export': 'تصدير البيانات',
    'analytics.demo.volunteer': 'عرض المتطوع',
    'analytics.demo.organization': 'عرض المنظمة',
    'analytics.demo.admin': 'عرض المدير',
    
    // Analytics Time Range
    'analytics.timeRange.7d': '7 أيام',
    'analytics.timeRange.30d': '30 يوم',
    'analytics.timeRange.90d': '90 يوم',
    'analytics.timeRange.1y': 'سنة واحدة',
    
    // Analytics Tabs
    'analytics.tabs.overview': 'نظرة عامة',
    'analytics.tabs.growth': 'النمو',
    'analytics.tabs.engagement': 'المشاركة',
    'analytics.tabs.performance': 'الأداء',
    
    // Analytics Metrics
    'analytics.metrics.totalVolunteers': 'إجمالي المتطوعين',
    'analytics.metrics.totalOrganizations': 'إجمالي المنظمات',
    'analytics.metrics.totalOpportunities': 'إجمالي الفرص',
    'analytics.metrics.totalMatches': 'إجمالي المطابقات',
    'analytics.metrics.newVolunteersMonth': 'متطوعون جدد هذا الشهر',
    'analytics.metrics.newOpportunitiesMonth': 'فرص جديدة هذا الشهر',
    'analytics.metrics.growthRate': 'معدل النمو',
    'analytics.metrics.messagesSent': 'الرسائل المرسلة',
    'analytics.metrics.profileViews': 'مشاهدات الملف الشخصي',
    'analytics.metrics.searchesPerformed': 'عمليات البحث المنجزة',
    'analytics.metrics.applicationsSubmitted': 'الطلبات المقدمة',
    'analytics.metrics.applicationSuccessRate': 'معدل نجاح الطلبات',
    'analytics.metrics.averageMatchScore': 'متوسط نقاط المطابقة',
    'analytics.metrics.responseTime': 'وقت الاستجابة',
    'analytics.metrics.retentionRate': 'معدل الاحتفاظ',
    
    // Analytics Charts
    'analytics.charts.topCities': 'أهم المدن',
    'analytics.charts.popularCauses': 'القضايا الشائعة',
    'analytics.charts.growthTrend': 'اتجاه النمو',
    'analytics.charts.activityByHour': 'النشاط حسب الساعة',
    'analytics.charts.activityByHour.desc': 'ساعات الذروة (تنسيق 24 ساعة)',
    
    // Analytics Legend
    'analytics.legend.volunteers': 'المتطوعون',
    'analytics.legend.organizations': 'المنظمات',
    
    // Analytics Performance
    'analytics.performance.satisfactionScore': 'نقاط رضا المستخدمين',
    'analytics.performance.satisfactionScore.desc': 'بناءً على تعليقات وتقييمات المستخدمين',
    'analytics.performance.systemHealth': 'صحة النظام',
    'analytics.performance.uptime': 'وقت التشغيل',
    'analytics.performance.apiResponse': 'وقت استجابة API',
    'analytics.performance.errorRate': 'معدل الأخطاء',
    
    // Admin Console
    'admin.title': 'وحدة التحكم الإدارية',
    'admin.subtitle': 'أدوات إدارة ومراقبة المنصة الشاملة',
    'admin.auth.title': 'مطلوب وصول المدير',
    'admin.auth.subtitle': 'أدخل رمز المدير للوصول إلى وحدة التحكم',
    'admin.auth.placeholder': 'أدخل رمز المدير...',
    'admin.auth.submit': 'دخول وحدة التحكم',
    'admin.auth.demo': 'رمز التجربة',
    
    // Admin Tabs
    'admin.tabs.overview': 'نظرة عامة',
    'admin.tabs.users': 'المستخدمون',
    'admin.tabs.reports': 'التقارير',
    'admin.tabs.content': 'المحتوى',
    'admin.tabs.system': 'النظام',
    
    // Admin Stats
    'admin.stats.totalUsers': 'إجمالي المستخدمين',
    'admin.stats.pendingReports': 'التقارير المعلقة',
    'admin.stats.suspendedUsers': 'المستخدمون المعلقون',
    'admin.stats.systemUptime': 'وقت تشغيل النظام',
    
    // Admin Activity & Alerts
    'admin.recentActivity': 'النشاط الأخير',
    'admin.systemAlerts': 'تنبيهات النظام',
    
    // Admin Users
    'admin.searchUsers': 'البحث في المستخدمين...',
    'admin.userDetails': 'تفاصيل المستخدم',
    'admin.exportLogs': 'تصدير السجلات',
    
    // Admin Filters
    'admin.filters.all': 'الكل',
    'admin.filters.volunteers': 'المتطوعون',
    'admin.filters.organizations': 'المنظمات',
    
    // Admin Table Headers
    'admin.table.name': 'الاسم',
    'admin.table.type': 'النوع',
    'admin.table.status': 'الحالة',
    'admin.table.joinDate': 'تاريخ الانضمام',
    'admin.table.reports': 'التقارير',
    'admin.table.actions': 'الإجراءات',
    
    // Admin User Types
    'admin.userType.volunteer': 'متطوع',
    'admin.userType.organization': 'منظمة',
    
    // Admin Status
    'admin.status.active': 'نشط',
    'admin.status.suspended': 'معلق',
    'admin.status.pending': 'في الانتظار',
    'admin.status.online': 'متصل',
    
    // Admin Actions
    'admin.actions.view': 'عرض',
    'admin.actions.suspend': 'تعليق',
    'admin.actions.review': 'مراجعة',
    'admin.actions.resolve': 'حل',
    'admin.actions.dismiss': 'رفض',
    
    // Admin Reports
    'admin.priority.high': 'عالي',
    'admin.priority.medium': 'متوسط',
    'admin.priority.low': 'منخفض',
    'admin.priority.critical': 'حرج',
    
    'admin.reportType.user': 'مستخدم',
    'admin.reportType.opportunity': 'فرصة',
    'admin.reportType.message': 'رسالة',
    
    // Admin System
    'admin.system.maintenance': 'وضع الصيانة',
    'admin.system.monitoring': 'مراقبة النظام',
    'admin.system.enableMaintenance': 'تفعيل وضع الصيانة',
    'admin.system.clearCache': 'مسح ذاكرة التخزين المؤقت',
    'admin.system.backupDatabase': 'نسخ احتياطي لقاعدة البيانات',
    'admin.system.serverStatus': 'حالة الخادم',
    'admin.system.databaseStatus': 'حالة قاعدة البيانات',
    'admin.system.queueStatus': 'حالة قائمة الانتظار',
    
    // Demo Seed Data
    'demo.seedData.title': 'مولد بيانات العرض التوضيحي',
    'demo.seedData.description': 'إنشاء بيانات عرض توضيحي شاملة لعرض ميزات سراج الإصدار الثاني',
    'demo.seedData.generate': 'إنشاء بيانات العرض',
    'demo.seedData.loading': 'جاري الإنشاء...',
    'demo.seedData.clear': 'مسح البيانات',
    'demo.seedData.loaded': 'تم تحميل بيانات العرض في',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

interface LanguageProviderProps {
  children: React.ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>('en');
  const [mounted, setMounted] = useState(false);

  const direction: Direction = language === 'ar' ? 'rtl' : 'ltr';

  useEffect(() => {
    setMounted(true);
    
    // Check localStorage first
    const savedLanguage = localStorage.getItem('seraaj-language') as Language;
    if (savedLanguage && ['en', 'ar'].includes(savedLanguage)) {
      setLanguageState(savedLanguage);
    } else {
      // Detect from browser language
      const browserLang = navigator.language.toLowerCase();
      if (browserLang.startsWith('ar')) {
        setLanguageState('ar');
      }
    }
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    
    // Set direction
    root.dir = direction;
    
    // Set lang attribute
    root.lang = language;
    
    // Add RTL class for CSS
    if (direction === 'rtl') {
      root.classList.add('rtl');
    } else {
      root.classList.remove('rtl');
    }
    
    localStorage.setItem('seraaj-language', language);
  }, [language, direction, mounted]);

  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
  };

  const toggleLanguage = () => {
    setLanguageState(prev => prev === 'en' ? 'ar' : 'en');
  };

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return null;
  }

  return (
    <LanguageContext.Provider value={{ language, direction, toggleLanguage, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};