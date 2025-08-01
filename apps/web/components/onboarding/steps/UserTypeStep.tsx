"use client";

import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { OnboardingData, UserType } from '../OnboardingFlow';
import { PxCard } from '../../ui';

interface UserTypeStepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
}

export const UserTypeStep: React.FC<UserTypeStepProps> = ({ data, updateData }) => {
  const { t } = useLanguage();

  const handleUserTypeSelect = (userType: UserType) => {
    updateData({ userType });
  };

  const userTypes = [
    {
      type: 'volunteer' as UserType,
      icon: '🙋‍♂️',
      title: t('onboarding.userType.volunteer.title'),
      description: t('onboarding.userType.volunteer.desc'),
      features: [
        t('onboarding.userType.volunteer.feature1'),
        t('onboarding.userType.volunteer.feature2'),
        t('onboarding.userType.volunteer.feature3'),
      ],
      color: 'bg-pixel-coral dark:bg-neon-pink',
    },
    {
      type: 'organization' as UserType,
      icon: '🏢',
      title: t('onboarding.userType.org.title'),
      description: t('onboarding.userType.org.desc'),
      features: [
        t('onboarding.userType.org.feature1'),
        t('onboarding.userType.org.feature2'),
        t('onboarding.userType.org.feature3'),
      ],
      color: 'bg-electric-teal dark:bg-neon-cyan',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <p className="text-ink dark:text-gray-300 text-lg">
          {t('onboarding.userType.question')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {userTypes.map((userType) => (
          <PxCard
            key={userType.type}
            className={`p-6 cursor-pointer transition-all duration-300 transform hover:scale-105 ${
              data.userType === userType.type
                ? 'ring-4 ring-primary dark:ring-neon-cyan shadow-px-glow'
                : 'hover:shadow-px'
            }`}
            onClick={() => handleUserTypeSelect(userType.type)}
          >
            <div className="text-center mb-6">
              <div className={`w-16 h-16 mx-auto mb-4 ${userType.color} rounded-lg flex items-center justify-center`}>
                <span className="text-3xl">{userType.icon}</span>
              </div>
              <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
                {userType.title}
              </h3>
              <p className="text-ink dark:text-gray-300">
                {userType.description}
              </p>
            </div>

            <div className="space-y-3">
              <h4 className="font-pixel text-sm text-ink dark:text-white">
                {t('onboarding.userType.features')}:
              </h4>
              <ul className="space-y-2">
                {userType.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm text-ink dark:text-gray-300">
                    <span className="text-primary dark:text-neon-green mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {data.userType === userType.type && (
              <div className="mt-4 text-center">
                <span className="inline-block px-4 py-2 bg-primary dark:bg-neon-cyan text-ink dark:text-dark-bg font-pixel text-xs rounded-lg">
                  {t('onboarding.userType.selected')}
                </span>
              </div>
            )}
          </PxCard>
        ))}
      </div>

      <div className="text-center text-sm text-ink dark:text-gray-400">
        {t('onboarding.userType.note')}
      </div>
    </div>
  );
};