"use client";

import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { OnboardingData } from '../OnboardingFlow';
import { PxBadge, PxChip } from '../../ui';

interface CompletionStepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
}

export const CompletionStep: React.FC<CompletionStepProps> = ({ data }) => {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      {/* Success Animation */}
      <div className="text-center mb-8">
        <div className="w-24 h-24 mx-auto mb-6 bg-electric-teal dark:bg-neon-green rounded-full flex items-center justify-center animate-px-bounce">
          <span className="text-4xl">🎉</span>
        </div>
        <h3 className="text-2xl font-pixel text-ink dark:text-white mb-2">
          {t('onboarding.completion.success')}
        </h3>
        <p className="text-ink dark:text-gray-300">
          {data.userType === 'volunteer' 
            ? t('onboarding.completion.message.volunteer')
            : t('onboarding.completion.message.org')
          }
        </p>
      </div>

      {/* Profile Summary */}
      <div className="bg-gray-50 dark:bg-dark-bg rounded-lg p-6 space-y-4">
        <h4 className="font-pixel text-lg text-ink dark:text-white mb-4">
          {t('onboarding.completion.summary')}
        </h4>

        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-pixel text-ink dark:text-gray-400">
              {t('onboarding.profile.name')}:
            </span>
            <span className="ml-2 text-ink dark:text-white">{data.name}</span>
          </div>
          <div>
            <span className="font-pixel text-ink dark:text-gray-400">
              {t('onboarding.profile.location')}:
            </span>
            <span className="ml-2 text-ink dark:text-white">{data.location}</span>
          </div>
          {data.userType === 'organization' && data.organizationName && (
            <div className="md:col-span-2">
              <span className="font-pixel text-ink dark:text-gray-400">
                {t('onboarding.profile.orgName')}:
              </span>
              <span className="ml-2 text-ink dark:text-white">{data.organizationName}</span>
            </div>
          )}
        </div>

        {/* User Type Badge */}
        <div>
          <PxBadge variant={data.userType === 'volunteer' ? 'success' : 'info'}>
            {data.userType === 'volunteer' 
              ? t('onboarding.userType.volunteer.title')
              : t('onboarding.userType.org.title')
            }
          </PxBadge>
        </div>

        {/* Causes */}
        {data.causes.length > 0 && (
          <div>
            <span className="font-pixel text-sm text-ink dark:text-gray-400 block mb-2">
              {t('onboarding.preferences.causes.title')}:
            </span>
            <div className="flex flex-wrap gap-1">
              {data.causes.slice(0, 5).map(cause => (
                <PxChip key={cause} size="sm" variant="selected">
                  {cause}
                </PxChip>
              ))}
              {data.causes.length > 5 && (
                <PxChip size="sm">
                  +{data.causes.length - 5} {t('common.more')}
                </PxChip>
              )}
            </div>
          </div>
        )}

        {/* Volunteer Skills */}
        {data.userType === 'volunteer' && data.skills.length > 0 && (
          <div>
            <span className="font-pixel text-sm text-ink dark:text-gray-400 block mb-2">
              {t('onboarding.preferences.skills.title')}:
            </span>
            <div className="flex flex-wrap gap-1">
              {data.skills.slice(0, 4).map(skill => (
                <PxChip key={skill} size="sm">
                  {skill}
                </PxChip>
              ))}
              {data.skills.length > 4 && (
                <PxChip size="sm">
                  +{data.skills.length - 4} {t('common.more')}
                </PxChip>
              )}
            </div>
          </div>
        )}

        {/* Availability */}
        {data.userType === 'volunteer' && data.availability && (
          <div>
            <span className="font-pixel text-sm text-ink dark:text-gray-400">
              {t('onboarding.preferences.availability.title')}:
            </span>
            <span className="ml-2 text-ink dark:text-white">
              {data.availability} {t('onboarding.preferences.availability.hours')}
            </span>
          </div>
        )}
      </div>

      {/* Next Steps */}
      <div className="bg-primary/10 dark:bg-neon-cyan/10 rounded-lg p-6">
        <h4 className="font-pixel text-lg text-ink dark:text-white mb-4">
          {t('onboarding.completion.nextSteps.title')}
        </h4>
        <ul className="space-y-3 text-sm text-ink dark:text-gray-300">
          {data.userType === 'volunteer' ? (
            <>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-green mr-2 mt-0.5">1.</span>
                {t('onboarding.completion.nextSteps.volunteer.step1')}
              </li>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-green mr-2 mt-0.5">2.</span>
                {t('onboarding.completion.nextSteps.volunteer.step2')}
              </li>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-green mr-2 mt-0.5">3.</span>
                {t('onboarding.completion.nextSteps.volunteer.step3')}
              </li>
            </>
          ) : (
            <>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-cyan mr-2 mt-0.5">1.</span>
                {t('onboarding.completion.nextSteps.org.step1')}
              </li>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-cyan mr-2 mt-0.5">2.</span>
                {t('onboarding.completion.nextSteps.org.step2')}
              </li>
              <li className="flex items-start">
                <span className="text-primary dark:text-neon-cyan mr-2 mt-0.5">3.</span>
                {t('onboarding.completion.nextSteps.org.step3')}
              </li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
};