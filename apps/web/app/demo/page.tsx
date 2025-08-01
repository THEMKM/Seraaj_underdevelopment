"use client";

import { AppLayout } from "../../components/layout/AppLayout";
import { SeedDataLoader } from "../../components/demo/SeedDataLoader";
import { useLanguage } from "../../contexts/LanguageContext";
import { PxCard, PxButton, PxBadge } from "../../components/ui";
import { useState, useEffect } from "react";

export default function DemoPage() {
  const { t } = useLanguage();
  const [demoData, setDemoData] = useState<any>(null);

  useEffect(() => {
    // Check if demo data exists
    const existingData = localStorage.getItem('seraaj_demo_data');
    if (existingData) {
      setDemoData(JSON.parse(existingData));
    }
  }, []);

  const demoFeatures = [
    {
      title: '8-Bit Optimism Design',
      description: 'Unique pixel-perfect design system with chunky corners and retro aesthetics',
      route: '/',
      status: 'completed',
      icon: '🎨'
    },
    {
      title: 'Smart Onboarding Flow',
      description: '5-step interactive onboarding with user type selection and preferences',
      route: '/onboarding',
      status: 'completed',
      icon: '🚀'
    },
    {
      title: 'Personalized Feed',
      description: 'AI-powered opportunity matching with swipe and card view modes',
      route: '/feed',
      status: 'completed',
      icon: '📊'
    },
    {
      title: 'Advanced Search',
      description: 'Comprehensive search and filtering with saved searches',
      route: '/search',
      status: 'completed',
      icon: '🔍'
    },
    {
      title: 'Profile Management',
      description: 'Professional profiles with versioning and change tracking',
      route: '/profile',
      status: 'completed',
      icon: '👤'
    },
    {
      title: 'Real-time Messaging',
      description: 'WebSocket-powered messaging with status indicators',
      route: '/messages',
      status: 'completed',
      icon: '💬'
    },
    {
      title: 'Analytics Dashboard',
      description: 'Comprehensive analytics with multiple visualization types',
      route: '/analytics',
      status: 'completed',
      icon: '📈'
    },
    {
      title: 'Admin Console',
      description: 'Advanced admin tools for user management and system monitoring',
      route: '/admin',
      status: 'completed',
      icon: '⚙️'
    },
    {
      title: 'Arabic RTL Support',
      description: 'Full internationalization with Arabic language and RTL layout',
      route: '/',
      status: 'completed',
      icon: '🌍'
    },
    {
      title: 'Dark Mode',
      description: 'Beautiful dark theme with neon accents and smooth transitions',
      route: '/',
      status: 'completed',
      icon: '🌙'
    }
  ];

  const handleDataLoaded = (data: any) => {
    setDemoData(data);
  };

  return (
    <AppLayout userType="admin">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
            <span className="text-4xl">🎯</span>
          </div>
          <h1 className="text-4xl font-pixel text-ink dark:text-white mb-4">
            SERAAJ V2 DEMO
          </h1>
          <p className="text-xl text-ink dark:text-gray-300 mb-2">
            Two-sided volunteer marketplace for MENA nonprofits
          </p>
          <p className="text-ink dark:text-gray-400">
            Experience the complete platform with 8-bit optimism design aesthetic
          </p>
        </div>

        {/* Demo Data Generator */}
        <div className="mb-8">
          <SeedDataLoader onDataLoaded={handleDataLoaded} />
        </div>

        {/* Feature Showcase */}
        <div className="mb-8">
          <h2 className="text-2xl font-pixel text-ink dark:text-white mb-6 text-center">
            ✨ COMPLETED FEATURES
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demoFeatures.map((feature, index) => (
              <PxCard key={index} className="p-6 hover:shadow-px-glow transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
                    <span className="text-xl">{feature.icon}</span>
                  </div>
                  <PxBadge variant="success" size="sm">
                    {feature.status.toUpperCase()}
                  </PxBadge>
                </div>
                <h3 className="font-pixel text-ink dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-ink dark:text-gray-400 mb-4">
                  {feature.description}
                </p>
                <PxButton
                  variant="secondary"
                  size="sm"
                  onClick={() => window.location.href = feature.route}
                  className="w-full"
                >
                  EXPLORE →
                </PxButton>
              </PxCard>
            ))}
          </div>
        </div>

        {/* Quick Navigation */}
        <PxCard className="p-8">
          <h2 className="text-2xl font-pixel text-ink dark:text-white mb-6 text-center">
            🚀 QUICK NAVIGATION
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <PxButton
              variant="primary"
              onClick={() => window.location.href = '/'}
              className="h-16 flex flex-col items-center gap-1"
            >
              <span className="text-xl">🏠</span>
              <span className="text-xs">HOME</span>
            </PxButton>
            <PxButton
              variant="primary"
              onClick={() => window.location.href = '/feed'}
              className="h-16 flex flex-col items-center gap-1"
            >
              <span className="text-xl">📊</span>
              <span className="text-xs">FEED</span>
            </PxButton>
            <PxButton
              variant="primary"
              onClick={() => window.location.href = '/analytics'}
              className="h-16 flex flex-col items-center gap-1"
            >
              <span className="text-xl">📈</span>
              <span className="text-xs">ANALYTICS</span>
            </PxButton>
            <PxButton
              variant="primary"
              onClick={() => window.location.href = '/admin'}
              className="h-16 flex flex-col items-center gap-1"
            >
              <span className="text-xl">⚙️</span>
              <span className="text-xs">ADMIN</span>
            </PxButton>
          </div>
        </PxCard>

        {/* Demo Statistics */}
        {demoData && (
          <div className="mt-8">
            <h2 className="text-2xl font-pixel text-ink dark:text-white mb-6 text-center">
              📊 DEMO STATISTICS
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <PxCard className="p-4 text-center">
                <div className="text-3xl font-pixel text-primary dark:text-neon-cyan mb-2">
                  {demoData.organizations?.length || 0}
                </div>
                <div className="text-sm text-ink dark:text-gray-400">Organizations</div>
              </PxCard>
              <PxCard className="p-4 text-center">
                <div className="text-3xl font-pixel text-primary dark:text-neon-cyan mb-2">
                  {demoData.volunteers?.length || 0}
                </div>
                <div className="text-sm text-ink dark:text-gray-400">Volunteers</div>
              </PxCard>
              <PxCard className="p-4 text-center">
                <div className="text-3xl font-pixel text-primary dark:text-neon-cyan mb-2">
                  {demoData.opportunities?.length || 0}
                </div>
                <div className="text-sm text-ink dark:text-gray-400">Opportunities</div>
              </PxCard>
              <PxCard className="p-4 text-center">
                <div className="text-3xl font-pixel text-primary dark:text-neon-cyan mb-2">
                  {demoData.applications?.length || 0}
                </div>
                <div className="text-sm text-ink dark:text-gray-400">Applications</div>
              </PxCard>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center">
          <div className="bg-gradient-to-r from-primary via-electric-teal to-primary dark:from-neon-cyan dark:via-neon-pink dark:to-neon-cyan bg-clip-text text-transparent">
            <h3 className="text-2xl font-pixel mb-2">
              🎮 BUILT WITH 8-BIT OPTIMISM
            </h3>
          </div>
          <p className="text-ink dark:text-gray-400 text-sm">
            Next.js 14 • TypeScript • Tailwind CSS • WebSocket • i18n • Dark Mode
          </p>
        </div>
      </div>
    </AppLayout>
  );
}