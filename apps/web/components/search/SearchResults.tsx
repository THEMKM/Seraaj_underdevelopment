"use client";

import React from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxCard, PxChip, PxBadge, PxButton, PxSkeletonCard } from '../ui';
import { SearchFilters } from './AdvancedSearch';

export interface Opportunity {
  id: number;
  title: string;
  organization: string;
  location: string;
  remote: boolean;
  timeCommitment: string;
  causes: string[];
  skills: string[];
  type: string[];
  matchScore: number;
  description: string;
  datePosted: string;
  urgency: 'low' | 'medium' | 'high';
  applicants: number;
  featured: boolean;
}

interface SearchResultsProps {
  opportunities: Opportunity[];
  isLoading: boolean;
  filters: SearchFilters;
  totalResults: number;
  onApply: (opportunityId: number) => void;
  onSave: (opportunityId: number) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  opportunities,
  isLoading,
  filters,
  totalResults,
  onApply,
  onSave,
  onLoadMore,
  hasMore = false
}) => {
  const { t } = useLanguage();

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case 'high': return <PxBadge variant="error" size="sm">🔥 {t('search.urgency.high')}</PxBadge>;
      case 'medium': return <PxBadge variant="warning" size="sm">⚡ {t('search.urgency.medium')}</PxBadge>;
      default: return null;
    }
  };

  const formatDatePosted = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return t('search.posted.today');
    if (diffDays <= 7) return t('search.posted.days', { days: diffDays });
    if (diffDays <= 30) return t('search.posted.weeks', { weeks: Math.ceil(diffDays / 7) });
    return t('search.posted.months', { months: Math.ceil(diffDays / 30) });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 3 }).map((_, index) => (
          <PxSkeletonCard key={index} />
        ))}
      </div>
    );
  }

  if (opportunities.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 dark:bg-dark-border rounded-lg flex items-center justify-center">
          <span className="text-4xl">🔍</span>
        </div>
        <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
          {t('search.noResults.title')}
        </h3>
        <p className="text-ink dark:text-gray-300 mb-6">
          {filters.query 
            ? t('search.noResults.withQuery', { query: filters.query })
            : t('search.noResults.general')
          }
        </p>
        <div className="space-y-2 text-sm text-ink dark:text-gray-400">
          <p>• {t('search.noResults.tip1')}</p>
          <p>• {t('search.noResults.tip2')}</p>
          <p>• {t('search.noResults.tip3')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-pixel text-ink dark:text-white">
            {t('search.results.found', { count: totalResults })}
          </h3>
          {filters.query && (
            <p className="text-sm text-ink dark:text-gray-400">
              {t('search.results.for')} "{filters.query}"
            </p>
          )}
        </div>
        <div className="text-sm text-ink dark:text-gray-400">
          {t('search.sortedBy')} {t(`search.sort.${filters.sortBy}`)}
        </div>
      </div>

      {/* Opportunities List */}
      <div className="space-y-4">
        {opportunities.map((opportunity) => (
          <PxCard 
            key={opportunity.id} 
            className={`p-6 hover:shadow-px-glow transition-all duration-300 dark:bg-dark-surface dark:border-dark-border ${
              opportunity.featured ? 'ring-2 ring-primary dark:ring-neon-cyan' : ''
            }`}
          >
            <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
              {/* Main Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="text-xl font-pixel text-ink dark:text-white">
                        {opportunity.title}
                      </h4>
                      {opportunity.featured && (
                        <PxBadge variant="premium" size="sm">⭐ {t('search.featured')}</PxBadge>
                      )}
                      {getUrgencyBadge(opportunity.urgency)}
                    </div>
                    <p className="text-ink dark:text-gray-300">
                      <span className="font-semibold">{opportunity.organization}</span> • 
                      {opportunity.remote ? (
                        <span className="ml-1">🌐 {t('search.remote')}</span>
                      ) : (
                        <span className="ml-1">{opportunity.location}</span>
                      )}
                    </p>
                  </div>
                </div>

                <p className="text-ink dark:text-gray-300 mb-4 leading-relaxed">
                  {opportunity.description}
                </p>

                {/* Tags */}
                <div className="space-y-3 mb-4">
                  {/* Causes */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-pixel text-ink dark:text-gray-400">
                      {t('search.causes')}:
                    </span>
                    {opportunity.causes.map((cause) => (
                      <PxChip key={cause} size="sm" variant="selected">
                        {cause}
                      </PxChip>
                    ))}
                  </div>

                  {/* Skills */}
                  {opportunity.skills.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-pixel text-ink dark:text-gray-400">
                        {t('search.skills')}:
                      </span>
                      {opportunity.skills.slice(0, 3).map((skill) => (
                        <PxChip key={skill} size="sm">
                          {skill}
                        </PxChip>
                      ))}
                      {opportunity.skills.length > 3 && (
                        <PxChip size="sm">
                          +{opportunity.skills.length - 3} {t('common.more')}
                        </PxChip>
                      )}
                    </div>
                  )}

                  {/* Type */}
                  {opportunity.type.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-pixel text-ink dark:text-gray-400">
                        {t('search.type')}:
                      </span>
                      {opportunity.type.map((type) => (
                        <PxChip key={type} size="sm" variant="default">
                          {type}
                        </PxChip>
                      ))}
                    </div>
                  )}
                </div>

                {/* Meta Info */}
                <div className="flex items-center gap-4 text-sm text-ink dark:text-gray-400">
                  <span>⏰ {opportunity.timeCommitment}</span>
                  <span>📅 {formatDatePosted(opportunity.datePosted)}</span>
                  <span>👥 {t('search.applicants', { count: opportunity.applicants })}</span>
                </div>
              </div>

              {/* Right Side - Match Score & Actions */}
              <div className="flex flex-col items-end gap-4">
                <div className="text-center">
                  <PxBadge 
                    variant={opportunity.matchScore >= 90 ? 'premium' : opportunity.matchScore >= 70 ? 'success' : 'info'}
                    animated={opportunity.matchScore >= 90}
                    className="mb-2"
                  >
                    {opportunity.matchScore}% {t('search.match')}
                  </PxBadge>
                  <p className="text-xs text-ink dark:text-gray-400">
                    {t('search.compatibility')}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 w-full lg:w-auto">
                  <PxButton 
                    variant="primary" 
                    size="sm"
                    onClick={() => onApply(opportunity.id)}
                    className="hover:shadow-px-glow w-full lg:w-auto"
                  >
                    {t('search.apply')}
                  </PxButton>
                  <PxButton 
                    variant="secondary" 
                    size="sm"
                    onClick={() => onSave(opportunity.id)}
                    className="w-full lg:w-auto"
                  >
                    💾 {t('search.save')}
                  </PxButton>
                </div>
              </div>
            </div>
          </PxCard>
        ))}
      </div>

      {/* Load More */}
      {hasMore && onLoadMore && (
        <div className="text-center pt-6">
          <PxButton 
            variant="secondary" 
            size="lg"
            onClick={onLoadMore}
            disabled={isLoading}
          >
            {isLoading ? t('search.loading') : t('search.loadMore')}
          </PxButton>
        </div>
      )}
    </div>
  );
};