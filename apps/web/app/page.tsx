"use client";

import { PxButton, PxCard, PxThemeToggle, PxLanguageToggle } from "../components/ui";
import { HeroSearch } from "../components/landing/HeroSearch";
import { useLanguage } from "../contexts/LanguageContext";
import { useAuth } from "../contexts/AuthContext";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const { t } = useLanguage();
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg transition-colors duration-300">
      {/* Header */}
      <header className="border-b-2 border-ink dark:border-dark-border bg-primary dark:bg-deep-indigo">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-pixel text-ink dark:text-neon-cyan animate-px-glow">SERAAJ</h1>
            <nav className="flex items-center gap-4">
              <PxLanguageToggle />
              <PxThemeToggle />
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-ink dark:text-white">
                    Welcome, {user?.first_name}!
                  </span>
                  <PxButton 
                    variant="secondary" 
                    size="sm"
                    onClick={() => router.push('/feed')}
                  >
                    Dashboard
                  </PxButton>
                  <PxButton 
                    variant="outline" 
                    size="sm"
                    onClick={logout}
                  >
                    Logout
                  </PxButton>
                </>
              ) : (
                <>
                  <PxButton 
                    variant="secondary" 
                    size="sm"
                    onClick={() => router.push('/auth/login')}
                  >
                    {t('nav.login')}
                  </PxButton>
                  <PxButton 
                    variant="primary" 
                    size="sm"
                    onClick={() => router.push('/auth/register')}
                  >
                    {t('nav.signup')}
                  </PxButton>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16 animate-px-fade-in">
          <h2 className="text-4xl md:text-6xl font-pixel text-ink dark:text-white mb-8 leading-tight">
            {t('landing.title')}
          </h2>
          <p className="text-xl text-ink dark:text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
            {t('landing.subtitle')}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <PxButton variant="primary" size="lg" className="hover:shadow-px-glow">
              {t('landing.cta.volunteer')}
            </PxButton>
            <PxButton variant="secondary" size="lg">
              {t('landing.cta.org')}
            </PxButton>
          </div>
          
          {/* Hero Search */}
          <HeroSearch />
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <PxCard className="p-8 hover:shadow-px-glow transition-all duration-300 dark:bg-dark-surface dark:border-dark-border">
            <h3 className="text-xl font-pixel text-ink dark:text-electric-teal mb-4">{t('landing.feature.volunteers.title')}</h3>
            <p className="text-ink dark:text-gray-300 leading-relaxed">
              {t('landing.feature.volunteers.desc')}
            </p>
          </PxCard>

          <PxCard className="p-8 hover:shadow-px-glow transition-all duration-300 dark:bg-dark-surface dark:border-dark-border">
            <h3 className="text-xl font-pixel text-ink dark:text-electric-teal mb-4">{t('landing.feature.ngos.title')}</h3>
            <p className="text-ink dark:text-gray-300 leading-relaxed">
              {t('landing.feature.ngos.desc')}
            </p>
          </PxCard>

          <PxCard className="p-8 hover:shadow-px-glow transition-all duration-300 dark:bg-dark-surface dark:border-dark-border">
            <h3 className="text-xl font-pixel text-ink dark:text-electric-teal mb-4">{t('landing.feature.impact.title')}</h3>
            <p className="text-ink dark:text-gray-300 leading-relaxed">
              {t('landing.feature.impact.desc')}
            </p>
          </PxCard>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <PxCard variant="highlighted" className="p-12 max-w-2xl mx-auto animate-px-glow dark:bg-gradient-to-br dark:from-deep-indigo dark:to-pixel-lavender">
            <h3 className="text-2xl font-pixel text-ink dark:text-white mb-4">
              {t('landing.ready.title')}
            </h3>
            <p className="text-ink dark:text-gray-200 mb-6">
              {t('landing.ready.desc')}
            </p>
            <PxButton variant="primary" size="lg" className="hover:shadow-px-glow">
              {t('landing.ready.cta')}
            </PxButton>
          </PxCard>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-ink dark:border-dark-border bg-ink dark:bg-dark-surface text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="font-pixel text-sm">
            SERAAJ v2.0 · 8-BIT OPTIMISM
          </p>
        </div>
      </footer>
    </div>
  );
}
