"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useWebSocket, NotificationMessage } from '../../contexts/WebSocketContext';
import { PxButton, PxCard, PxBadge, PxModal } from '../ui';

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage();
  const { notifications, markNotificationAsRead, clearAllNotifications } = useWebSocket();
  const [filter, setFilter] = useState<'all' | 'unread' | 'message' | 'application' | 'match' | 'system'>('all');

  const getNotificationIcon = (type: NotificationMessage['type']) => {
    switch (type) {
      case 'message': return '💬';
      case 'application': return '📋';
      case 'match': return '🎯';
      case 'system': return '⚙️';
      default: return '🔔';
    }
  };

  const getNotificationColor = (type: NotificationMessage['type']) => {
    switch (type) {
      case 'message': return 'text-blue-600 dark:text-blue-400';
      case 'application': return 'text-green-600 dark:text-green-400';
      case 'match': return 'text-purple-600 dark:text-purple-400';
      case 'system': return 'text-gray-600 dark:text-gray-400';
      default: return 'text-ink dark:text-white';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 1) return t('notifications.justNow');
    if (diffMinutes < 60) return t('notifications.minutesAgo', { minutes: diffMinutes });
    if (diffMinutes < 1440) return t('notifications.hoursAgo', { hours: Math.floor(diffMinutes / 60) });
    return t('notifications.daysAgo', { days: Math.floor(diffMinutes / 1440) });
  };

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notification.read;
    return notification.type === filter;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const filterOptions = [
    { key: 'all', label: t('notifications.filter.all'), count: notifications.length },
    { key: 'unread', label: t('notifications.filter.unread'), count: unreadCount },
    { key: 'message', label: t('notifications.filter.messages'), count: notifications.filter(n => n.type === 'message').length },
    { key: 'application', label: t('notifications.filter.applications'), count: notifications.filter(n => n.type === 'application').length },
    { key: 'match', label: t('notifications.filter.matches'), count: notifications.filter(n => n.type === 'match').length },
  ];

  const handleNotificationClick = (notification: NotificationMessage) => {
    if (!notification.read) {
      markNotificationAsRead(notification.id);
    }
    
    // Navigate to the action URL if provided
    if (notification.actionUrl) {
      window.location.href = notification.actionUrl;
    }
    
    onClose();
  };

  return (
    <PxModal
      isOpen={isOpen}
      onClose={onClose}
      title={t('notifications.title')}
      size="lg"
    >
      <div className="space-y-4">
        {/* Header with Actions */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-pixel text-ink dark:text-white">
              {t('notifications.title')}
            </h3>
            <p className="text-sm text-ink dark:text-gray-400">
              {unreadCount > 0 
                ? t('notifications.unreadCount', { count: unreadCount })
                : t('notifications.allRead')
              }
            </p>
          </div>
          
          {unreadCount > 0 && (
            <PxButton
              variant="secondary"
              size="sm"
              onClick={clearAllNotifications}
            >
              {t('notifications.markAllRead')}
            </PxButton>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {filterOptions.map(option => (
            <PxButton
              key={option.key}
              variant={filter === option.key ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilter(option.key as any)}
              className="flex items-center gap-2"
            >
              {option.label}
              {option.count > 0 && (
                <span className="bg-white dark:bg-dark-bg text-ink dark:text-white text-xs px-2 py-1 rounded">
                  {option.count}
                </span>
              )}
            </PxButton>
          ))}
        </div>

        {/* Notifications List */}
        <div className="max-h-96 overflow-y-auto space-y-2">
          {filteredNotifications.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
                <span className="text-2xl">🔔</span>
              </div>
              <h4 className="font-pixel text-ink dark:text-white mb-2">
                {filter === 'unread' 
                  ? t('notifications.noUnread.title')
                  : t('notifications.noNotifications.title')
                }
              </h4>
              <p className="text-sm text-ink dark:text-gray-400">
                {filter === 'unread' 
                  ? t('notifications.noUnread.desc')
                  : t('notifications.noNotifications.desc')
                }
              </p>
            </div>
          ) : (
            filteredNotifications.map((notification) => (
              <PxCard
                key={notification.id}
                className={`p-4 cursor-pointer transition-all duration-200 hover:shadow-px ${
                  !notification.read 
                    ? 'bg-primary/5 dark:bg-neon-cyan/5 border-l-4 border-l-primary dark:border-l-neon-cyan' 
                    : 'hover:bg-gray-50 dark:hover:bg-dark-border/50'
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex items-start gap-3">
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${
                    notification.type === 'message' ? 'bg-blue-100 dark:bg-blue-900/30' :
                    notification.type === 'application' ? 'bg-green-100 dark:bg-green-900/30' :
                    notification.type === 'match' ? 'bg-purple-100 dark:bg-purple-900/30' :
                    'bg-gray-100 dark:bg-gray-800'
                  }`}>
                    <span className="text-lg">
                      {getNotificationIcon(notification.type)}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-1">
                      <h4 className={`font-pixel text-sm ${!notification.read ? 'text-ink dark:text-white' : 'text-ink dark:text-gray-300'}`}>
                        {notification.title}
                      </h4>
                      <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                        {!notification.read && (
                          <div className="w-2 h-2 bg-primary dark:bg-neon-cyan rounded-full"></div>
                        )}
                        <span className="text-xs text-ink dark:text-gray-400">
                          {formatTime(notification.timestamp)}
                        </span>
                      </div>
                    </div>
                    
                    <p className={`text-sm leading-relaxed ${!notification.read ? 'text-ink dark:text-gray-300' : 'text-ink dark:text-gray-400'}`}>
                      {notification.content}
                    </p>
                    
                    {/* Notification Type Badge */}
                    <div className="mt-2">
                      <PxBadge 
                        variant="default" 
                        size="sm"
                        className={getNotificationColor(notification.type)}
                      >
                        {t(`notifications.type.${notification.type}`)}
                      </PxBadge>
                    </div>
                  </div>
                </div>
              </PxCard>
            ))
          )}
        </div>

        {/* Footer */}
        {filteredNotifications.length > 0 && (
          <div className="flex justify-between items-center pt-4 border-t border-ink/20 dark:border-dark-border">
            <span className="text-sm text-ink dark:text-gray-400">
              {t('notifications.showing', { 
                count: filteredNotifications.length,
                total: notifications.length 
              })}
            </span>
            
            <PxButton variant="secondary" size="sm" onClick={onClose}>
              {t('common.close')}
            </PxButton>
          </div>
        )}
      </div>
    </PxModal>
  );
};

// Notification Bell Component for Header
interface NotificationBellProps {
  onClick: () => void;
  className?: string;
}

export const NotificationBell: React.FC<NotificationBellProps> = ({ onClick, className }) => {
  const { unreadCount } = useWebSocket();

  return (
    <button
      onClick={onClick}
      className={`relative p-2 text-ink dark:text-white hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-colors duration-200 ${className}`}
    >
      <span className="text-xl">🔔</span>
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-pixel px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </button>
  );
};