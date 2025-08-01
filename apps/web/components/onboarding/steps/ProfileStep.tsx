"use client";

import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { OnboardingData } from '../OnboardingFlow';
import { PxInput } from '../../ui';

interface ProfileStepProps {
  data: OnboardingData;
  updateData: (updates: Partial<OnboardingData>) => void;
  onNext: () => void;
}

export const ProfileStep: React.FC<ProfileStepProps> = ({ data, updateData }) => {
  const { t } = useLanguage();

  const handleInputChange = (field: keyof OnboardingData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    updateData({ [field]: e.target.value });
  };

  const locations = [
    'Amman, Jordan',
    'Beirut, Lebanon', 
    'Cairo, Egypt',
    'Dubai, UAE',
    'Riyadh, Saudi Arabia',
    'Baghdad, Iraq',
    'Kuwait City, Kuwait',
    'Doha, Qatar',
    'Manama, Bahrain',
    'Muscat, Oman',
    'Other'
  ];

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <p className="text-ink dark:text-gray-300">
          {data.userType === 'volunteer' 
            ? t('onboarding.profile.intro.volunteer')
            : t('onboarding.profile.intro.org')
          }
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Info */}
        <div className="space-y-4">
          <PxInput
            label={data.userType === 'volunteer' 
              ? t('onboarding.profile.name') 
              : t('onboarding.profile.contactName')
            }
            value={data.name}
            onChange={handleInputChange('name')}
            placeholder={data.userType === 'volunteer' 
              ? t('onboarding.profile.namePlaceholder')
              : t('onboarding.profile.contactNamePlaceholder')
            }
            required
          />

          <PxInput
            label={t('onboarding.profile.email')}
            type="email"
            value={data.email}
            onChange={handleInputChange('email')}
            placeholder={t('onboarding.profile.emailPlaceholder')}
            required
          />

          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
              {t('onboarding.profile.location')} *
            </label>
            <select
              value={data.location}
              onChange={(e) => updateData({ location: e.target.value })}
              className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
              required
            >
              <option value="">{t('onboarding.profile.locationPlaceholder')}</option>
              {locations.map(location => (
                <option key={location} value={location}>{location}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Organization-specific fields */}
        {data.userType === 'organization' && (
          <div className="space-y-4">
            <PxInput
              label={t('onboarding.profile.orgName')}
              value={data.organizationName || ''}
              onChange={(e) => updateData({ organizationName: e.target.value })}
              placeholder={t('onboarding.profile.orgNamePlaceholder')}
              required
            />

            <div>
              <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                {t('onboarding.profile.orgType')}
              </label>
              <select
                value={data.organizationType || ''}
                onChange={(e) => updateData({ organizationType: e.target.value })}
                className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
              >
                <option value="">{t('onboarding.profile.orgTypePlaceholder')}</option>
                <option value="nonprofit">{t('onboarding.profile.orgTypes.nonprofit')}</option>
                <option value="charity">{t('onboarding.profile.orgTypes.charity')}</option>
                <option value="ngo">{t('onboarding.profile.orgTypes.ngo')}</option>
                <option value="social-enterprise">{t('onboarding.profile.orgTypes.socialEnterprise')}</option>
                <option value="community-group">{t('onboarding.profile.orgTypes.communityGroup')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                {t('onboarding.profile.orgSize')}
              </label>
              <select
                value={data.organizationSize || ''}
                onChange={(e) => updateData({ organizationSize: e.target.value })}
                className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
              >
                <option value="">{t('onboarding.profile.orgSizePlaceholder')}</option>
                <option value="1-5">{t('onboarding.profile.orgSizes.small')}</option>
                <option value="6-20">{t('onboarding.profile.orgSizes.medium')}</option>
                <option value="21-50">{t('onboarding.profile.orgSizes.large')}</option>
                <option value="50+">{t('onboarding.profile.orgSizes.xlarge')}</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Bio */}
      <div>
        <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
          {data.userType === 'volunteer' 
            ? t('onboarding.profile.bio')
            : t('onboarding.profile.orgDesc')
          }
        </label>
        <textarea
          value={data.bio}
          onChange={handleInputChange('bio')}
          placeholder={data.userType === 'volunteer' 
            ? t('onboarding.profile.bioPlaceholder')
            : t('onboarding.profile.orgDescPlaceholder')
          }
          className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 resize-none"
          rows={4}
        />
      </div>
    </div>
  );
};