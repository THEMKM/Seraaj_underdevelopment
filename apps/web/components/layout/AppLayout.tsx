"use client";

import React from 'react';
import { clsx } from 'clsx';
import { MobileNav, DesktopSidebar } from './MobileNav';
import { PxThemeToggle, PxLanguageToggle } from '../ui';
import { PxButton } from '../ui/PxButton';
import { NotificationBell, NotificationCenter } from '../notifications/NotificationCenter';
import { useState } from 'react';

interface AppLayoutProps {
  children: React.ReactNode;
  userType?: 'volunteer' | 'org' | 'admin';
  showSidebar?: boolean;
  className?: string;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  userType = 'volunteer',
  showSidebar = true,
  className,
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  return (
    <div className="min-h-screen bg-white dark:bg-dark-bg">
      {/* Desktop Sidebar */}
      {showSidebar && <DesktopSidebar userType={userType} />}
      
      {/* Main Content Area */}
      <div className={clsx(
        'flex flex-col min-h-screen',
        {
          'md:ml-64': showSidebar,
        }
      )}>
        {/* Top Bar (Mobile & Desktop) */}
        <header className="sticky top-0 z-20 bg-primary dark:bg-deep-indigo border-b-2 border-ink dark:border-dark-border">
          <div className="flex items-center justify-between px-4 py-3">
            {/* Mobile Logo / Back Button */}
            <div className="md:hidden">
              <h1 className="text-lg font-pixel text-ink dark:text-neon-cyan">SERAAJ</h1>
            </div>
            
            {/* Desktop Page Title */}
            <div className="hidden md:block">
              <h2 className="text-lg font-pixel text-ink dark:text-white">
                {userType === 'volunteer' ? 'VOLUNTEER DASHBOARD' : 
                 userType === 'org' ? 'ORGANIZATION PORTAL' : 
                 'ADMIN CONSOLE'}
              </h2>
            </div>
            
            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <NotificationBell onClick={() => setShowNotifications(true)} />
              <PxLanguageToggle />
              <PxThemeToggle />
              <PxButton variant="secondary" size="sm">
                SETTINGS
              </PxButton>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className={clsx(
          'flex-1 pb-20 md:pb-4', // Extra bottom padding for mobile nav
          className
        )}>
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <MobileNav userType={userType} />
      
      {/* Notification Center */}
      <NotificationCenter 
        isOpen={showNotifications} 
        onClose={() => setShowNotifications(false)} 
      />
    </div>
  );
};