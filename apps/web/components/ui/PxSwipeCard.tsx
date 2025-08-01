"use client";

import React, { useState, useRef } from 'react';
import { clsx } from 'clsx';
import { PxCard } from './PxCard';

interface PxSwipeCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  className?: string;
  swipeThreshold?: number;
}

export const PxSwipeCard: React.FC<PxSwipeCardProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  className,
  swipeThreshold = 100,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleDragStart = (e: React.PointerEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
    setDragOffset({ x: 0, y: 0 });
  };

  const handleDragMove = (e: React.PointerEvent) => {
    if (!isDragging) return;

    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;
    setDragOffset({ x: deltaX, y: deltaY });
  };

  const handleDragEnd = () => {
    if (!isDragging) return;

    const { x, y } = dragOffset;
    
    // Determine swipe direction
    if (Math.abs(x) > Math.abs(y)) {
      // Horizontal swipe
      if (x > swipeThreshold && onSwipeRight) {
        onSwipeRight();
      } else if (x < -swipeThreshold && onSwipeLeft) {
        onSwipeLeft();
      }
    } else {
      // Vertical swipe
      if (y < -swipeThreshold && onSwipeUp) {
        onSwipeUp();
      }
    }

    // Reset
    setIsDragging(false);
    setDragOffset({ x: 0, y: 0 });
  };

  const getSwipeIndicator = () => {
    const { x, y } = dragOffset;
    const absX = Math.abs(x);
    const absY = Math.abs(y);

    if (absX > absY) {
      if (x > swipeThreshold * 0.5) {
        return { type: 'right', opacity: Math.min(absX / swipeThreshold, 1) };
      } else if (x < -swipeThreshold * 0.5) {
        return { type: 'left', opacity: Math.min(absX / swipeThreshold, 1) };
      }
    } else if (y < -swipeThreshold * 0.5) {
      return { type: 'up', opacity: Math.min(absY / swipeThreshold, 1) };
    }

    return null;
  };

  const swipeIndicator = getSwipeIndicator();
  const rotation = isDragging ? dragOffset.x * 0.1 : 0;

  return (
    <div
      ref={cardRef}
      className={clsx('relative touch-none select-none cursor-grab', className)}
      style={{
        transform: `translate(${dragOffset.x}px, ${dragOffset.y}px) rotate(${rotation}deg)`,
        transition: isDragging ? 'none' : 'transform 0.3s ease-out',
      }}
      onPointerDown={handleDragStart}
      onPointerMove={handleDragMove}
      onPointerUp={handleDragEnd}
      onPointerLeave={handleDragEnd}
    >
      <PxCard className="relative overflow-hidden">
        {children}
        
        {/* Swipe Indicators */}
        {swipeIndicator && (
          <div 
            className="absolute inset-0 flex items-center justify-center"
            style={{ opacity: swipeIndicator.opacity }}
          >
            <div
              className={clsx(
                'clip-px border-px font-pixel text-2xl p-4',
                {
                  'bg-electric-teal border-ink text-ink': swipeIndicator.type === 'right',
                  'bg-pixel-coral border-ink text-white': swipeIndicator.type === 'left',
                  'bg-primary border-ink text-ink': swipeIndicator.type === 'up',
                }
              )}
            >
              {swipeIndicator.type === 'right' && '✓'}
              {swipeIndicator.type === 'left' && '✕'}
              {swipeIndicator.type === 'up' && '★'}
            </div>
          </div>
        )}
      </PxCard>

      {/* Swipe Instructions */}
      <div className="absolute -bottom-8 left-0 right-0 text-center">
        <div className="flex justify-center gap-4 text-xs font-pixel text-gray-500">
          {onSwipeLeft && <span>← PASS</span>}
          {onSwipeRight && <span>LIKE →</span>}
          {onSwipeUp && <span>↑ SUPER LIKE</span>}
        </div>
      </div>
    </div>
  );
};