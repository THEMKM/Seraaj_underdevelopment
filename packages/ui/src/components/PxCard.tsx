import React from 'react';
import { clsx } from 'clsx';

interface PxCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'highlighted';
}

export const PxCard: React.FC<PxCardProps> = ({
  children,
  className,
  variant = 'default',
}) => {
  return (
    <div
      className={clsx(
        'clip-px shadow-px border-px',
        {
          'bg-white border-ink': variant === 'default',
          'bg-primary border-ink': variant === 'highlighted',
        },
        className
      )}
    >
      {children}
    </div>
  );
};