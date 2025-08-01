"use client";

import React from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxButton } from './PxButton';

interface PxLanguageToggleProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const PxLanguageToggle: React.FC<PxLanguageToggleProps> = ({ 
  className, 
  size = 'sm' 
}) => {
  const { language, toggleLanguage } = useLanguage();

  return (
    <PxButton
      variant="secondary"
      size={size}
      onClick={toggleLanguage}
      className={className}
      title={language === 'en' ? 'Switch to Arabic' : 'Switch to English'}
    >
      {language === 'en' ? 'العربية' : 'English'}
    </PxButton>
  );
};