"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxButton, PxCard, PxBadge, PxModal } from '../ui';
import { ProfileEditor } from './ProfileEditor';
import { ProfileVersionHistory } from './ProfileVersionHistory';
import { ProfilePreview } from './ProfilePreview';

export interface ProfileData {
  id: string;
  userType: 'volunteer' | 'organization';
  name: string;
  email: string;
  location: string;
  bio: string;
  avatar?: string;
  
  // Volunteer-specific fields
  skills?: string[];
  causes?: string[];
  interests?: string[];
  availability?: string;
  experience?: string;
  languages?: string[];
  
  // Organization-specific fields
  organizationName?: string;
  organizationType?: string;
  organizationSize?: string;
  website?: string;
  founded?: string;
  teamMembers?: TeamMember[];
  
  // Profile metadata
  completionScore: number;
  lastUpdated: string;
  version: number;
  isPublic: boolean;
  isVerified: boolean;
  verificationLevel: 'basic' | 'verified' | 'premium';
}

export interface ProfileVersion {
  id: string;
  version: number;
  data: ProfileData;
  timestamp: string;
  changes: string[];
  updatedBy: string;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  joinedDate: string;
}

interface ProfileManagementProps {
  profile: ProfileData;
  versions: ProfileVersion[];
  onSave: (data: ProfileData) => void;
  onRevert: (versionId: string) => void;
}

export const ProfileManagement: React.FC<ProfileManagementProps> = ({
  profile,
  versions,
  onSave,
  onRevert
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'edit' | 'preview' | 'history'>('edit');
  const [isEditMode, setIsEditMode] = useState(false);
  const [tempProfile, setTempProfile] = useState<ProfileData>(profile);
  const [showPreviewModal, setShowPreviewModal] = useState(false);

  const tabs = [
    { key: 'edit', label: t('profile.tabs.edit'), icon: '✏️' },
    { key: 'preview', label: t('profile.tabs.preview'), icon: '👁️' },
    { key: 'history', label: t('profile.tabs.history'), icon: '📜' }
  ];

  const getCompletionBadge = (score: number) => {
    if (score >= 90) return <PxBadge variant="success">💎 {t('profile.completion.complete')}</PxBadge>;
    if (score >= 70) return <PxBadge variant="info">⭐ {t('profile.completion.good')}</PxBadge>;
    if (score >= 50) return <PxBadge variant="warning">📝 {t('profile.completion.basic')}</PxBadge>;
    return <PxBadge variant="error">⚠️ {t('profile.completion.incomplete')}</PxBadge>;
  };

  const getVerificationBadge = (level: string, verified: boolean) => {
    if (!verified) return <PxBadge variant="default">🔒 {t('profile.verification.pending')}</PxBadge>;
    
    switch (level) {
      case 'premium': return <PxBadge variant="premium">👑 {t('profile.verification.premium')}</PxBadge>;
      case 'verified': return <PxBadge variant="success">✅ {t('profile.verification.verified')}</PxBadge>;
      default: return <PxBadge variant="info">📋 {t('profile.verification.basic')}</PxBadge>;
    }
  };

  const handleSave = () => {
    onSave(tempProfile);
    setIsEditMode(false);
    setTempProfile(profile); // Reset temp data
  };

  const handleCancel = () => {
    setTempProfile(profile); // Reset to original
    setIsEditMode(false);
  };

  const hasUnsavedChanges = JSON.stringify(tempProfile) !== JSON.stringify(profile);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Profile Header */}
      <PxCard className="p-6 bg-white dark:bg-dark-surface">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
              {profile.avatar ? (
                <img src={profile.avatar} alt={profile.name} className="w-full h-full rounded-lg object-cover" />
              ) : (
                <span className="text-2xl font-pixel text-ink dark:text-dark-bg">
                  {profile.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-pixel text-ink dark:text-white">
                  {profile.organizationName || profile.name}
                </h1>
                {getVerificationBadge(profile.verificationLevel, profile.isVerified)}
              </div>
              <div className="flex items-center gap-3 text-sm text-ink dark:text-gray-400">
                <span>📍 {profile.location}</span>
                <span>📅 {t('profile.lastUpdated')}: {new Date(profile.lastUpdated).toLocaleDateString()}</span>
                <span>v{profile.version}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {getCompletionBadge(profile.completionScore)}
            <div className="text-right">
              <div className="font-pixel text-lg text-ink dark:text-white">
                {profile.completionScore}%
              </div>
              <div className="text-xs text-ink dark:text-gray-400">
                {t('profile.completion.score')}
              </div>
            </div>
          </div>
        </div>
      </PxCard>

      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {tabs.map(tab => (
            <PxButton
              key={tab.key}
              variant={activeTab === tab.key ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab(tab.key as any)}
            >
              {tab.icon} {tab.label}
            </PxButton>
          ))}
        </div>

        <div className="flex items-center gap-3">
          {activeTab === 'edit' && (
            <>
              {isEditMode ? (
                <>
                  <PxButton
                    variant="secondary"
                    size="sm"
                    onClick={handleCancel}
                  >
                    {t('common.cancel')}
                  </PxButton>
                  <PxButton
                    variant="primary"
                    size="sm"
                    onClick={handleSave}
                    disabled={!hasUnsavedChanges}
                    className="hover:shadow-px-glow"
                  >
                    💾 {t('profile.save')}
                  </PxButton>
                </>
              ) : (
                <PxButton
                  variant="primary"
                  size="sm"
                  onClick={() => setIsEditMode(true)}
                >
                  ✏️ {t('profile.edit')}
                </PxButton>
              )}
            </>
          )}
          
          {activeTab === 'preview' && (
            <PxButton
              variant="secondary"
              size="sm"
              onClick={() => setShowPreviewModal(true)}
            >
              🚀 {t('profile.publicView')}
            </PxButton>
          )}
        </div>
      </div>

      {/* Unsaved Changes Warning */}
      {hasUnsavedChanges && isEditMode && (
        <PxCard className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-pixel text-sm text-yellow-800 dark:text-yellow-200">
                {t('profile.unsavedChanges')}
              </p>
              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                {t('profile.unsavedChanges.desc')}
              </p>
            </div>
          </div>
        </PxCard>
      )}

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'edit' && (
          <ProfileEditor
            profile={tempProfile}
            onChange={setTempProfile}
            isEditMode={isEditMode}
            onToggleEditMode={setIsEditMode}
          />
        )}
        
        {activeTab === 'preview' && (
          <ProfilePreview
            profile={profile}
            isPublic={profile.isPublic}
          />
        )}
        
        {activeTab === 'history' && (
          <ProfileVersionHistory
            versions={versions}
            currentVersion={profile.version}
            onRevert={onRevert}
          />
        )}
      </div>

      {/* Public View Modal */}
      <PxModal
        isOpen={showPreviewModal}
        onClose={() => setShowPreviewModal(false)}
        title={t('profile.publicView.title')}
        size="lg"
      >
        <ProfilePreview
          profile={profile}
          isPublic={true}
          showActions={false}
        />
      </PxModal>
    </div>
  );
};