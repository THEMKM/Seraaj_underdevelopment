"use client";

import { AppLayout } from "../../components/layout/AppLayout";
import { AnalyticsDashboard } from "../../components/analytics/AnalyticsDashboard";
import { useState } from "react";
import { PxButton } from "../../components/ui";
import { useLanguage } from "../../contexts/LanguageContext";

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const [userType, setUserType] = useState<'volunteer' | 'organization' | 'admin'>('admin');

  return (
    <AppLayout userType={userType}>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div>
              <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
                {t('analytics.pageTitle')}
              </h1>
              <p className="text-ink dark:text-gray-300">
                {t('analytics.pageSubtitle')}
              </p>
            </div>
            
            {/* User Type Switcher for Demo */}
            <div className="flex gap-2">
              <PxButton
                variant={userType === 'volunteer' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setUserType('volunteer')}
              >
                👥 {t('analytics.demo.volunteer')}
              </PxButton>
              <PxButton
                variant={userType === 'organization' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setUserType('organization')}
              >
                🏢 {t('analytics.demo.organization')}
              </PxButton>
              <PxButton
                variant={userType === 'admin' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setUserType('admin')}
              >
                ⚡ {t('analytics.demo.admin')}
              </PxButton>
            </div>
          </div>
        </div>

        <AnalyticsDashboard userType={userType} />
      </div>
    </AppLayout>
  );
}