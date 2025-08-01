"use client";

import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { OnboardingData } from '../OnboardingFlow';

interface WelcomeStepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
}

export const WelcomeStep: React.FC<WelcomeStepProps> = ({ onNext }) => {
  const { t } = useLanguage();

  return (
    <div className="text-center space-y-6">
      {/* Logo/Icon */}
      <div className="mb-8">
        <div className="w-24 h-24 mx-auto mb-4 bg-pixel-coral dark:bg-neon-pink rounded-lg flex items-center justify-center">
          <span className="text-3xl font-pixel text-white">S</span>
        </div>
        <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
          {t('onboarding.welcome.header')}
        </h1>
        <p className="text-lg text-ink dark:text-gray-300">
          {t('onboarding.welcome.subtitle')}
        </p>
      </div>

      {/* Features Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="text-center p-4">
          <div className="w-12 h-12 mx-auto mb-3 bg-electric-teal dark:bg-neon-cyan rounded-lg flex items-center justify-center">
            <span className="text-xl">🎯</span>
          </div>
          <h3 className="font-pixel text-sm text-ink dark:text-white mb-2">
            {t('onboarding.welcome.feature1.title')}
          </h3>
          <p className="text-xs text-ink dark:text-gray-400">
            {t('onboarding.welcome.feature1.desc')}
          </p>
        </div>
        
        <div className="text-center p-4">
          <div className="w-12 h-12 mx-auto mb-3 bg-pixel-lavender dark:bg-neon-pink rounded-lg flex items-center justify-center">
            <span className="text-xl">⚡</span>
          </div>
          <h3 className="font-pixel text-sm text-ink dark:text-white mb-2">
            {t('onboarding.welcome.feature2.title')}
          </h3>
          <p className="text-xs text-ink dark:text-gray-400">
            {t('onboarding.welcome.feature2.desc')}
          </p>
        </div>
        
        <div className="text-center p-4">
          <div className="w-12 h-12 mx-auto mb-3 bg-pixel-mint dark:bg-neon-green rounded-lg flex items-center justify-center">
            <span className="text-xl">💫</span>
          </div>
          <h3 className="font-pixel text-sm text-ink dark:text-white mb-2">
            {t('onboarding.welcome.feature3.title')}
          </h3>
          <p className="text-xs text-ink dark:text-gray-400">
            {t('onboarding.welcome.feature3.desc')}
          </p>
        </div>
      </div>

      {/* Call to Action */}
      <div className="space-y-4">
        <p className="text-ink dark:text-gray-300">
          {t('onboarding.welcome.cta')}
        </p>
        <div className="flex justify-center">
          <button
            onClick={onNext}
            className="px-8 py-3 bg-pixel-coral dark:bg-neon-pink text-white font-pixel text-sm rounded-lg hover:shadow-px-glow transition-all duration-300 transform hover:scale-105"
          >
            {t('onboarding.welcome.start')}
          </button>
        </div>
      </div>
    </div>
  );
};