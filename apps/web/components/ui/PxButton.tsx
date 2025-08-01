import React from 'react';
import { clsx } from 'clsx';

interface PxButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const PxButton: React.FC<PxButtonProps> = ({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}) => {
  return (
    <button
      className={clsx(
        'clip-px shadow-px border-px font-pixel transition-all duration-200',
        'hover:translate-x-1 hover:translate-y-1 hover:shadow-none',
        'active:translate-x-1 active:translate-y-1 active:shadow-none',
        'focus:outline-none focus:ring-2 focus:ring-pixel-coral focus:ring-dotted',
        {
          'bg-primary border-ink text-ink dark:bg-neon-cyan dark:border-white dark:text-dark-bg': variant === 'primary',
          'bg-white border-ink text-ink dark:bg-dark-surface dark:border-dark-border dark:text-white': variant === 'secondary',
          'bg-pixel-coral border-ink text-white dark:bg-neon-pink dark:border-white': variant === 'danger',
          'px-px py-1 text-xs': size === 'sm',
          'px-px-2 py-2 text-sm': size === 'md',
          'px-px-3 py-3 text-base': size === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};