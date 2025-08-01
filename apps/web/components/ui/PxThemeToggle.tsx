"use client";

import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { PxButton } from './PxButton';

export const PxThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <PxButton
      variant="secondary"
      size="sm"
      onClick={toggleTheme}
      className="relative overflow-hidden"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <span className="relative z-10">
        {theme === 'light' ? '🌙' : '☀️'}
      </span>
    </PxButton>
  );
};