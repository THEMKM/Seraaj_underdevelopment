import React from 'react';
import { clsx } from 'clsx';

interface PxProgressProps {
  value: number;
  max?: number;
  className?: string;
  showLabel?: boolean;
}

export const PxProgress: React.FC<PxProgressProps> = ({
  value,
  max = 100,
  className,
  showLabel = false,
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={clsx('space-y-1', className)}>
      {showLabel && (
        <div className="flex justify-between text-sm font-pixel text-ink">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="clip-px border-px border-ink bg-white h-6 overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};