"use client";

import React, { useEffect, useState } from 'react';
import { clsx } from 'clsx';

export interface ToastProps {
  id: string;
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  onRemove: (id: string) => void;
}

export const PxToast: React.FC<ToastProps> = ({
  id,
  message,
  type = 'info',
  duration = 5000,
  onRemove,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleRemove();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleRemove = () => {
    setIsVisible(false);
    setTimeout(() => onRemove(id), 300);
  };

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-electric-teal border-ink text-ink';
      case 'error':
        return 'bg-pixel-coral border-ink text-white';
      case 'warning':
        return 'bg-primary border-ink text-ink';
      case 'info':
      default:
        return 'bg-pixel-mint border-ink text-ink';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  return (
    <div
      className={clsx(
        'clip-px border-px shadow-px font-body p-4 mb-2 transition-all duration-300',
        getTypeStyles(),
        {
          'translate-x-0 opacity-100': isVisible,
          'translate-x-full opacity-0': !isVisible,
        }
      )}
    >
      <div className="flex items-center gap-3">
        <span className="font-pixel text-sm">{getIcon()}</span>
        <span className="flex-1">{message}</span>
        <button
          onClick={handleRemove}
          className="font-pixel text-xs hover:opacity-70 transition-opacity"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

// Toast Container Component
interface ToastContainerProps {
  toasts: ToastProps[];
  onRemoveToast: (id: string) => void;
}

export const PxToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  onRemoveToast,
}) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <PxToast
          key={toast.id}
          {...toast}
          onRemove={onRemoveToast}
        />
      ))}
    </div>
  );
};