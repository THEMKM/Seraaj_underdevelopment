"use client";

import React, { useEffect } from 'react';
import { clsx } from 'clsx';
import { PxButton } from './PxButton';

interface PxModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showCloseButton?: boolean;
}

export const PxModal: React.FC<PxModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-ink/50 backdrop-blur-sm animate-px-fade-in"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div 
        className={clsx(
          'relative clip-px border-px border-ink bg-white shadow-px-glow animate-px-fade-in',
          'max-h-[90vh] overflow-y-auto',
          {
            'w-full max-w-sm': size === 'sm',
            'w-full max-w-md': size === 'md', 
            'w-full max-w-2xl': size === 'lg',
            'w-full max-w-4xl': size === 'xl',
          }
        )}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-px-2 border-b-2 border-ink bg-primary">
            {title && (
              <h2 className="font-pixel text-ink text-lg">{title}</h2>
            )}
            {showCloseButton && (
              <PxButton
                variant="secondary"
                size="sm"
                onClick={onClose}
                className="ml-auto"
              >
                ✕
              </PxButton>
            )}
          </div>
        )}
        
        {/* Content */}
        <div className="p-px-2">
          {children}
        </div>
      </div>
    </div>
  );
};