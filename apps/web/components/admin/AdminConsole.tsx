"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxCard, PxButton, PxBadge, PxInput, PxModal } from '../ui';

export interface User {
  id: string;
  name: string;
  email: string;
  type: 'volunteer' | 'organization';
  status: 'active' | 'suspended' | 'pending';
  joinDate: string;
  lastActive: string;
  applications?: number;
  opportunities?: number;
  reportCount: number;
}

export interface Report {
  id: string;
  type: 'user' | 'opportunity' | 'message';
  reportedId: string;
  reportedBy: string;
  reason: string;
  description: string;
  status: 'pending' | 'reviewing' | 'resolved' | 'dismissed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

export interface SystemAlert {
  id: string;
  type: 'performance' | 'security' | 'database' | 'api';
  severity: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

interface AdminConsoleProps {
  className?: string;
}

export const AdminConsole: React.FC<AdminConsoleProps> = ({ className }) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'reports' | 'content' | 'system'>('overview');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data
  const mockUsers: User[] = [
    {
      id: 'u1',
      name: 'Sarah Ahmed',
      email: 'sarah@example.com',
      type: 'volunteer',
      status: 'active',
      joinDate: '2024-01-15',
      lastActive: '2024-01-27',
      applications: 12,
      reportCount: 0
    },
    {
      id: 'u2',
      name: 'Hope Foundation',
      email: 'info@hopefoundation.org',
      type: 'organization',
      status: 'active',
      joinDate: '2023-12-10',
      lastActive: '2024-01-26',
      opportunities: 8,
      reportCount: 1
    },
    {
      id: 'u3',
      name: 'Ahmad Hassan',
      email: 'ahmad@test.com',
      type: 'volunteer',
      status: 'suspended',
      joinDate: '2024-01-20',
      lastActive: '2024-01-25',
      applications: 3,
      reportCount: 3
    }
  ];

  const mockReports: Report[] = [
    {
      id: 'r1',
      type: 'user',
      reportedId: 'u3',
      reportedBy: 'u1',
      reason: 'Inappropriate behavior',
      description: 'User sent inappropriate messages during interview',
      status: 'pending',
      priority: 'high',
      timestamp: '2024-01-27T10:30:00Z'
    },
    {
      id: 'r2',
      type: 'opportunity',
      reportedId: 'opp1',
      reportedBy: 'u4',
      reason: 'Misleading information',
      description: 'Job description does not match actual volunteer work',
      status: 'reviewing',
      priority: 'medium',
      timestamp: '2024-01-26T15:45:00Z'
    }
  ];

  const mockAlerts: SystemAlert[] = [
    {
      id: 'a1',
      type: 'performance',
      severity: 'warning',
      title: 'High API Response Time',
      message: 'Average response time exceeded 2 seconds in the last hour',
      timestamp: '2024-01-27T11:15:00Z',
      resolved: false
    },
    {
      id: 'a2',
      type: 'security',
      severity: 'critical',
      title: 'Multiple Failed Login Attempts',
      message: '15 failed login attempts from IP 192.168.1.100',
      timestamp: '2024-01-27T09:30:00Z',
      resolved: true
    }
  ];

  const tabs = [
    { key: 'overview', label: t('admin.tabs.overview'), icon: '📊' },
    { key: 'users', label: t('admin.tabs.users'), icon: '👥' },
    { key: 'reports', label: t('admin.tabs.reports'), icon: '🚨' },
    { key: 'content', label: t('admin.tabs.content'), icon: '📝' },
    { key: 'system', label: t('admin.tabs.system'), icon: '⚙️' }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'error';
      case 'pending': return 'warning';
      default: return 'secondary';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'secondary';
    }
  };

  const handleUserAction = (userId: string, action: string) => {
    // Process admin action for user
    // Implement user actions based on action type
    switch (action) {
      case 'activate':
        setNotifications(prev => [...prev, { type: 'success', message: `User ${userId} activated successfully` }]);
        break;
      case 'deactivate':
        setNotifications(prev => [...prev, { type: 'info', message: `User ${userId} deactivated` }]);
        break;
      case 'delete':
        setNotifications(prev => [...prev, { type: 'warning', message: `User ${userId} marked for deletion` }]);
        break;
      default:
        setNotifications(prev => [...prev, { type: 'info', message: `Action ${action} performed on user ${userId}` }]);
    }
  };

