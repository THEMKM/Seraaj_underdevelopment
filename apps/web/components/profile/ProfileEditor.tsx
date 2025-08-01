"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { ProfileData } from './ProfileManagement';
import { PxInput, PxCard, PxChip, PxButton, PxProgress } from '../ui';

interface ProfileEditorProps {
  profile: ProfileData;
  onChange: (profile: ProfileData) => void;
  isEditMode: boolean;
  onToggleEditMode: (enabled: boolean) => void;
}

export const ProfileEditor: React.FC<ProfileEditorProps> = ({
  profile,
  onChange,
  isEditMode,
  onToggleEditMode
}) => {
  const { t } = useLanguage();

  const skillOptions = [
    'Teaching', 'Mentoring', 'Social Media', 'Graphic Design', 'Writing',
    'Photography', 'Video Editing', 'Web Development', 'Marketing',
    'Project Management', 'Event Planning', 'Fundraising', 'Public Speaking',
    'Translation', 'Data Analysis', 'Research', 'Healthcare', 'Counseling'
  ];

  const causeOptions = [
    'Education', 'Health', 'Environment', 'Poverty', 'Human Rights',
    'Refugees', 'Women Empowerment', 'Youth Development', 'Elderly Care',
    'Disability Support', 'Mental Health', 'Community Development',
    'Food Security', 'Water & Sanitation', 'Technology for Good'
  ];

  const interestOptions = [
    'Direct Service', 'Advocacy', 'Research', 'Capacity Building',
    'Emergency Response', 'Policy Work', 'Creative Projects',
    'Technology Solutions', 'Community Outreach', 'Training & Workshops'
  ];

  const languageOptions = [
    'Arabic', 'English', 'French', 'Spanish', 'Turkish', 'Persian', 'Hebrew', 'Kurdish'
  ];

  const calculateCompletionScore = (profileData: ProfileData): number => {
    let score = 0;
    const weights = {
      basic: 5, // name, email, location, bio
      avatar: 10,
      skills: 15,
      causes: 15,
      interests: 10,
      availability: 10,
      experience: 10,
      languages: 10,
      // Organization specific
      organizationName: 5,
      organizationType: 5,
      website: 5,
      founded: 5
    };

    // Basic fields
    if (profileData.name) score += weights.basic;
    if (profileData.email) score += weights.basic;
    if (profileData.location) score += weights.basic;
    if (profileData.bio && profileData.bio.length > 50) score += weights.basic;
    if (profileData.avatar) score += weights.avatar;

    if (profileData.userType === 'volunteer') {
      if (profileData.skills && profileData.skills.length > 0) score += weights.skills;
      if (profileData.causes && profileData.causes.length > 0) score += weights.causes;
      if (profileData.interests && profileData.interests.length > 0) score += weights.interests;
      if (profileData.availability) score += weights.availability;
      if (profileData.experience && profileData.experience.length > 100) score += weights.experience;
      if (profileData.languages && profileData.languages.length > 0) score += weights.languages;
    } else {
      if (profileData.organizationName) score += weights.organizationName;
      if (profileData.organizationType) score += weights.organizationType;
      if (profileData.website) score += weights.website;
      if (profileData.founded) score += weights.founded;
      if (profileData.causes && profileData.causes.length > 0) score += weights.causes;
    }

    return Math.min(100, score);
  };

  const updateProfile = (updates: Partial<ProfileData>) => {
    const updated = { ...profile, ...updates };
    updated.completionScore = calculateCompletionScore(updated);
    updated.lastUpdated = new Date().toISOString();
    onChange(updated);
  };

  const toggleArrayItem = (array: string[] = [], item: string) => {
    return array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  const renderBasicFields = () => (
    <PxCard className="p-6 space-y-4">
      <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
        {t('profile.sections.basic')}
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PxInput
          label={profile.userType === 'volunteer' ? t('profile.fields.name') : t('profile.fields.contactName')}
          value={profile.name}
          onChange={(e) => updateProfile({ name: e.target.value })}
          disabled={!isEditMode}
          required
        />
        
        <PxInput
          label={t('profile.fields.email')}
          type="email"
          value={profile.email}
          onChange={(e) => updateProfile({ email: e.target.value })}
          disabled={!isEditMode}
          required
        />
        
        <PxInput
          label={t('profile.fields.location')}
          value={profile.location}
          onChange={(e) => updateProfile({ location: e.target.value })}
          disabled={!isEditMode}
          required
        />

        {profile.userType === 'organization' && (
          <>
            <PxInput
              label={t('profile.fields.organizationName')}
              value={profile.organizationName || ''}
              onChange={(e) => updateProfile({ organizationName: e.target.value })}
              disabled={!isEditMode}
              required
            />
            
            <div>
              <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                {t('profile.fields.organizationType')}
              </label>
              <select
                value={profile.organizationType || ''}
                onChange={(e) => updateProfile({ organizationType: e.target.value })}
                disabled={!isEditMode}
                className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 disabled:opacity-50"
              >
                <option value="">{t('profile.fields.organizationType.placeholder')}</option>
                <option value="nonprofit">{t('profile.orgTypes.nonprofit')}</option>
                <option value="charity">{t('profile.orgTypes.charity')}</option>
                <option value="ngo">{t('profile.orgTypes.ngo')}</option>
                <option value="social-enterprise">{t('profile.orgTypes.socialEnterprise')}</option>
                <option value="community-group">{t('profile.orgTypes.communityGroup')}</option>
              </select>
            </div>

            <PxInput
              label={t('profile.fields.website')}
              type="url"
              value={profile.website || ''}
              onChange={(e) => updateProfile({ website: e.target.value })}
              disabled={!isEditMode}
              placeholder="https://..."
            />
          </>
        )}
      </div>

      <div>
        <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
          {profile.userType === 'volunteer' ? t('profile.fields.bio') : t('profile.fields.organizationDescription')}
        </label>
        <textarea
          value={profile.bio}
          onChange={(e) => updateProfile({ bio: e.target.value })}
          disabled={!isEditMode}
          placeholder={profile.userType === 'volunteer' 
            ? t('profile.fields.bio.placeholder')
            : t('profile.fields.organizationDescription.placeholder')
          }
          className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 resize-none disabled:opacity-50"
          rows={4}
        />
        <div className="text-xs text-ink dark:text-gray-400 mt-1">
          {profile.bio.length}/500 {t('profile.fields.characters')}
        </div>
      </div>
    </PxCard>
  );

  const renderVolunteerFields = () => {
    if (profile.userType !== 'volunteer') return null;

    return (
      <>
        {/* Skills & Expertise */}
        <PxCard className="p-6 space-y-4">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('profile.sections.skillsExpertise')}
          </h3>
          
          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
              {t('profile.fields.skills')}
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {skillOptions.map(skill => (
                <PxChip
                  key={skill}
                  variant={profile.skills?.includes(skill) ? 'selected' : 'default'}
                  onClick={() => isEditMode && updateProfile({ 
                    skills: toggleArrayItem(profile.skills, skill) 
                  })}
                  className={isEditMode ? "cursor-pointer" : "cursor-default"}
                  size="sm"
                >
                  {skill}
                </PxChip>
              ))}
            </div>
            <p className="text-xs text-ink dark:text-gray-400">
              {t('profile.fields.skills.selected', { count: profile.skills?.length || 0 })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                {t('profile.fields.availability')}
              </label>
              <select
                value={profile.availability || ''}
                onChange={(e) => updateProfile({ availability: e.target.value })}
                disabled={!isEditMode}
                className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 disabled:opacity-50"
              >
                <option value="">{t('profile.fields.availability.placeholder')}</option>
                <option value="1-2">1-2 {t('profile.fields.hoursPerWeek')}</option>
                <option value="3-5">3-5 {t('profile.fields.hoursPerWeek')}</option>
                <option value="6-10">6-10 {t('profile.fields.hoursPerWeek')}</option>
                <option value="10+">10+ {t('profile.fields.hoursPerWeek')}</option>
                <option value="flexible">{t('profile.fields.flexible')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
                {t('profile.fields.languages')}
              </label>
              <div className="flex flex-wrap gap-1">
                {languageOptions.map(language => (
                  <PxChip
                    key={language}
                    variant={profile.languages?.includes(language) ? 'selected' : 'default'}
                    onClick={() => isEditMode && updateProfile({ 
                      languages: toggleArrayItem(profile.languages, language) 
                    })}
                    className={isEditMode ? "cursor-pointer" : "cursor-default"}
                    size="sm"
                  >
                    {language}
                  </PxChip>
                ))}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
              {t('profile.fields.experience')}
            </label>
            <textarea
              value={profile.experience || ''}
              onChange={(e) => updateProfile({ experience: e.target.value })}
              disabled={!isEditMode}
              placeholder={t('profile.fields.experience.placeholder')}
              className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 resize-none disabled:opacity-50"
              rows={3}
            />
            <div className="text-xs text-ink dark:text-gray-400 mt-1">
              {(profile.experience || '').length}/1000 {t('profile.fields.characters')}
            </div>
          </div>
        </PxCard>

        {/* Interests & Causes */}
        <PxCard className="p-6 space-y-4">
          <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
            {t('profile.sections.interestsCauses')}
          </h3>
          
          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
              {t('profile.fields.causes')}
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {causeOptions.map(cause => (
                <PxChip
                  key={cause}
                  variant={profile.causes?.includes(cause) ? 'selected' : 'default'}
                  onClick={() => isEditMode && updateProfile({ 
                    causes: toggleArrayItem(profile.causes, cause) 
                  })}
                  className={isEditMode ? "cursor-pointer" : "cursor-default"}
                  size="sm"
                >
                  {cause}
                </PxChip>
              ))}
            </div>
            <p className="text-xs text-ink dark:text-gray-400">
              {t('profile.fields.causes.selected', { count: profile.causes?.length || 0 })}
            </p>
          </div>

          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
              {t('profile.fields.interests')}
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {interestOptions.map(interest => (
                <PxChip
                  key={interest}
                  variant={profile.interests?.includes(interest) ? 'selected' : 'default'}
                  onClick={() => isEditMode && updateProfile({ 
                    interests: toggleArrayItem(profile.interests, interest) 
                  })}
                  className={isEditMode ? "cursor-pointer" : "cursor-default"}
                  size="sm"
                >
                  {interest}
                </PxChip>
              ))}
            </div>
            <p className="text-xs text-ink dark:text-gray-400">
              {t('profile.fields.interests.selected', { count: profile.interests?.length || 0 })}
            </p>
          </div>
        </PxCard>
      </>
    );
  };

  const renderOrganizationFields = () => {
    if (profile.userType !== 'organization') return null;

    return (
      <PxCard className="p-6 space-y-4">
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('profile.sections.organizationDetails')}
        </h3>
        
        <div>
          <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
            {t('profile.fields.focusAreas')}
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {causeOptions.map(cause => (
              <PxChip
                key={cause}
                variant={profile.causes?.includes(cause) ? 'selected' : 'default'}
                onClick={() => isEditMode && updateProfile({ 
                  causes: toggleArrayItem(profile.causes, cause) 
                })}
                className={isEditMode ? "cursor-pointer" : "cursor-default"}
                size="sm"
              >
                {cause}
              </PxChip>
            ))}
          </div>
          <p className="text-xs text-ink dark:text-gray-400">
            {t('profile.fields.focusAreas.selected', { count: profile.causes?.length || 0 })}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <PxInput
            label={t('profile.fields.founded')}
            type="number"
            value={profile.founded || ''}
            onChange={(e) => updateProfile({ founded: e.target.value })}
            disabled={!isEditMode}
            placeholder="2020"
            min="1900"
            max={new Date().getFullYear()}
          />

          <div>
            <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
              {t('profile.fields.organizationSize')}
            </label>
            <select
              value={profile.organizationSize || ''}
              onChange={(e) => updateProfile({ organizationSize: e.target.value })}
              disabled={!isEditMode}
              className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300 disabled:opacity-50"
            >
              <option value="">{t('profile.fields.organizationSize.placeholder')}</option>
              <option value="1-5">1-5 {t('profile.fields.people')}</option>
              <option value="6-20">6-20 {t('profile.fields.people')}</option>
              <option value="21-50">21-50 {t('profile.fields.people')}</option>
              <option value="50+">50+ {t('profile.fields.people')}</option>
            </select>
          </div>
        </div>
      </PxCard>
    );
  };

  return (
    <div className="space-y-6">
      {/* Completion Progress */}
      <PxCard className="p-4 bg-gradient-to-r from-primary/10 to-electric-teal/10 dark:from-neon-cyan/10 dark:to-neon-pink/10">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-pixel text-ink dark:text-white">
            {t('profile.completion.title')}
          </h3>
          <span className="text-lg font-pixel text-ink dark:text-white">
            {profile.completionScore}%
          </span>
        </div>
        <PxProgress 
          value={profile.completionScore} 
          className="h-3 mb-2"
        />
        <p className="text-xs text-ink dark:text-gray-400">
          {profile.completionScore < 100 
            ? t('profile.completion.improve')
            : t('profile.completion.perfect')
          }
        </p>
      </PxCard>

      {/* Basic Information */}
      {renderBasicFields()}
      
      {/* Type-specific fields */}
      {renderVolunteerFields()}
      {renderOrganizationFields()}

      {/* Privacy Settings */}
      <PxCard className="p-6">
        <h3 className="text-lg font-pixel text-ink dark:text-white mb-4">
          {t('profile.sections.privacy')}
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border-2 border-ink/20 dark:border-dark-border rounded-lg">
            <div>
              <h4 className="font-pixel text-sm text-ink dark:text-white">
                {t('profile.privacy.publicProfile')}
              </h4>
              <p className="text-xs text-ink dark:text-gray-400">
                {t('profile.privacy.publicProfile.desc')}
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={profile.isPublic}
                onChange={(e) => updateProfile({ isPublic: e.target.checked })}
                disabled={!isEditMode}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 dark:peer-focus:ring-neon-cyan/25 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary dark:peer-checked:bg-neon-cyan"></div>
            </label>
          </div>
        </div>
      </PxCard>
    </div>
  );
};