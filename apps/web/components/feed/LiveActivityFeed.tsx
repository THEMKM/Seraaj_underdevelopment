"use client";

import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { PxCard, PxBadge, PxButton } from '../ui';

export interface ActivityItem {
  id: string;
  type: 'application' | 'match' | 'message' | 'profile_view' | 'opportunity_posted' | 'volunteer_joined';
  userId: string;
  userName: string;
  userAvatar?: string;
  userType: 'volunteer' | 'organization';
  title: string;
  description: string;
  timestamp: string;
  relatedId?: string;
  relatedTitle?: string;
  isNew: boolean;
}

interface LiveActivityFeedProps {
  className?: string;
  maxItems?: number;
}

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({ 
  className, 
  maxItems = 10 
}) => {
  const { t } = useLanguage();
  const { isConnected } = useWebSocket();
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Mock activity data
  const mockActivities: ActivityItem[] = [
    {
      id: 'act-1',
      type: 'match',
      userId: 'user-123',
      userName: 'Sarah Ahmed',
      userType: 'volunteer',
      title: 'New opportunity match',
      description: 'Found 3 new volunteer opportunities matching your profile',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
      relatedId: 'opp-456',
      relatedTitle: 'English Tutor for Refugee Children',
      isNew: true
    },
    {
      id: 'act-2',
      type: 'application',
      userId: 'org-789',
      userName: 'Hope Foundation',
      userType: 'organization',
      title: 'Application received',
      description: 'New volunteer application for English tutoring program',
      timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(), // 12 minutes ago
      relatedId: 'app-101',
      isNew: true
    },
    {
      id: 'act-3',
      type: 'opportunity_posted',
      userId: 'org-234',
      userName: 'Green Lebanon Initiative',
      userType: 'organization',
      title: 'New opportunity posted',
      description: 'Environmental Awareness Campaign Coordinator',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(), // 25 minutes ago
      relatedId: 'opp-789',
      relatedTitle: 'Environmental Awareness Campaign Coordinator',
      isNew: false
    },
    {
      id: 'act-4',
      type: 'volunteer_joined',
      userId: 'user-456',
      userName: 'Ahmed Hassan',
      userType: 'volunteer',
      title: 'Volunteer joined',
      description: 'Started volunteering with Community Health Program',
      timestamp: new Date(Date.now() - 35 * 60 * 1000).toISOString(), // 35 minutes ago
      relatedId: 'opp-567',
      relatedTitle: 'Community Health Program',
      isNew: false
    },
    {
      id: 'act-5',
      type: 'profile_view',
      userId: 'org-345',
      userName: 'Cairo Medical Aid',
      userType: 'organization',
      title: 'Profile viewed',
      description: 'Viewed your volunteer profile',
      timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 minutes ago
      isNew: false
    },
    {
      id: 'act-6',
      type: 'message',
      userId: 'org-678',
      userName: 'Tech for Good MENA',
      userType: 'organization',
      title: 'New message',
      description: 'Sent you a message about the Web Developer position',
      timestamp: new Date(Date.now() - 65 * 60 * 1000).toISOString(), // 1 hour ago
      relatedId: 'conv-234',
      isNew: false
    }
  ];

  useEffect(() => {
    // Simulate loading
    const loadActivities = () => {
      setIsLoading(true);
      setTimeout(() => {
        setActivities(mockActivities.slice(0, maxItems));
        setIsLoading(false);
      }, 1000);
    };

    loadActivities();

    // Simulate real-time updates
    const interval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance of new activity
        const newActivity: ActivityItem = {
          id: `act-${Date.now()}`,
          type: ['match', 'application', 'message', 'profile_view'][Math.floor(Math.random() * 4)] as ActivityItem['type'],
          userId: `user-${Math.floor(Math.random() * 1000)}`,
          userName: ['Sarah Ahmed', 'Hope Foundation', 'Ahmad Ali', 'Green Initiative'][Math.floor(Math.random() * 4)],
          userType: Math.random() > 0.5 ? 'volunteer' : 'organization',
          title: 'New activity',
          description: 'Something interesting happened!',
          timestamp: new Date().toISOString(),
          isNew: true
        };

        setActivities(prev => [newActivity, ...prev.slice(0, maxItems - 1)]);

        // Mark as not new after a few seconds
        setTimeout(() => {
          setActivities(prev => 
            prev.map(act => 
              act.id === newActivity.id ? { ...act, isNew: false } : act
            )
          );
        }, 5000);
      }
    }, 15000); // Every 15 seconds

    return () => clearInterval(interval);
  }, [maxItems]);

  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'match': return '🎯';
      case 'application': return '📋';
      case 'message': return '💬';
      case 'profile_view': return '👁️';
      case 'opportunity_posted': return '📢';
      case 'volunteer_joined': return '🤝';
      default: return '📌';
    }
  };

  const getActivityColor = (type: ActivityItem['type']) => {
    switch (type) {
      case 'match': return 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400';
      case 'application': return 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400';
      case 'message': return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400';
      case 'profile_view': return 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400';
      case 'opportunity_posted': return 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400';
      case 'volunteer_joined': return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400';
      default: return 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return t('activity.justNow');
    if (diffMinutes < 60) return t('activity.minutesAgo', { minutes: diffMinutes });
    if (diffMinutes < 1440) return t('activity.hoursAgo', { hours: Math.floor(diffMinutes / 60) });
    return t('activity.daysAgo', { days: Math.floor(diffMinutes / 1440) });
  };

  const handleActivityClick = (activity: ActivityItem) => {
    // Navigate to related content
    if (activity.relatedId) {
      switch (activity.type) {
        case 'message':
          window.location.href = `/messages?conversation=${activity.relatedId}`;
          break;
        case 'application':
          window.location.href = `/applications/${activity.relatedId}`;
          break;
        case 'match':
        case 'opportunity_posted':
          window.location.href = `/opportunities/${activity.relatedId}`;
          break;
        case 'profile_view':
          window.location.href = `/profile/${activity.userId}`;
          break;
      }
    }
  };

  if (isLoading) {
    return (
      <PxCard className={`p-6 ${className}`}>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-pixel text-ink dark:text-white">
              {t('activity.title')}
            </h3>
            <div className="w-4 h-4 bg-gray-300 dark:bg-gray-600 rounded animate-pulse"></div>
          </div>
          
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      </PxCard>
    );
  }

  return (
    <PxCard className={`p-6 ${className}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="font-pixel text-ink dark:text-white">
            {t('activity.title')}
          </h3>
          <div className="flex items-center gap-2">
            {isConnected && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600 dark:text-green-400 font-pixel">
                  {t('activity.live')}
                </span>
              </div>
            )}
            <PxButton variant="secondary" size="sm">
              {t('activity.viewAll')}
            </PxButton>
          </div>
        </div>

        {/* Activities List */}
        {activities.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 mx-auto mb-3 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
            <p className="text-sm text-ink dark:text-gray-400">
              {t('activity.noActivity')}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {activities.map((activity) => (
              <div
                key={activity.id}
                className={`p-3 rounded-lg border transition-all duration-300 cursor-pointer hover:shadow-px ${
                  activity.isNew 
                    ? 'bg-primary/5 dark:bg-neon-cyan/5 border-primary/20 dark:border-neon-cyan/20 animate-px-fade-in' 
                    : 'bg-white dark:bg-dark-surface border-ink/10 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-border/50'
                }`}
                onClick={() => handleActivityClick(activity)}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${getActivityColor(activity.type)}`}>
                    <span className="text-sm">
                      {getActivityIcon(activity.type)}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-1">
                      <h4 className="font-pixel text-sm text-ink dark:text-white">
                        {activity.title}
                      </h4>
                      <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                        {activity.isNew && (
                          <PxBadge variant="error" size="sm">
                            {t('activity.new')}
                          </PxBadge>
                        )}
                        <span className="text-xs text-ink dark:text-gray-400">
                          {formatTime(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-ink dark:text-gray-400 mb-1">
                      {activity.description}
                    </p>
                    
                    <div className="flex items-center gap-2">
                      {/* User Info */}
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-electric-teal dark:bg-neon-pink rounded flex items-center justify-center">
                          <span className="text-xs font-pixel text-white">
                            {activity.userName.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <span className="text-xs text-ink dark:text-gray-400">
                          {activity.userName}
                        </span>
                      </div>
                      
                      {/* User Type Badge */}
                      <PxBadge 
                        variant={activity.userType === 'volunteer' ? 'info' : 'success'} 
                        size="sm"
                      >
                        {t(`activity.userType.${activity.userType}`)}
                      </PxBadge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        {activities.length > 0 && (
          <div className="pt-3 border-t border-ink/10 dark:border-dark-border">
            <div className="flex items-center justify-between">
              <span className="text-xs text-ink dark:text-gray-400">
                {t('activity.lastUpdated')}: {formatTime(activities[0]?.timestamp || new Date().toISOString())}
              </span>
              <PxButton variant="secondary" size="sm">
                {t('activity.refresh')}
              </PxButton>
            </div>
          </div>
        )}
      </div>
    </PxCard>
  );
};