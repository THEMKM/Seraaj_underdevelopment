"use client";

import React from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { ProfileData } from './ProfileManagement';
import { PxCard, PxChip, PxBadge, PxButton } from '../ui';

interface ProfilePreviewProps {
  profile: ProfileData;
  isPublic: boolean;
  showActions?: boolean;
}

export const ProfilePreview: React.FC<ProfilePreviewProps> = ({
  profile,
  isPublic,
  showActions = true
}) => {
  const { t } = useLanguage();

  const getVerificationBadge = (level: string, verified: boolean) => {
    if (!verified) return null;
    
    switch (level) {
      case 'premium': return <PxBadge variant="premium">👑 {t('profile.verification.premium')}</PxBadge>;
      case 'verified': return <PxBadge variant="success">✅ {t('profile.verification.verified')}</PxBadge>;
      default: return <PxBadge variant="info">📋 {t('profile.verification.basic')}</PxBadge>;
    }
  };

  const renderVolunteerProfile = () => {
    if (profile.userType !== 'volunteer') return null;

    return (
      <>
        {/* Skills & Expertise */}
        {profile.skills && profile.skills.length > 0 && (
          <PxCard className="p-6">
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('profile.sections.skillsExpertise')}
            </h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-pixel text-ink dark:text-gray-400 mb-2">
                  {t('profile.fields.skills')}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map(skill => (
                    <PxChip key={skill} size="sm" variant="selected">
                      {skill}
                    </PxChip>
                  ))}
                </div>
              </div>

              {profile.languages && profile.languages.length > 0 && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400 mb-2">
                    {t('profile.fields.languages')}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.languages.map(language => (
                      <PxChip key={language} size="sm">
                        {language}
                      </PxChip>
                    ))}
                  </div>
                </div>
              )}

              {profile.availability && (
                <div className="flex items-center gap-4">
                  <div>
                    <h4 className="text-sm font-pixel text-ink dark:text-gray-400">
                      {t('profile.fields.availability')}
                    </h4>
                    <p className="text-ink dark:text-white">
                      {profile.availability === 'flexible' 
                        ? t('profile.fields.flexible')
                        : `${profile.availability} ${t('profile.fields.hoursPerWeek')}`
                      }
                    </p>
                  </div>
                </div>
              )}
            </div>
          </PxCard>
        )}

        {/* Experience */}
        {profile.experience && (
          <PxCard className="p-6">
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('profile.fields.experience')}
            </h3>
            <p className="text-ink dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
              {profile.experience}
            </p>
          </PxCard>
        )}

        {/* Interests & Causes */}
        {((profile.causes && profile.causes.length > 0) || (profile.interests && profile.interests.length > 0)) && (
          <PxCard className="p-6">
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('profile.sections.interestsCauses')}
            </h3>
            
            <div className="space-y-4">
              {profile.causes && profile.causes.length > 0 && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400 mb-2">
                    {t('profile.fields.causes')}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.causes.map(cause => (
                      <PxChip key={cause} size="sm" variant="selected">
                        {cause}
                      </PxChip>
                    ))}
                  </div>
                </div>
              )}

              {profile.interests && profile.interests.length > 0 && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400 mb-2">
                    {t('profile.fields.interests')}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.interests.map(interest => (
                      <PxChip key={interest} size="sm">
                        {interest}
                      </PxChip>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </PxCard>
        )}
      </>
    );
  };

  const renderOrganizationProfile = () => {
    if (profile.userType !== 'organization') return null;

    return (
      <>
        {/* Organization Details */}
        <PxCard className="p-6">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('profile.sections.organizationDetails')}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              {profile.organizationType && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400">
                    {t('profile.fields.organizationType')}
                  </h4>
                  <p className="text-ink dark:text-white">
                    {t(`profile.orgTypes.${profile.organizationType}`)}
                  </p>
                </div>
              )}

              {profile.founded && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400">
                    {t('profile.fields.founded')}
                  </h4>
                  <p className="text-ink dark:text-white">{profile.founded}</p>
                </div>
              )}

              {profile.organizationSize && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400">
                    {t('profile.fields.organizationSize')}
                  </h4>
                  <p className="text-ink dark:text-white">
                    {profile.organizationSize} {t('profile.fields.people')}
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-3">
              {profile.website && (
                <div>
                  <h4 className="text-sm font-pixel text-ink dark:text-gray-400">
                    {t('profile.fields.website')}
                  </h4>
                  <a 
                    href={profile.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary dark:text-neon-cyan hover:underline"
                  >
                    {profile.website}
                  </a>
                </div>
              )}
            </div>
          </div>
        </PxCard>

        {/* Focus Areas */}
        {profile.causes && profile.causes.length > 0 && (
          <PxCard className="p-6">
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {t('profile.fields.focusAreas')}
            </h3>
            <div className="flex flex-wrap gap-2">
              {profile.causes.map(cause => (
                <PxChip key={cause} size="sm" variant="selected">
                  {cause}
                </PxChip>
              ))}
            </div>
          </PxCard>
        )}
      </>
    );
  };

  if (!isPublic && !profile.isPublic) {
    return (
      <PxCard className="p-12 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
          <span className="text-2xl">🔒</span>
        </div>
        <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
          {t('profile.preview.private.title')}
        </h3>
        <p className="text-ink dark:text-gray-400 mb-6">
          {t('profile.preview.private.desc')}
        </p>
        {showActions && (
          <PxButton variant="primary" size="sm">
            {t('profile.preview.makePublic')}
          </PxButton>
        )}
      </PxCard>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <PxCard className="p-6">
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-24 h-24 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
              {profile.avatar ? (
                <img 
                  src={profile.avatar} 
                  alt={profile.organizationName || profile.name} 
                  className="w-full h-full rounded-lg object-cover" 
                />
              ) : (
                <span className="text-3xl font-pixel text-ink dark:text-dark-bg">
                  {(profile.organizationName || profile.name).charAt(0).toUpperCase()}
                </span>
              )}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl font-pixel text-ink dark:text-white">
                    {profile.organizationName || profile.name}
                  </h1>
                  {getVerificationBadge(profile.verificationLevel, profile.isVerified)}
                </div>
                <div className="flex items-center gap-3 text-sm text-ink dark:text-gray-400 mb-3">
                  <span>📍 {profile.location}</span>
                  {profile.userType === 'volunteer' && profile.availability && (
                    <span>⏰ {profile.availability === 'flexible' 
                      ? t('profile.fields.flexible')
                      : `${profile.availability} ${t('profile.fields.hoursPerWeek')}`
                    }</span>
                  )}
                </div>
              </div>

              {showActions && (
                <div className="flex gap-2">
                  <PxButton variant="primary" size="sm">
                    {profile.userType === 'volunteer' 
                      ? t('profile.actions.contact')
                      : t('profile.actions.viewOpportunities')
                    }
                  </PxButton>
                  <PxButton variant="secondary" size="sm">
                    💾 {t('profile.actions.save')}
                  </PxButton>
                </div>
              )}
            </div>

            {/* Bio */}
            {profile.bio && (
              <p className="text-ink dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {profile.bio}
              </p>
            )}
          </div>
        </div>
      </PxCard>

      {/* Type-specific content */}
      {renderVolunteerProfile()}
      {renderOrganizationProfile()}

      {/* Contact Actions (for public view) */}
      {isPublic && showActions && (
        <PxCard className="p-6 bg-gradient-to-r from-primary/10 to-electric-teal/10 dark:from-neon-cyan/10 dark:to-neon-pink/10">
          <div className="text-center">
            <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
              {profile.userType === 'volunteer' 
                ? t('profile.cta.volunteer.title')
                : t('profile.cta.organization.title')
              }
            </h3>
            <p className="text-ink dark:text-gray-300 mb-6">
              {profile.userType === 'volunteer' 
                ? t('profile.cta.volunteer.desc')
                : t('profile.cta.organization.desc')
              }
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <PxButton variant="primary" className="hover:shadow-px-glow">
                {profile.userType === 'volunteer' 
                  ? t('profile.cta.volunteer.action')
                  : t('profile.cta.organization.action')
                }
              </PxButton>
              <PxButton variant="secondary">
                💬 {t('profile.actions.message')}
              </PxButton>
            </div>
          </div>
        </PxCard>
      )}
    </div>
  );
};