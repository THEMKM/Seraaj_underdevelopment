"use client";

import React from 'react';
import { clsx } from 'clsx';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}

const volunteerNavItems: NavItem[] = [
  { label: 'FEED', href: '/feed', icon: '🎯' },
  { label: 'APPLICATIONS', href: '/applications', icon: '📝', badge: 3 },
  { label: 'MESSAGES', href: '/messages', icon: '💬', badge: 1 },
  { label: 'PROFILE', href: '/profile', icon: '👤' },
];

const orgNavItems: NavItem[] = [
  { label: 'DASHBOARD', href: '/org/dashboard', icon: '📊' },
  { label: 'OPPORTUNITIES', href: '/org/opportunities', icon: '🎯' },
  { label: 'CANDIDATES', href: '/org/candidates', icon: '👥', badge: 5 },
  { label: 'ANALYTICS', href: '/org/analytics', icon: '📈' },
];

interface MobileNavProps {
  userType?: 'volunteer' | 'org' | 'admin';
  className?: string;
}

export const MobileNav: React.FC<MobileNavProps> = ({ 
  userType = 'volunteer',
  className 
}) => {
  const pathname = usePathname();
  const navItems = userType === 'org' ? orgNavItems : volunteerNavItems;

  return (
    <nav className={clsx(
      'fixed bottom-0 left-0 right-0 z-40 md:hidden',
      'bg-white dark:bg-dark-surface border-t-2 border-ink dark:border-dark-border',
      'shadow-px-glow dark:shadow-px-dark',
      className
    )}>
      <div className="flex items-center justify-around py-2 px-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          
          return (
            <Link key={item.href} href={item.href}>
              <div className={clsx(
                'relative flex flex-col items-center px-2 py-2 min-w-0 transition-all duration-200',
                'clip-px border border-transparent',
                {
                  'bg-primary border-ink text-ink dark:bg-neon-cyan dark:text-dark-bg': isActive,
                  'text-gray-600 dark:text-gray-400 hover:text-ink dark:hover:text-white': !isActive,
                }
              )}>
                {/* Icon */}
                <div className="text-lg mb-1 relative">
                  {item.icon}
                  {/* Badge */}
                  {item.badge && item.badge > 0 && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-pixel-coral border border-ink clip-px text-white font-pixel text-xs flex items-center justify-center">
                      {item.badge > 9 ? '9+' : item.badge}
                    </div>
                  )}
                </div>
                
                {/* Label */}
                <span className="font-pixel text-xs leading-none text-center">
                  {item.label}
                </span>
              </div>
            </Link>
          );
        })}
      </div>
      
      {/* Safe area for iPhone home indicator */}
      <div className="h-safe-area-inset-bottom bg-inherit" />
    </nav>
  );
};

// Desktop Sidebar Component
interface DesktopSidebarProps {
  userType?: 'volunteer' | 'org' | 'admin';
  className?: string;
}

export const DesktopSidebar: React.FC<DesktopSidebarProps> = ({
  userType = 'volunteer',
  className
}) => {
  const pathname = usePathname();
  const navItems = userType === 'org' ? orgNavItems : volunteerNavItems;

  return (
    <aside className={clsx(
      'hidden md:flex md:flex-col w-64 h-screen',
      'bg-white dark:bg-dark-surface border-r-2 border-ink dark:border-dark-border',
      'fixed left-0 top-0 z-30',
      className
    )}>
      {/* Logo */}
      <div className="p-6 border-b-2 border-ink dark:border-dark-border bg-primary dark:bg-deep-indigo">
        <h1 className="text-xl font-pixel text-ink dark:text-neon-cyan">SERAAJ</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="space-y-2 px-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            
            return (
              <Link key={item.href} href={item.href}>
                <div className={clsx(
                  'flex items-center gap-3 px-4 py-3 transition-all duration-200',
                  'clip-px border-px',
                  {
                    'bg-primary border-ink text-ink dark:bg-neon-cyan dark:text-dark-bg shadow-px': isActive,
                    'border-transparent text-gray-600 dark:text-gray-400 hover:text-ink dark:hover:text-white hover:bg-gray-50 dark:hover:bg-dark-bg': !isActive,
                  }
                )}>
                  <span className="text-lg">{item.icon}</span>
                  <span className="font-pixel text-sm flex-1">{item.label}</span>
                  {item.badge && item.badge > 0 && (
                    <div className="w-5 h-5 bg-pixel-coral border border-ink clip-px text-white font-pixel text-xs flex items-center justify-center">
                      {item.badge > 9 ? '9+' : item.badge}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      </nav>
    </aside>
  );
};