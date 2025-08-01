import React from 'react';
import { clsx } from 'clsx';

interface PxInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const PxInput: React.FC<PxInputProps> = ({
  label,
  error,
  className,
  ...props
}) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-pixel text-ink">
          {label}
        </label>
      )}
      <input
        className={clsx(
          'w-full clip-px border-px bg-white border-ink font-body',
          'px-px-2 py-2 text-sm text-ink',
          'focus:outline-none focus:ring-2 focus:ring-pixel-coral focus:ring-dotted',
          'placeholder:text-gray-500',
          {
            'border-pixel-coral': error,
          },
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm font-body text-pixel-coral">{error}</p>
      )}
    </div>
  );
};