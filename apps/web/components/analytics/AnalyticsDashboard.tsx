"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxCard, PxButton, PxBadge, PxProgress } from '../ui';

export interface AnalyticsData {
  // Overview metrics
  totalVolunteers: number;
  totalOrganizations: number;
  totalOpportunities: number;
  totalMatches: number;
  
  // Growth metrics
  newVolunteersThisMonth: number;
  newOpportunitiesThisMonth: number;
  applicationSuccessRate: number;
  averageMatchScore: number;
  
  // Activity metrics
  messagesSent: number;
  profileViews: number;
  searchesPerformed: number;
  opportunitiesApplied: number;
  
  // Performance metrics
  responseTime: number;
  satisfactionScore: number;
  retentionRate: number;
  
  // Geographic data
  topCities: Array<{ name: string; count: number; percentage: number }>;
  
  // Cause distribution
  topCauses: Array<{ name: string; count: number; percentage: number }>;
  
  // Time-based data
  activityByHour: Array<{ hour: number; activity: number }>;
  growthByMonth: Array<{ month: string; volunteers: number; organizations: number }>;
}

interface AnalyticsDashboardProps {
  userType: 'volunteer' | 'organization' | 'admin';
  timeRange?: '7d' | '30d' | '90d' | '1y';
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  userType,
  timeRange = '30d'
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'overview' | 'growth' | 'engagement' | 'performance'>('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);

  // Mock analytics data
  const mockData: AnalyticsData = {
    totalVolunteers: 2847,
    totalOrganizations: 156,
    totalOpportunities: 423,
    totalMatches: 1892,
    newVolunteersThisMonth: 234,
    newOpportunitiesThisMonth: 45,
    applicationSuccessRate: 68,
    averageMatchScore: 82,
    messagesSent: 5643,
    profileViews: 12890,
    searchesPerformed: 8765,
    opportunitiesApplied: 967,
    responseTime: 2.3,
    satisfactionScore: 4.6,
    retentionRate: 87,
    topCities: [
      { name: 'Amman', count: 1245, percentage: 43.7 },
      { name: 'Beirut', count: 678, percentage: 23.8 },
      { name: 'Cairo', count: 456, percentage: 16.0 },
      { name: 'Dubai', count: 289, percentage: 10.2 },
      { name: 'Riyadh', count: 179, percentage: 6.3 }
    ],
    topCauses: [
      { name: 'Education', count: 156, percentage: 36.9 },
      { name: 'Health', count: 89, percentage: 21.0 },
      { name: 'Environment', count: 67, percentage: 15.8 },
      { name: 'Youth Development', count: 45, percentage: 10.6 },
      { name: 'Refugees', count: 66, percentage: 15.6 }
    ],
    activityByHour: [
      { hour: 0, activity: 12 }, { hour: 1, activity: 8 }, { hour: 2, activity: 5 },
      { hour: 3, activity: 3 }, { hour: 4, activity: 2 }, { hour: 5, activity: 4 },
      { hour: 6, activity: 15 }, { hour: 7, activity: 28 }, { hour: 8, activity: 45 },
      { hour: 9, activity: 67 }, { hour: 10, activity: 89 }, { hour: 11, activity: 95 },
      { hour: 12, activity: 78 }, { hour: 13, activity: 82 }, { hour: 14, activity: 76 },
      { hour: 15, activity: 91 }, { hour: 16, activity: 88 }, { hour: 17, activity: 93 },
      { hour: 18, activity: 87 }, { hour: 19, activity: 75 }, { hour: 20, activity: 65 },
      { hour: 21, activity: 48 }, { hour: 22, activity: 35 }, { hour: 23, activity: 22 }
    ],
    growthByMonth: [
      { month: 'Oct', volunteers: 2534, organizations: 142 },
      { month: 'Nov', volunteers: 2678, organizations: 148 },
      { month: 'Dec', volunteers: 2791, organizations: 153 },
      { month: 'Jan', volunteers: 2847, organizations: 156 }
    ]
  };

  const timeRangeOptions = [
    { key: '7d', label: t('analytics.timeRange.7d') },
    { key: '30d', label: t('analytics.timeRange.30d') },
    { key: '90d', label: t('analytics.timeRange.90d') },
    { key: '1y', label: t('analytics.timeRange.1y') }
  ];

  const tabs = [
    { key: 'overview', label: t('analytics.tabs.overview'), icon: '📊' },
    { key: 'growth', label: t('analytics.tabs.growth'), icon: '📈' },
    { key: 'engagement', label: t('analytics.tabs.engagement'), icon: '👥' },
    { key: 'performance', label: t('analytics.tabs.performance'), icon: '⚡' }
  ];

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: string;
    color?: string;
  }> = ({ title, value, change, icon, color = 'bg-primary dark:bg-neon-cyan' }) => (
    <PxCard className="p-6 hover:shadow-px-glow transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center`}>
          <span className="text-2xl">{icon}</span>
        </div>
        {change !== undefined && (
          <PxBadge variant={change >= 0 ? 'success' : 'error'} size="sm">
            {change >= 0 ? '↗' : '↘'} {Math.abs(change)}%
          </PxBadge>
        )}
      </div>
      <h3 className="text-2xl font-pixel text-ink dark:text-white mb-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </h3>
      <p className="text-sm text-ink dark:text-gray-400">{title}</p>
    </PxCard>
  );

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title={t('analytics.metrics.totalVolunteers')}
          value={mockData.totalVolunteers}
          change={12}
          icon="👥"
          color="bg-blue-500 dark:bg-blue-600"
        />
        <MetricCard
          title={t('analytics.metrics.totalOrganizations')}
          value={mockData.totalOrganizations}
          change={8}
          icon="🏢"
          color="bg-green-500 dark:bg-green-600"
        />
        <MetricCard
          title={t('analytics.metrics.totalOpportunities')}
          value={mockData.totalOpportunities}
          change={15}
          icon="🎯"
          color="bg-purple-500 dark:bg-purple-600"
        />
        <MetricCard
          title={t('analytics.metrics.totalMatches')}
          value={mockData.totalMatches}
          change={23}
          icon="✨"
          color="bg-orange-500 dark:bg-orange-600"
        />
      </div>

