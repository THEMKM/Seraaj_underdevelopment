"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxButton, PxInput, PxChip, PxCard } from '../ui';

export interface SearchFilters {
  query: string;
  location: string;
  causes: string[];
  skills: string[];
  timeCommitment: string[];
  type: string[];
  remote: boolean;
  sortBy: 'relevance' | 'date' | 'match-score' | 'time-commitment';
  datePosted: 'any' | 'today' | 'week' | 'month';
}

interface AdvancedSearchProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onSearch: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  filters,
  onFiltersChange,
  onSearch,
  isOpen,
  onToggle
}) => {
  const { t } = useLanguage();

  const causes = [
    'Education', 'Health', 'Environment', 'Poverty', 'Human Rights',
    'Refugees', 'Women Empowerment', 'Youth Development', 'Elderly Care',
    'Disability Support', 'Mental Health', 'Community Development',
    'Food Security', 'Water & Sanitation', 'Technology for Good'
  ];

  const skills = [
    'Teaching', 'Mentoring', 'Social Media', 'Graphic Design', 'Writing',
    'Photography', 'Video Editing', 'Web Development', 'Marketing',
    'Project Management', 'Event Planning', 'Fundraising', 'Public Speaking',
    'Translation', 'Data Analysis', 'Research', 'Healthcare', 'Counseling'
  ];

  const timeCommitments = [
    '1-2 hours/week', '3-5 hours/week', '6-10 hours/week', '10+ hours/week',
    'One-time event', 'Flexible schedule', 'Weekends only', 'Evenings only'
  ];

  const opportunityTypes = [
    'Direct Service', 'Advocacy', 'Research', 'Capacity Building',
    'Emergency Response', 'Policy Work', 'Creative Projects',
    'Technology Solutions', 'Community Outreach', 'Training & Workshops'
  ];

  const locations = [
    'Amman, Jordan', 'Beirut, Lebanon', 'Cairo, Egypt', 'Dubai, UAE',
    'Riyadh, Saudi Arabia', 'Baghdad, Iraq', 'Kuwait City, Kuwait',
    'Doha, Qatar', 'Manama, Bahrain', 'Muscat, Oman'
  ];

  const updateFilter = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const toggleArrayFilter = (key: 'causes' | 'skills' | 'timeCommitment' | 'type', value: string) => {
    const current = filters[key];
    const updated = current.includes(value)
      ? current.filter(item => item !== value)
      : [...current, value];
    updateFilter(key, updated);
  };

  const clearAllFilters = () => {
    onFiltersChange({
      query: '',
      location: '',
      causes: [],
      skills: [],
      timeCommitment: [],
      type: [],
      remote: false,
      sortBy: 'relevance',
      datePosted: 'any'
    });
  };

  const activeFiltersCount = 
    (filters.location ? 1 : 0) +
    filters.causes.length +
    filters.skills.length +
    filters.timeCommitment.length +
    filters.type.length +
    (filters.remote ? 1 : 0) +
    (filters.sortBy !== 'relevance' ? 1 : 0) +
    (filters.datePosted !== 'any' ? 1 : 0);

  return (
    <div className="space-y-4">
      {/* Search Bar with Toggle */}
      <div className="flex gap-3">
        <div className="flex-1">
          <PxInput
            value={filters.query}
            onChange={(e) => updateFilter('query', e.target.value)}
            placeholder={t('search.placeholder')}
            className="text-lg"
          />
        </div>
        <PxButton
          variant="secondary"
          onClick={onToggle}
          className="flex items-center gap-2"
        >
          🔍 {t('search.filters')}
          {activeFiltersCount > 0 && (
            <span className="bg-primary dark:bg-neon-cyan text-ink dark:text-dark-bg text-xs font-pixel px-2 py-1 rounded">
              {activeFiltersCount}
            </span>
          )}
        </PxButton>
        <PxButton
          variant="primary"
          onClick={onSearch}
          className="hover:shadow-px-glow"
        >
          {t('search.search')}
        </PxButton>
      </div>

      {/* Advanced Filters Panel */}
      {isOpen && (
        <PxCard className="p-6 space-y-6 bg-white dark:bg-dark-surface animate-px-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-pixel text-ink dark:text-white">
              {t('search.advanced.title')}
            </h3>
            {activeFiltersCount > 0 && (
              <PxButton variant="secondary" size="sm" onClick={clearAllFilters}>
                {t('search.clearAll')}
              </PxButton>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Location & Basic Filters */}
            <div className="space-y-4">
              {/* Location */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                  {t('search.location')}
                </label>
                <select
                  value={filters.location}
                  onChange={(e) => updateFilter('location', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
                >
                  <option value="">{t('search.anyLocation')}</option>
                  {locations.map(location => (
                    <option key={location} value={location}>{location}</option>
                  ))}
                </select>
              </div>

              {/* Remote Work */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="remote"
                  checked={filters.remote}
                  onChange={(e) => updateFilter('remote', e.target.checked)}
                  className="w-4 h-4 text-primary bg-white border-2 border-ink rounded focus:ring-primary dark:focus:ring-neon-cyan dark:bg-dark-surface dark:border-dark-border"
                />
                <label htmlFor="remote" className="ml-2 text-sm font-pixel text-ink dark:text-white">
                  {t('search.remoteWork')}
                </label>
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                  {t('search.sortBy')}
                </label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => updateFilter('sortBy', e.target.value as SearchFilters['sortBy'])}
                  className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
                >
                  <option value="relevance">{t('search.sort.relevance')}</option>
                  <option value="date">{t('search.sort.date')}</option>
                  <option value="match-score">{t('search.sort.matchScore')}</option>
                  <option value="time-commitment">{t('search.sort.timeCommitment')}</option>
                </select>
              </div>

              {/* Date Posted */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-2">
                  {t('search.datePosted')}
                </label>
                <select
                  value={filters.datePosted}
                  onChange={(e) => updateFilter('datePosted', e.target.value as SearchFilters['datePosted'])}
                  className="w-full px-4 py-3 border-2 border-ink dark:border-dark-border rounded-lg bg-white dark:bg-dark-surface text-ink dark:text-white font-body focus:ring-2 focus:ring-primary dark:focus:ring-neon-cyan focus:border-transparent transition-all duration-300"
                >
                  <option value="any">{t('search.date.any')}</option>
                  <option value="today">{t('search.date.today')}</option>
                  <option value="week">{t('search.date.week')}</option>
                  <option value="month">{t('search.date.month')}</option>
                </select>
              </div>
            </div>

            {/* Chip Filters */}
            <div className="space-y-4">
              {/* Causes */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
                  {t('search.causes')}
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {causes.map(cause => (
                    <PxChip
                      key={cause}
                      variant={filters.causes.includes(cause) ? 'selected' : 'default'}
                      onClick={() => toggleArrayFilter('causes', cause)}
                      className="cursor-pointer"
                      size="sm"
                    >
                      {cause}
                    </PxChip>
                  ))}
                </div>
              </div>

              {/* Skills */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
                  {t('search.skills')}
                </label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {skills.map(skill => (
                    <PxChip
                      key={skill}
                      variant={filters.skills.includes(skill) ? 'selected' : 'default'}
                      onClick={() => toggleArrayFilter('skills', skill)}
                      className="cursor-pointer"
                      size="sm"
                    >
                      {skill}
                    </PxChip>
                  ))}
                </div>
              </div>

              {/* Time Commitment */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
                  {t('search.timeCommitment')}
                </label>
                <div className="flex flex-wrap gap-2">
                  {timeCommitments.map(time => (
                    <PxChip
                      key={time}
                      variant={filters.timeCommitment.includes(time) ? 'selected' : 'default'}
                      onClick={() => toggleArrayFilter('timeCommitment', time)}
                      className="cursor-pointer"
                      size="sm"
                    >
                      {time}
                    </PxChip>
                  ))}
                </div>
              </div>

              {/* Opportunity Type */}
              <div>
                <label className="block text-sm font-pixel text-ink dark:text-white mb-3">
                  {t('search.opportunityType')}
                </label>
                <div className="flex flex-wrap gap-2">
                  {opportunityTypes.map(type => (
                    <PxChip
                      key={type}
                      variant={filters.type.includes(type) ? 'selected' : 'default'}
                      onClick={() => toggleArrayFilter('type', type)}
                      className="cursor-pointer"
                      size="sm"
                    >
                      {type}
                    </PxChip>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-ink/20 dark:border-dark-border">
            <div className="text-sm text-ink dark:text-gray-400">
              {activeFiltersCount === 0 
                ? t('search.noFilters')
                : t('search.activeFilters', { count: activeFiltersCount })
              }
            </div>
            <div className="flex gap-3">
              <PxButton variant="secondary" onClick={onToggle}>
                {t('common.close')}
              </PxButton>
              <PxButton 
                variant="primary" 
                onClick={() => { onSearch(); onToggle(); }}
                className="hover:shadow-px-glow"
              >
                {t('search.applyFilters')}
              </PxButton>
            </div>
          </div>
        </PxCard>
      )}
    </div>
  );
};