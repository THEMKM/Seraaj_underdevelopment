"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { ProfileVersion } from './ProfileManagement';
import { PxCard, PxBadge, PxButton, PxModal } from '../ui';

interface ProfileVersionHistoryProps {
  versions: ProfileVersion[];
  currentVersion: number;
  onRevert: (versionId: string) => void;
}

export const ProfileVersionHistory: React.FC<ProfileVersionHistoryProps> = ({
  versions,
  currentVersion,
  onRevert
}) => {
  const { t } = useLanguage();
  const [selectedVersion, setSelectedVersion] = useState<ProfileVersion | null>(null);
  const [showRevertModal, setShowRevertModal] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return t('profile.history.today');
    if (diffDays <= 7) return t('profile.history.daysAgo', { days: diffDays });
    if (diffDays <= 30) return t('profile.history.weeksAgo', { weeks: Math.ceil(diffDays / 7) });
    return date.toLocaleDateString();
  };

  const getChangeTypeIcon = (change: string) => {
    if (change.includes('added')) return '➕';
    if (change.includes('removed')) return '➖';
    if (change.includes('updated') || change.includes('changed')) return '✏️';
    if (change.includes('created')) return '🆕';
    return '🔄';
  };

  const getVersionBadge = (version: ProfileVersion) => {
    if (version.version === currentVersion) {
      return <PxBadge variant="success">✅ {t('profile.history.current')}</PxBadge>;
    }
    
    const daysSince = Math.ceil(
      (new Date().getTime() - new Date(version.timestamp).getTime()) / (1000 * 60 * 60 * 24)
    );
    
    if (daysSince <= 1) return <PxBadge variant="info">🆕 {t('profile.history.recent')}</PxBadge>;
    if (daysSince <= 7) return <PxBadge variant="default">📅 {t('profile.history.thisWeek')}</PxBadge>;
    return <PxBadge variant="default">📜 {t('profile.history.older')}</PxBadge>;
  };

  const handleRevert = () => {
    if (selectedVersion) {
      onRevert(selectedVersion.id);
      setShowRevertModal(false);
      setSelectedVersion(null);
    }
  };

  if (versions.length === 0) {
    return (
      <PxCard className="p-12 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
          <span className="text-2xl">📜</span>
        </div>
        <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
          {t('profile.history.empty.title')}
        </h3>
        <p className="text-ink dark:text-gray-400">
          {t('profile.history.empty.desc')}
        </p>
      </PxCard>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-pixel text-ink dark:text-white">
            {t('profile.history.title')}
          </h3>
          <p className="text-sm text-ink dark:text-gray-400">
            {t('profile.history.subtitle', { count: versions.length })}
          </p>
        </div>
      </div>

      {/* Version Timeline */}
      <div className="space-y-3">
        {versions.map((version, index) => (
          <PxCard 
            key={version.id}
            className={`p-4 transition-all duration-300 ${
              version.version === currentVersion 
                ? 'ring-2 ring-primary dark:ring-neon-cyan bg-primary/5 dark:bg-neon-cyan/5' 
                : 'hover:shadow-px cursor-pointer'
            }`}
            onClick={() => version.version !== currentVersion && setSelectedVersion(version)}
          >
            <div className="flex items-start justify-between gap-4">
              {/* Version Info */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-pixel text-ink dark:text-white">
                    {t('profile.history.version')} {version.version}
                  </h4>
                  {getVersionBadge(version)}
                </div>
                
                <div className="flex items-center gap-4 text-sm text-ink dark:text-gray-400 mb-3">
                  <span>📅 {formatDate(version.timestamp)}</span>
                  <span>👤 {version.updatedBy}</span>
                  <span>🔢 {version.changes.length} {t('profile.history.changes')}</span>
                </div>

                {/* Changes List */}
                <div className="space-y-1">
                  {version.changes.slice(0, 3).map((change, changeIndex) => (
                    <div key={changeIndex} className="flex items-center gap-2 text-sm">
                      <span>{getChangeTypeIcon(change)}</span>
                      <span className="text-ink dark:text-gray-300">{change}</span>
                    </div>
                  ))}
                  {version.changes.length > 3 && (
                    <div className="text-xs text-ink dark:text-gray-400">
                      +{version.changes.length - 3} {t('profile.history.moreChanges')}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2">
                {version.version !== currentVersion && (
                  <>
                    <PxButton
                      variant="secondary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedVersion(version);
                        setShowRevertModal(true);
                      }}
                    >
                      🔄 {t('profile.history.revert')}
                    </PxButton>
                    <PxButton
                      variant="secondary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedVersion(version);
                      }}
                    >
                      👁️ {t('profile.history.view')}
                    </PxButton>
                  </>
                )}
              </div>
            </div>
          </PxCard>
        ))}
      </div>

      {/* Version Detail Modal */}
      {selectedVersion && (
        <PxModal
          isOpen={!!selectedVersion}
          onClose={() => setSelectedVersion(null)}
          title={t('profile.history.versionDetails', { version: selectedVersion.version })}
        >
          <div className="space-y-4">
            {/* Version Meta */}
            <div className="bg-gray-50 dark:bg-dark-bg p-4 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-pixel text-sm text-ink dark:text-white">
                  {t('profile.history.version')} {selectedVersion.version}
                </span>
                {getVersionBadge(selectedVersion)}
              </div>
              <div className="text-sm text-ink dark:text-gray-400">
                <p>📅 {new Date(selectedVersion.timestamp).toLocaleString()}</p>
                <p>👤 {t('profile.history.updatedBy')}: {selectedVersion.updatedBy}</p>
              </div>
            </div>

            {/* All Changes */}
            <div>
              <h4 className="font-pixel text-sm text-ink dark:text-white mb-3">
                {t('profile.history.allChanges')} ({selectedVersion.changes.length})
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {selectedVersion.changes.map((change, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm p-2 bg-white dark:bg-dark-surface rounded">
                    <span>{getChangeTypeIcon(change)}</span>
                    <span className="text-ink dark:text-gray-300">{change}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Profile Data Preview */}
            <div>
              <h4 className="font-pixel text-sm text-ink dark:text-white mb-3">
                {t('profile.history.profileData')}
              </h4>
              <div className="bg-gray-50 dark:bg-dark-bg p-4 rounded-lg text-sm max-h-48 overflow-y-auto">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p><strong>{t('profile.fields.name')}:</strong> {selectedVersion.data.name}</p>
                    <p><strong>{t('profile.fields.location')}:</strong> {selectedVersion.data.location}</p>
                    <p><strong>{t('profile.completion.score')}:</strong> {selectedVersion.data.completionScore}%</p>
                  </div>
                  <div>
                    {selectedVersion.data.skills && (
                      <p><strong>{t('profile.fields.skills')}:</strong> {selectedVersion.data.skills.length} items</p>
                    )}
                    {selectedVersion.data.causes && (
                      <p><strong>{t('profile.fields.causes')}:</strong> {selectedVersion.data.causes.length} items</p>
                    )}
                    <p><strong>{t('profile.fields.isPublic')}:</strong> {selectedVersion.data.isPublic ? t('common.yes') : t('common.no')}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-ink/20 dark:border-dark-border">
              <PxButton
                variant="secondary"
                onClick={() => setSelectedVersion(null)}
              >
                {t('common.close')}
              </PxButton>
              {selectedVersion.version !== currentVersion && (
                <PxButton
                  variant="primary"
                  onClick={() => setShowRevertModal(true)}
                >
                  🔄 {t('profile.history.revertToThis')}
                </PxButton>
              )}
            </div>
          </div>
        </PxModal>
      )}

      {/* Revert Confirmation Modal */}
      <PxModal
        isOpen={showRevertModal}
        onClose={() => setShowRevertModal(false)}
        title={t('profile.history.revertConfirm.title')}
      >
        <div className="space-y-4">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <h4 className="font-pixel text-sm text-yellow-800 dark:text-yellow-200 mb-2">
                  {t('profile.history.revertConfirm.warning')}
                </h4>
                <p className="text-sm text-yellow-600 dark:text-yellow-400">
                  {t('profile.history.revertConfirm.desc')}
                </p>
              </div>
            </div>
          </div>

          {selectedVersion && (
            <div className="bg-gray-50 dark:bg-dark-bg p-4 rounded-lg">
              <h4 className="font-pixel text-sm text-ink dark:text-white mb-2">
                {t('profile.history.revertingTo')}:
              </h4>
              <p className="text-sm text-ink dark:text-gray-300">
                {t('profile.history.version')} {selectedVersion.version} • {formatDate(selectedVersion.timestamp)}
              </p>
              <p className="text-xs text-ink dark:text-gray-400 mt-1">
                {selectedVersion.changes.length} {t('profile.history.changes')} • {t('profile.history.updatedBy')}: {selectedVersion.updatedBy}
              </p>
            </div>
          )}

          <div className="flex justify-end gap-3">
            <PxButton
              variant="secondary"
              onClick={() => setShowRevertModal(false)}
            >
              {t('common.cancel')}
            </PxButton>
            <PxButton
              variant="primary"
              onClick={handleRevert}
              className="bg-yellow-500 hover:bg-yellow-600 text-white"
            >
              🔄 {t('profile.history.confirmRevert')}
            </PxButton>
          </div>
        </div>
      </PxModal>
    </div>
  );
};