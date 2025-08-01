"use client";

import { AppLayout } from "../../components/layout/AppLayout";
import { AdminConsole } from "../../components/admin/AdminConsole";
import { useLanguage } from "../../contexts/LanguageContext";
import { useState, useEffect } from "react";
import { PxCard, PxButton } from "../../components/ui";

export default function AdminPage() {
  const { t } = useLanguage();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [authCode, setAuthCode] = useState('');

  // Simple auth check for demo purposes
  useEffect(() => {
    const checkAuth = () => {
      // In a real app, this would check actual admin permissions
      const adminAuth = localStorage.getItem('admin_auth');
      if (adminAuth === 'authorized') {
        setIsAuthorized(true);
      }
    };
    checkAuth();
  }, []);

  const handleAuthSubmit = () => {
    // Demo auth code
    if (authCode === 'admin2024' || authCode === 'seraaj_admin') {
      localStorage.setItem('admin_auth', 'authorized');
      setIsAuthorized(true);
    } else {
      alert('Invalid admin code. Try: admin2024');
    }
  };

  if (!isAuthorized) {
    return (
      <AppLayout userType="volunteer">
        <div className="max-w-md mx-auto px-4 py-12">
          <PxCard className="p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
                <span className="text-3xl">🔐</span>
              </div>
              <h1 className="text-2xl font-pixel text-ink dark:text-white mb-2">
                {t('admin.auth.title')}
              </h1>
              <p className="text-ink dark:text-gray-400 text-sm">
                {t('admin.auth.subtitle')}
              </p>
            </div>
            
            <div className="space-y-4">
              <input
                type="password"
                placeholder={t('admin.auth.placeholder')}
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                className="w-full px-4 py-3 border border-ink/20 dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-pixel text-sm"
                onKeyPress={(e) => e.key === 'Enter' && handleAuthSubmit()}
              />
              
              <PxButton 
                variant="primary" 
                onClick={handleAuthSubmit}
                className="w-full"
              >
                {t('admin.auth.submit')}
              </PxButton>
              
              <div className="text-center pt-4">
                <p className="text-xs text-ink dark:text-gray-400">
                  {t('admin.auth.demo')}: <code className="bg-gray-100 dark:bg-dark-border px-2 py-1 rounded font-mono">admin2024</code>
                </p>
              </div>
            </div>
          </PxCard>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout userType="admin">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <AdminConsole />
      </div>
    </AppLayout>
  );
}