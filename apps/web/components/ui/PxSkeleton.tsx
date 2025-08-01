import React from 'react';
import { clsx } from 'clsx';

interface PxSkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export const PxSkeleton: React.FC<PxSkeletonProps> = ({
  className,
  variant = 'rectangular',
  width,
  height,
  lines = 1,
}) => {
  const baseClasses = clsx(
    'animate-px-shimmer shimmer bg-gray-200',
    'bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200',
    {
      'clip-px': variant === 'rectangular',
      'rounded-full': variant === 'circular',
      'h-4': variant === 'text' && !height,
      'h-16': variant === 'rectangular' && !height,
      'w-16': variant === 'circular' && !width,
      'w-full': variant === 'text' && !width,
    },
    className
  );

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  if (variant === 'text' && lines > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={clsx(baseClasses, {
              'w-3/4': index === lines - 1, // Last line shorter
            })}
            style={style}
          />
        ))}
      </div>
    );
  }

  return <div className={baseClasses} style={style} />;
};

// Skeleton patterns for common UI elements
export const PxSkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx('clip-px border-px border-gray-200 bg-white p-6 space-y-4', className)}>
    <PxSkeleton variant="rectangular" height={40} width="60%" />
    <PxSkeleton variant="text" lines={3} />
    <div className="flex gap-2">
      <PxSkeleton variant="rectangular" height={32} width={80} />
      <PxSkeleton variant="rectangular" height={32} width={100} />
    </div>
  </div>
);

export const PxSkeletonProfile: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx('flex items-center gap-4', className)}>
    <PxSkeleton variant="circular" width={48} height={48} />
    <div className="flex-1 space-y-2">
      <PxSkeleton variant="text" width="40%" height={16} />
      <PxSkeleton variant="text" width="60%" height={14} />
    </div>
  </div>
);