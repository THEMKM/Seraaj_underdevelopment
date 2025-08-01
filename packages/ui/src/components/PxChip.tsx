import React from 'react';
import { clsx } from 'clsx';

interface PxChipProps {
  children: React.ReactNode;
  variant?: 'default' | 'selected';
  size?: 'sm' | 'md';
  onClick?: () => void;
  className?: string;
}

export const PxChip: React.FC<PxChipProps> = ({
  children,
  variant = 'default',
  size = 'md',
  onClick,
  className,
}) => {
  const isClickable = !!onClick;

  return (
    <span
      className={clsx(
        'inline-block clip-px border-px font-body',
        {
          'bg-white border-ink text-ink': variant === 'default',
          'bg-primary border-ink text-ink': variant === 'selected',
          'px-2 py-1 text-xs': size === 'sm',
          'px-px py-2 text-sm': size === 'md',
          'cursor-pointer hover:bg-primary transition-colors': isClickable && variant === 'default',
          'cursor-pointer hover:bg-pixel-mint transition-colors': isClickable && variant === 'selected',
        },
        className
      )}
      onClick={onClick}
    >
      {children}
    </span>
  );
};