      {/* Geographic Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('analytics.charts.topCities')}
          </h3>
          <div className="space-y-3">
            {mockData.topCities.map((city, index) => (
              <div key={city.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-primary dark:bg-neon-cyan rounded flex items-center justify-center">
                    <span className="text-xs font-pixel text-ink dark:text-dark-bg">
                      {index + 1}
                    </span>
                  </div>
                  <span className="font-pixel text-sm text-ink dark:text-white">
                    {city.name}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24">
                    <PxProgress value={city.percentage} className="h-2" />
                  </div>
                  <span className="text-sm text-ink dark:text-gray-400 w-12 text-right">
                    {city.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </PxCard>

        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('analytics.charts.popularCauses')}
          </h3>
          <div className="space-y-3">
            {mockData.topCauses.map((cause, index) => (
              <div key={cause.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-electric-teal dark:bg-neon-pink rounded flex items-center justify-center">
                    <span className="text-xs font-pixel text-white">
                      {index + 1}
                    </span>
                  </div>
                  <span className="font-pixel text-sm text-ink dark:text-white">
                    {cause.name}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24">
                    <PxProgress value={cause.percentage} className="h-2" />
                  </div>
                  <span className="text-sm text-ink dark:text-gray-400 w-12 text-right">
                    {cause.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </PxCard>
      </div>
    </div>
  );

  const renderGrowthTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title={t('analytics.metrics.newVolunteersMonth')}
          value={mockData.newVolunteersThisMonth}
          change={18}
          icon="📈"
          color="bg-green-500 dark:bg-green-600"
        />
        <MetricCard
          title={t('analytics.metrics.newOpportunitiesMonth')}
          value={mockData.newOpportunitiesThisMonth}
          change={12}
          icon="🚀"
          color="bg-blue-500 dark:bg-blue-600"
        />
        <MetricCard
          title={t('analytics.metrics.growthRate')}
          value="12.5%"
          change={3}
          icon="⬆️"
          color="bg-purple-500 dark:bg-purple-600"
        />
      </div>

      {/* Growth Chart Simulation */}
      <PxCard className="p-6">
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('analytics.charts.growthTrend')}
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {mockData.growthByMonth.map((month, index) => (
            <div key={month.month} className="text-center">
              <div className="mb-2">
                <div className="relative h-32 bg-gray-100 dark:bg-dark-border rounded-lg overflow-hidden">
                  <div 
                    className="absolute bottom-0 w-full bg-primary dark:bg-neon-cyan transition-all duration-500"
                    style={{ height: `${(month.volunteers / 3000) * 100}%` }}
                  ></div>
                  <div 
                    className="absolute bottom-0 w-full bg-electric-teal dark:bg-neon-pink opacity-70 transition-all duration-500"
                    style={{ height: `${(month.organizations / 200) * 100}%` }}
                  ></div>
                </div>
              </div>
              <span className="text-sm font-pixel text-ink dark:text-white">
                {month.month}
              </span>
            </div>
          ))}
        </div>
        <div className="flex justify-center gap-4 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary dark:bg-neon-cyan rounded"></div>
            <span className="text-xs text-ink dark:text-gray-400">
              {t('analytics.legend.volunteers')}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-electric-teal dark:bg-neon-pink rounded"></div>
            <span className="text-xs text-ink dark:text-gray-400">
              {t('analytics.legend.organizations')}
            </span>
          </div>
        </div>
      </PxCard>
    </div>
  );

  const renderEngagementTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title={t('analytics.metrics.messagesSent')}
          value={mockData.messagesSent}
          change={25}
          icon="💬"
          color="bg-blue-500 dark:bg-blue-600"
        />
        <MetricCard
          title={t('analytics.metrics.profileViews')}
          value={mockData.profileViews}
          change={15}
          icon="👁️"
          color="bg-orange-500 dark:bg-orange-600"
        />
        <MetricCard
          title={t('analytics.metrics.searchesPerformed')}
          value={mockData.searchesPerformed}
          change={8}
          icon="🔍"
          color="bg-purple-500 dark:bg-purple-600"
        />
        <MetricCard
          title={t('analytics.metrics.applicationsSubmitted')}
          value={mockData.opportunitiesApplied}
          change={32}
          icon="📋"
          color="bg-green-500 dark:bg-green-600"
        />
      </div>

      {/* Activity Heatmap */}
      <PxCard className="p-6">
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('analytics.charts.activityByHour')}
        </h3>
        <div className="grid grid-cols-12 gap-1">
          {mockData.activityByHour.map((hour) => (
            <div key={hour.hour} className="text-center">
              <div 
                className="w-full mb-1 bg-primary dark:bg-neon-cyan rounded transition-all duration-300 hover:shadow-px-glow"
                style={{ 
                  height: `${Math.max(20, (hour.activity / 100) * 80)}px`,
                  opacity: Math.max(0.3, hour.activity / 100)
                }}
              ></div>
              <span className="text-xs text-ink dark:text-gray-400">
                {hour.hour.toString().padStart(2, '0')}
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-ink dark:text-gray-400 mt-2 text-center">
          {t('analytics.charts.activityByHour.desc')}
        </p>
      </PxCard>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title={t('analytics.metrics.applicationSuccessRate')}
          value={`${mockData.applicationSuccessRate}%`}
          change={5}
          icon="✅"
          color="bg-green-500 dark:bg-green-600"
        />
        <MetricCard
          title={t('analytics.metrics.averageMatchScore')}
          value={`${mockData.averageMatchScore}%`}
          change={2}
          icon="🎯"
          color="bg-purple-500 dark:bg-purple-600"
        />
        <MetricCard
          title={t('analytics.metrics.responseTime')}
          value={`${mockData.responseTime}s`}
          change={-8}
          icon="⚡"
          color="bg-orange-500 dark:bg-orange-600"
        />
        <MetricCard
          title={t('analytics.metrics.retentionRate')}
          value={`${mockData.retentionRate}%`}
          change={4}
          icon="🔄"
          color="bg-blue-500 dark:bg-blue-600"
        />
      </div>

      {/* Performance Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('analytics.performance.satisfactionScore')}
          </h3>
          <div className="text-center">
            <div className="text-4xl font-pixel text-primary dark:text-neon-cyan mb-2">
              {mockData.satisfactionScore}/5.0
            </div>
            <div className="flex justify-center gap-1 mb-4">
              {[1, 2, 3, 4, 5].map((star) => (
                <span 
                  key={star}
                  className={`text-2xl ${star <= Math.floor(mockData.satisfactionScore) ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                >
                  ⭐
                </span>
              ))}
            </div>
            <p className="text-sm text-ink dark:text-gray-400">
              {t('analytics.performance.satisfactionScore.desc')}
            </p>
          </div>
        </PxCard>

        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('analytics.performance.systemHealth')}
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink dark:text-gray-400">
                {t('analytics.performance.uptime')}
              </span>
              <div className="flex items-center gap-2">
                <PxProgress value={99.9} className="w-20 h-2" />
                <span className="text-sm font-pixel text-ink dark:text-white">99.9%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink dark:text-gray-400">
                {t('analytics.performance.apiResponse')}
              </span>
              <div className="flex items-center gap-2">
                <PxProgress value={85} className="w-20 h-2" />
                <span className="text-sm font-pixel text-ink dark:text-white">
                  {mockData.responseTime}s
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink dark:text-gray-400">
                {t('analytics.performance.errorRate')}
              </span>
              <div className="flex items-center gap-2">
                <PxProgress value={2} className="w-20 h-2" />
                <span className="text-sm font-pixel text-ink dark:text-white">0.1%</span>
              </div>
            </div>
          </div>
        </PxCard>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
            {t('analytics.title')}
          </h1>
          <p className="text-ink dark:text-gray-400">
            {userType === 'admin' 
              ? t('analytics.subtitle.admin')
              : userType === 'organization'
              ? t('analytics.subtitle.organization')
              : t('analytics.subtitle.volunteer')
            }
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Time Range Selector */}
          <div className="flex gap-1">
            {timeRangeOptions.map(option => (
              <PxButton
                key={option.key}
                variant={selectedTimeRange === option.key ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setSelectedTimeRange(option.key as any)}
              >
                {option.label}
              </PxButton>
            ))}
          </div>
          
          <PxButton variant="secondary" size="sm">
            📊 {t('analytics.export')}
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
      {activeTab === 'growth' && renderGrowthTab()}
      {activeTab === 'engagement' && renderEngagementTab()}
      {activeTab === 'performance' && renderPerformanceTab()}
    </div>
  );
};