  const handleReportAction = (reportId: string, action: string) => {
    // Process report action
    // Implement report actions based on action type
    switch (action) {
      case 'resolve':
        setNotifications(prev => [...prev, { type: 'success', message: `Report ${reportId} resolved` }]);
        break;
      case 'investigate':
        setNotifications(prev => [...prev, { type: 'info', message: `Investigation started for report ${reportId}` }]);
        break;
      case 'dismiss':
        setNotifications(prev => [...prev, { type: 'warning', message: `Report ${reportId} dismissed` }]);
        break;
      default:
        setNotifications(prev => [...prev, { type: 'info', message: `Action ${action} performed on report ${reportId}` }]);
    }
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Key Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <PxCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-500 dark:bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
            <div>
              <h3 className="text-2xl font-pixel text-ink dark:text-white">2,847</h3>
              <p className="text-sm text-ink dark:text-gray-400">{t('admin.stats.totalUsers')}</p>
            </div>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-red-500 dark:bg-red-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🚨</span>
            </div>
            <div>
              <h3 className="text-2xl font-pixel text-ink dark:text-white">{mockReports.filter(r => r.status === 'pending').length}</h3>
              <p className="text-sm text-ink dark:text-gray-400">{t('admin.stats.pendingReports')}</p>
            </div>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-500 dark:bg-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏸️</span>
            </div>
            <div>
              <h3 className="text-2xl font-pixel text-ink dark:text-white">{mockUsers.filter(u => u.status === 'suspended').length}</h3>
              <p className="text-sm text-ink dark:text-gray-400">{t('admin.stats.suspendedUsers')}</p>
            </div>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-500 dark:bg-green-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
            <div>
              <h3 className="text-2xl font-pixel text-ink dark:text-white">99.9%</h3>
              <p className="text-sm text-ink dark:text-gray-400">{t('admin.stats.systemUptime')}</p>
            </div>
          </div>
        </PxCard>
      </div>

      {/* Recent Activity & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('admin.recentActivity')}
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-dark-border rounded-lg">
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">👤</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-pixel text-ink dark:text-white">New user registered</p>
                <p className="text-xs text-ink dark:text-gray-400">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-dark-border rounded-lg">
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">🚨</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-pixel text-ink dark:text-white">Report submitted</p>
                <p className="text-xs text-ink dark:text-gray-400">15 minutes ago</p>
              </div>
            </div>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('admin.systemAlerts')}
          </h3>
          <div className="space-y-3">
            {mockAlerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-dark-border rounded-lg">
                <PxBadge variant={getSeverityColor(alert.severity) as any} size="sm">
                  {alert.severity.toUpperCase()}
                </PxBadge>
                <div className="flex-1">
                  <p className="text-sm font-pixel text-ink dark:text-white">{alert.title}</p>
                  <p className="text-xs text-ink dark:text-gray-400">{alert.message}</p>
                </div>
              </div>
            ))}
          </div>
        </PxCard>
      </div>
    </div>
  );

  const renderUsersTab = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <PxInput
            type="text"
            placeholder={t('admin.searchUsers')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />
        </div>
        <div className="flex gap-2">
          <PxButton variant="secondary" size="sm">
            {t('admin.filters.all')}
          </PxButton>
          <PxButton variant="secondary" size="sm">
            {t('admin.filters.volunteers')}
          </PxButton>
          <PxButton variant="secondary" size="sm">
            {t('admin.filters.organizations')}
          </PxButton>
        </div>
      </div>

      {/* Users Table */}
      <PxCard className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-ink/10 dark:border-dark-border">
              <tr>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.name')}</th>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.type')}</th>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.status')}</th>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.joinDate')}</th>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.reports')}</th>
                <th className="text-left py-3 font-pixel text-ink dark:text-white">{t('admin.table.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {mockUsers.map((user) => (
                <tr key={user.id} className="border-b border-ink/5 dark:border-dark-border/50">
                  <td className="py-4">
                    <div>
                      <p className="font-pixel text-sm text-ink dark:text-white">{user.name}</p>
                      <p className="text-xs text-ink dark:text-gray-400">{user.email}</p>
                    </div>
                  </td>
                  <td className="py-4">
                    <PxBadge variant={user.type === 'volunteer' ? 'info' : 'success'} size="sm">
                      {t(`admin.userType.${user.type}`)}
                    </PxBadge>
                  </td>
                  <td className="py-4">
                    <PxBadge variant={getStatusColor(user.status) as any} size="sm">
                      {t(`admin.status.${user.status}`)}
                    </PxBadge>
                  </td>
                  <td className="py-4 text-sm text-ink dark:text-gray-400">
                    {new Date(user.joinDate).toLocaleDateString()}
                  </td>
                  <td className="py-4">
                    <span className={`text-sm font-pixel ${user.reportCount > 0 ? 'text-red-600 dark:text-red-400' : 'text-ink dark:text-gray-400'}`}>
                      {user.reportCount}
                    </span>
                  </td>
                  <td className="py-4">
                    <div className="flex gap-2">
                      <PxButton
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedUser(user);
                          setShowUserModal(true);
                        }}
                      >
                        {t('admin.actions.view')}
                      </PxButton>
                      {user.status !== 'suspended' && (
                        <PxButton
                          variant="error"
                          size="sm"
                          onClick={() => handleUserAction(user.id, 'suspend')}
                        >
                          {t('admin.actions.suspend')}
                        </PxButton>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </PxCard>
    </div>
  );

  const renderReportsTab = () => (
    <div className="space-y-6">
      {/* Reports List */}
      <div className="space-y-4">
        {mockReports.map((report) => (
          <PxCard key={report.id} className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-start gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <PxBadge variant={report.priority === 'high' ? 'error' : 'warning'} size="sm">
                    {t(`admin.priority.${report.priority}`)}
                  </PxBadge>
                  <PxBadge variant="secondary" size="sm">
                    {t(`admin.reportType.${report.type}`)}
                  </PxBadge>
                  <span className="text-xs text-ink dark:text-gray-400">
                    {new Date(report.timestamp).toLocaleString()}
                  </span>
                </div>
                <h4 className="font-pixel text-ink dark:text-white mb-2">{report.reason}</h4>
                <p className="text-sm text-ink dark:text-gray-400 mb-3">{report.description}</p>
                <p className="text-xs text-ink dark:text-gray-400">
                  Reported by: {report.reportedBy} • Target: {report.reportedId}
                </p>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <PxButton variant="primary" size="sm" onClick={() => handleReportAction(report.id, 'review')}>
                  {t('admin.actions.review')}
                </PxButton>
                <PxButton variant="success" size="sm" onClick={() => handleReportAction(report.id, 'resolve')}>
                  {t('admin.actions.resolve')}
                </PxButton>
                <PxButton variant="secondary" size="sm" onClick={() => handleReportAction(report.id, 'dismiss')}>
                  {t('admin.actions.dismiss')}
                </PxButton>
              </div>
            </div>
          </PxCard>
        ))}
      </div>
    </div>
  );

  const renderSystemTab = () => (
    <div className="space-y-6">
      {/* System Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('admin.system.maintenance')}
          </h3>
          <div className="space-y-3">
            <PxButton variant="warning" className="w-full">
              {t('admin.system.enableMaintenance')}
            </PxButton>
            <PxButton variant="secondary" className="w-full">
              {t('admin.system.clearCache')}
            </PxButton>
            <PxButton variant="secondary" className="w-full">
              {t('admin.system.backupDatabase')}
            </PxButton>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('admin.system.monitoring')}
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-ink dark:text-gray-400">{t('admin.system.serverStatus')}</span>
              <PxBadge variant="success" size="sm">ONLINE</PxBadge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-ink dark:text-gray-400">{t('admin.system.databaseStatus')}</span>
              <PxBadge variant="success" size="sm">HEALTHY</PxBadge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-ink dark:text-gray-400">{t('admin.system.queueStatus')}</span>
              <PxBadge variant="warning" size="sm">BUSY</PxBadge>
            </div>
          </div>
        </PxCard>
      </div>

      {/* System Alerts */}
      <PxCard className="p-6">
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('admin.systemAlerts')}
        </h3>
        <div className="space-y-3">
          {mockAlerts.map((alert) => (
            <div key={alert.id} className={`p-4 rounded-lg border ${alert.resolved ? 'bg-gray-50 dark:bg-dark-border/50' : 'bg-red-50 dark:bg-red-900/20'}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <PxBadge variant={getSeverityColor(alert.severity) as any} size="sm">
                      {alert.severity.toUpperCase()}
                    </PxBadge>
                    <span className="text-xs text-ink dark:text-gray-400">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <h4 className="font-pixel text-sm text-ink dark:text-white mb-1">{alert.title}</h4>
                  <p className="text-sm text-ink dark:text-gray-400">{alert.message}</p>
                </div>
                {!alert.resolved && (
                  <PxButton variant="success" size="sm">
                    {t('admin.actions.resolve')}
                  </PxButton>
                )}
              </div>
            </div>
          ))}
        </div>
      </PxCard>
    </div>
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
            {t('admin.title')}
          </h1>
          <p className="text-ink dark:text-gray-400">
            {t('admin.subtitle')}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <PxBadge variant="success" animated>
            {t('admin.status.online')}
          </PxBadge>
          <PxButton variant="secondary" size="sm">
            {t('admin.exportLogs')}
          </PxButton>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 flex-wrap">
        {tabs.map(tab => (
          <PxButton
            key={tab.key}
            variant={activeTab === tab.key ? 'primary' : 'secondary'}
            onClick={() => setActiveTab(tab.key as any)}
            className="flex items-center gap-2"
          >
            <span>{tab.icon}</span>
            {tab.label}
          </PxButton>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'users' && renderUsersTab()}
      {activeTab === 'reports' && renderReportsTab()}
      {activeTab === 'system' && renderSystemTab()}

      {/* User Details Modal */}
      {showUserModal && selectedUser && (
        <PxModal
          isOpen={showUserModal}
          onClose={() => setShowUserModal(false)}
          title={t('admin.userDetails')}
        >
          <div className="space-y-4">
            <div>
              <h3 className="font-pixel text-ink dark:text-white mb-2">{selectedUser.name}</h3>
              <p className="text-sm text-ink dark:text-gray-400 mb-4">{selectedUser.email}</p>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-ink dark:text-gray-400">{t('admin.table.type')}:</span>
                  <PxBadge variant={selectedUser.type === 'volunteer' ? 'info' : 'success'} size="sm" className="ml-2">
                    {t(`admin.userType.${selectedUser.type}`)}
                  </PxBadge>
                </div>
                <div>
                  <span className="text-ink dark:text-gray-400">{t('admin.table.status')}:</span>
                  <PxBadge variant={getStatusColor(selectedUser.status) as any} size="sm" className="ml-2">
                    {t(`admin.status.${selectedUser.status}`)}
                  </PxBadge>
                </div>
                <div>
                  <span className="text-ink dark:text-gray-400">{t('admin.table.joinDate')}:</span>
                  <span className="ml-2 text-ink dark:text-white">{new Date(selectedUser.joinDate).toLocaleDateString()}</span>
                </div>
                <div>
                  <span className="text-ink dark:text-gray-400">{t('admin.table.reports')}:</span>
                  <span className="ml-2 text-ink dark:text-white">{selectedUser.reportCount}</span>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 pt-4">
              <PxButton variant="primary" onClick={() => setShowUserModal(false)}>
                {t('common.close')}
              </PxButton>
              {selectedUser.status !== 'suspended' && (
                <PxButton variant="error" onClick={() => handleUserAction(selectedUser.id, 'suspend')}>
                  {t('admin.actions.suspend')}
                </PxButton>
              )}
            </div>
          </div>
        </PxModal>
      )}
    </div>
  );
};