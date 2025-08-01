"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxButton, PxCard, PxChip, PxModal, PxInput } from '../ui';
import { SearchFilters } from './AdvancedSearch';

export interface SavedSearch {
  id: string;
  name: string;
  filters: SearchFilters;
  alertEnabled: boolean;
  newResultsCount: number;
  lastRun: string;
  created: string;
}

interface SavedSearchesProps {
  savedSearches: SavedSearch[];
  onLoadSearch: (search: SavedSearch) => void;
  onSaveCurrentSearch: (name: string, filters: SearchFilters) => void;
  onDeleteSearch: (searchId: string) => void;
  onToggleAlert: (searchId: string, enabled: boolean) => void;
  currentFilters: SearchFilters;
}

export const SavedSearches: React.FC<SavedSearchesProps> = ({
  savedSearches,
  onLoadSearch,
  onSaveCurrentSearch,
  onDeleteSearch,
  onToggleAlert,
  currentFilters
}) => {
  const { t } = useLanguage();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchName, setSearchName] = useState('');

  const handleSaveSearch = () => {
    if (searchName.trim()) {
      onSaveCurrentSearch(searchName.trim(), currentFilters);
      setSearchName('');
      setIsModalOpen(false);
    }
  };

  const getActiveFiltersCount = (filters: SearchFilters) => {
    return (filters.location ? 1 : 0) +
           filters.causes.length +
           filters.skills.length +
           filters.timeCommitment.length +
           filters.type.length +
           (filters.remote ? 1 : 0) +
           (filters.sortBy !== 'relevance' ? 1 : 0) +
           (filters.datePosted !== 'any' ? 1 : 0);
  };

  const formatLastRun = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return t('search.saved.today');
    if (diffDays <= 7) return t('search.saved.daysAgo', { days: diffDays });
    return t('search.saved.weeksAgo', { weeks: Math.ceil(diffDays / 7) });
  };

  const currentFiltersCount = getActiveFiltersCount(currentFilters);
  const hasActiveFilters = currentFiltersCount > 0 || currentFilters.query.trim() !== '';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-pixel text-ink dark:text-white">
          {t('search.saved.title')}
        </h3>
        {hasActiveFilters && (
          <PxButton
            variant="secondary"
            size="sm"
            onClick={() => setIsModalOpen(true)}
          >
            💾 {t('search.saved.save')}
          </PxButton>
        )}
      </div>

      {/* Saved Searches List */}
      {savedSearches.length === 0 ? (
        <PxCard className="p-6 text-center bg-white dark:bg-dark-surface">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
            <span className="text-2xl">🔖</span>
          </div>
          <h4 className="font-pixel text-ink dark:text-white mb-2">
            {t('search.saved.empty.title')}
          </h4>
          <p className="text-sm text-ink dark:text-gray-400 mb-4">
            {t('search.saved.empty.desc')}
          </p>
          {hasActiveFilters && (
            <PxButton
              variant="primary"
              size="sm"
              onClick={() => setIsModalOpen(true)}
            >
              {t('search.saved.saveFirst')}
            </PxButton>
          )}
        </PxCard>
      ) : (
        <div className="space-y-3">
          {savedSearches.map((search) => (
            <PxCard 
              key={search.id}
              className="p-4 hover:shadow-px transition-all duration-300 bg-white dark:bg-dark-surface cursor-pointer"
              onClick={() => onLoadSearch(search)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <h4 className="font-pixel text-ink dark:text-white">
                    {search.name}
                  </h4>
                  {search.newResultsCount > 0 && (
                    <span className="bg-primary dark:bg-neon-cyan text-ink dark:text-dark-bg text-xs font-pixel px-2 py-1 rounded">
                      {search.newResultsCount} {t('search.saved.newResults')}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleAlert(search.id, !search.alertEnabled);
                    }}
                    className={`text-sm ${search.alertEnabled ? 'text-primary dark:text-neon-cyan' : 'text-gray-400'}`}
                    title={search.alertEnabled ? t('search.saved.alertOn') : t('search.saved.alertOff')}
                  >
                    🔔
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSearch(search.id);
                    }}
                    className="text-sm text-red-500 hover:text-red-600"
                    title={t('search.saved.delete')}
                  >
                    🗑️
                  </button>
                </div>
              </div>

              {/* Search Preview */}
              <div className="space-y-2">
                {search.filters.query && (
                  <div className="text-sm text-ink dark:text-gray-300">
                    <span className="font-semibold">"{search.filters.query}"</span>
                  </div>
                )}
                
                <div className="flex flex-wrap gap-1">
                  {search.filters.location && (
                    <PxChip size="sm" variant="default">📍 {search.filters.location}</PxChip>
                  )}
                  {search.filters.remote && (
                    <PxChip size="sm" variant="default">🌐 {t('search.remote')}</PxChip>
                  )}
                  {search.filters.causes.slice(0, 2).map(cause => (
                    <PxChip key={cause} size="sm" variant="selected">{cause}</PxChip>
                  ))}
                  {search.filters.causes.length > 2 && (
                    <PxChip size="sm">+{search.filters.causes.length - 2} {t('search.causes')}</PxChip>
                  )}
                  
                  {getActiveFiltersCount(search.filters) > 0 && (
                    <PxChip size="sm" variant="info">
                      {getActiveFiltersCount(search.filters)} {t('search.filters')}
                    </PxChip>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 text-xs text-ink dark:text-gray-400">
                <span>{t('search.saved.lastRun')}: {formatLastRun(search.lastRun)}</span>
                <span>{t('search.saved.created')}: {new Date(search.created).toLocaleDateString()}</span>
              </div>
            </PxCard>
          ))}
        </div>
      )}

      {/* Save Search Modal */}
      <PxModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={t('search.saved.modal.title')}
      >
        <div className="space-y-4">
          <p className="text-ink dark:text-gray-300">
            {t('search.saved.modal.desc')}
          </p>
          
          <PxInput
            label={t('search.saved.modal.name')}
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
            placeholder={t('search.saved.modal.placeholder')}
            autoFocus
          />

          {/* Current Filters Preview */}
          <div className="bg-gray-50 dark:bg-dark-bg p-4 rounded-lg">
            <h5 className="text-sm font-pixel text-ink dark:text-white mb-2">
              {t('search.saved.modal.preview')}:
            </h5>
            <div className="space-y-2">
              {currentFilters.query && (
                <div className="text-sm">"{currentFilters.query}"</div>
              )}
              <div className="flex flex-wrap gap-1">
                {currentFilters.location && (
                  <PxChip size="sm">📍 {currentFilters.location}</PxChip>
                )}
                {currentFilters.causes.slice(0, 3).map(cause => (
                  <PxChip key={cause} size="sm" variant="selected">{cause}</PxChip>
                ))}
                {currentFilters.causes.length > 3 && (
                  <PxChip size="sm">+{currentFilters.causes.length - 3} {t('common.more')}</PxChip>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3">
            <PxButton
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              {t('common.cancel')}
            </PxButton>
            <PxButton
              variant="primary"
              onClick={handleSaveSearch}
              disabled={!searchName.trim()}
            >
              {t('search.saved.modal.save')}
            </PxButton>
          </div>
        </div>
      </PxModal>
    </div>
  );
};