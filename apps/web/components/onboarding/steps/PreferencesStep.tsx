"use client";

import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { OnboardingData } from '../OnboardingFlow';
import { PxChip } from '../../ui';

interface PreferencesStepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
}

export const PreferencesStep: React.FC<PreferencesStepProps> = ({ data, updateData }) => {
  const { t } = useLanguage();

  const causes = [
    'Education', 'Health', 'Environment', 'Poverty', 'Human Rights',
    'Refugees', 'Women Empowerment', 'Youth Development', 'Elderly Care',
    'Disability Support', 'Mental Health', 'Community Development',
    'Food Security', 'Water & Sanitation', 'Technology for Good'
  ];

  const volunteerSkills = [
    'Teaching', 'Mentoring', 'Social Media', 'Graphic Design', 'Writing',
    'Photography', 'Video Editing', 'Web Development', 'Marketing',
    'Project Management', 'Event Planning', 'Fundraising', 'Public Speaking',
    'Translation', 'Data Analysis', 'Research', 'Healthcare', 'Counseling'
  ];

  const interests = [
    'Direct Service', 'Advocacy', 'Research', 'Capacity Building',
    'Emergency Response', 'Policy Work', 'Creative Projects',
    'Technology Solutions', 'Community Outreach', 'Training & Workshops'
  ];

  const availabilityOptions = [
    { value: '1-2', label: t('onboarding.preferences.availability.minimal') },
    { value: '3-5', label: t('onboarding.preferences.availability.moderate') },
    { value: '6-10', label: t('onboarding.preferences.availability.significant') },
    { value: '10+', label: t('onboarding.preferences.availability.extensive') },
  ];

  const toggleArrayItem = (array: string[], item: string) => {
    return array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  const handleCauseToggle = (cause: string) => {
    updateData({ causes: toggleArrayItem(data.causes, cause) });
  };

  const handleSkillToggle = (skill: string) => {
    updateData({ skills: toggleArrayItem(data.skills, skill) });
  };

  const handleInterestToggle = (interest: string) => {
    updateData({ interests: toggleArrayItem(data.interests, interest) });
  };

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <p className="text-ink dark:text-gray-300">
          {data.userType === 'volunteer' 
            ? t('onboarding.preferences.intro.volunteer')
            : t('onboarding.preferences.intro.org')
          }
        </p>
      </div>

      {/* Causes */}
      <div>
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('onboarding.preferences.causes.title')} *
        </h3>
        <p className="text-sm text-ink dark:text-gray-400 mb-4">
          {data.userType === 'volunteer' 
            ? t('onboarding.preferences.causes.desc.volunteer')
            : t('onboarding.preferences.causes.desc.org')
          }
        </p>
        <div className="flex flex-wrap gap-2">
          {causes.map(cause => (
            <PxChip
              key={cause}
              variant={data.causes.includes(cause) ? 'selected' : 'default'}
              onClick={() => handleCauseToggle(cause)}
              className="cursor-pointer"
            >
              {cause}
            </PxChip>
          ))}
        </div>
      </div>

      {data.userType === 'volunteer' && (
        <>
          {/* Skills */}
          <div>
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('onboarding.preferences.skills.title')}
            </h3>
            <p className="text-sm text-ink dark:text-gray-400 mb-4">
              {t('onboarding.preferences.skills.desc')}
            </p>
            <div className="flex flex-wrap gap-2">
              {volunteerSkills.map(skill => (
                <PxChip
                  key={skill}
                  variant={data.skills.includes(skill) ? 'selected' : 'default'}
                  onClick={() => handleSkillToggle(skill)}
                  className="cursor-pointer"
                >
                  {skill}
                </PxChip>
              ))}
            </div>
          </div>

          {/* Interests */}
          <div>
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('onboarding.preferences.interests.title')}
            </h3>
            <p className="text-sm text-ink dark:text-gray-400 mb-4">
              {t('onboarding.preferences.interests.desc')}
            </p>
            <div className="flex flex-wrap gap-2">
              {interests.map(interest => (
                <PxChip
                  key={interest}
                  variant={data.interests.includes(interest) ? 'selected' : 'default'}
                  onClick={() => handleInterestToggle(interest)}
                  className="cursor-pointer"
                >
                  {interest}
                </PxChip>
              ))}
            </div>
          </div>

          {/* Availability */}
          <div>
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('onboarding.preferences.availability.title')}
            </h3>
            <p className="text-sm text-ink dark:text-gray-400 mb-4">
              {t('onboarding.preferences.availability.desc')}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {availabilityOptions.map(option => (
                <div
                  key={option.value}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-300 ${
                    data.availability === option.value
                      ? 'border-primary dark:border-neon-cyan bg-primary/10 dark:bg-neon-cyan/10'
                      : 'border-ink/20 dark:border-dark-border hover:border-primary dark:hover:border-neon-cyan'
                  }`}
                  onClick={() => updateData({ availability: option.value })}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-pixel text-sm text-ink dark:text-white">
                      {option.value} {t('onboarding.preferences.availability.hours')}
                    </span>
                    {data.availability === option.value && (
                      <span className="text-primary dark:text-neon-cyan">✓</span>
                    )}
                  </div>
                  <p className="text-xs text-ink dark:text-gray-400 mt-1">
                    {option.label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <div className="text-center text-sm text-ink dark:text-gray-400">
        {t('onboarding.preferences.note')}
      </div>
    </div>
  );
};