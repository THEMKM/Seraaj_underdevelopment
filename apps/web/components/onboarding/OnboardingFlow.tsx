"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxButton, PxCard, PxProgress, PxChip } from '../ui';
import { WelcomeStep } from './steps/WelcomeStep';
import { UserTypeStep } from './steps/UserTypeStep';
import { ProfileStep } from './steps/ProfileStep';
import { PreferencesStep } from './steps/PreferencesStep';
import { CompletionStep } from './steps/CompletionStep';

export type UserType = 'volunteer' | 'organization';

export interface OnboardingData {
  userType: UserType | null;
  name: string;
  email: string;
  location: string;
  bio: string;
  interests: string[];
  skills: string[];
  causes: string[];
  availability: string;
  organizationName?: string;
  organizationType?: string;
  organizationSize?: string;
}

interface OnboardingFlowProps {
  onComplete: (data: OnboardingData) => void;
  onSkip?: () => void;
}

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete, onSkip }) => {
  const { t } = useLanguage();
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    userType: null,
    name: '',
    email: '',
    location: '',
    bio: '',
    interests: [],
    skills: [],
    causes: [],
    availability: '',
  });

  const steps = [
    { component: WelcomeStep, title: t('onboarding.welcome.title') },
    { component: UserTypeStep, title: t('onboarding.userType.title') },
    { component: ProfileStep, title: t('onboarding.profile.title') },
    { component: PreferencesStep, title: t('onboarding.preferences.title') },
    { component: CompletionStep, title: t('onboarding.completion.title') },
  ];

  const progress = ((currentStep + 1) / steps.length) * 100;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(data);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const updateData = (updates: Partial<OnboardingData>) => {
    setData(prev => ({ ...prev, ...updates }));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: return true; // Welcome step
      case 1: return data.userType !== null; // User type step
      case 2: return data.name && data.email && data.location; // Profile step
      case 3: return data.causes.length > 0; // Preferences step
      case 4: return true; // Completion step
      default: return false;
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-primary dark:bg-dark-bg flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-pixel text-ink dark:text-white">
              {t('onboarding.step')} {currentStep + 1} {t('common.of')} {steps.length}
            </span>
            <span className="text-sm font-pixel text-ink dark:text-white">
              {Math.round(progress)}%
            </span>
          </div>
          <PxProgress value={progress} className="h-3" />
        </div>

        {/* Step Content */}
        <PxCard className="p-8 mb-6 bg-white dark:bg-dark-surface">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-pixel text-ink dark:text-white mb-2">
              {steps[currentStep].title}
            </h2>
          </div>

          <CurrentStepComponent
            data={data}
            updateData={updateData}
            onNext={handleNext}
          />
        </PxCard>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <div className="flex gap-3">
            {currentStep > 0 && (
              <PxButton
                variant="secondary"
                onClick={handleBack}
              >
                {t('common.back')}
              </PxButton>
            )}
            {onSkip && currentStep === 0 && (
              <PxButton
                variant="secondary"
                onClick={onSkip}
              >
                {t('onboarding.skip')}
              </PxButton>
            )}
          </div>

          <PxButton
            variant="primary"
            onClick={handleNext}
            disabled={!canProceed()}
            className="hover:shadow-px-glow"
          >
            {currentStep === steps.length - 1
              ? t('onboarding.complete')
              : t('common.next')
            }
          </PxButton>
        </div>
      </div>
    </div>
  );
};