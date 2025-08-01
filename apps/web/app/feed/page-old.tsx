"use client";

import { PxButton, PxCard, PxChip, PxSwipeCard, PxBadge, PxSkeletonCard } from "../../components/ui";
import { AppLayout } from "../../components/layout/AppLayout";
import { LiveActivityFeed } from "../../components/feed/LiveActivityFeed";
import { useLanguage } from "../../contexts/LanguageContext";
import { useWebSocket } from "../../contexts/WebSocketContext";
import { useState, useEffect } from "react";

// Mock data for demonstration
const mockOpportunities = [
  {
    id: 1,
    title: "English Tutor for Refugee Children",
    organization: "Hope Foundation",
    location: "Amman, Jordan",
    timeCommitment: "4 hours/week",
    causes: ["Education", "Refugees"],
    skills: ["Teaching", "English", "Patience"],
    matchScore: 95,
    description: "Help refugee children improve their English skills through one-on-one tutoring sessions."
  },
  {
    id: 2,
    title: "Social Media Manager",
    organization: "Green Lebanon",
    location: "Beirut, Lebanon",
    timeCommitment: "6 hours/week",
    causes: ["Environment", "Awareness"],
    skills: ["Social Media", "Content Creation", "Arabic"],
    matchScore: 87,
    description: "Create engaging content to raise awareness about environmental issues in Lebanon."
  },
  {
    id: 3,
    title: "Community Health Educator",
    organization: "Cairo Medical Aid",
    location: "Cairo, Egypt",
    timeCommitment: "8 hours/week",
    causes: ["Health", "Community"],
    skills: ["Public Health", "Arabic", "Presentation"],
    matchScore: 82,
    description: "Conduct health education workshops in underserved communities."
  }
];

export default function FeedPage() {
  const { t } = useLanguage();
  const { connect, isConnected } = useWebSocket();
  const [viewMode, setViewMode] = useState<'cards' | 'swipe'>('cards');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // WebSocket will auto-connect when user is authenticated
    // No manual connection needed
  }, []);

  const handleApply = (opportunityId: number) => {
    console.log("Apply to opportunity:", opportunityId);
    // Redirect to application page
    window.location.href = `/opportunities/${opportunityId}/apply`;
  };

  const handleSwipeRight = (opportunity: any) => {
    console.log("Liked opportunity:", opportunity.title);
    handleApply(opportunity.id);
  };

  const handleSwipeLeft = (opportunity: any) => {
    console.log("Passed on opportunity:", opportunity.title);
  };

  const handleSwipeUp = (opportunity: any) => {
    console.log("Super liked opportunity:", opportunity.title);
    handleApply(opportunity.id);
  };

  return (
    <AppLayout userType="volunteer">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Feed Content */}
          <div className="lg:col-span-3 space-y-6">
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div>
              <h2 className="text-2xl md:text-3xl font-pixel text-ink dark:text-white mb-2">
                {t('feed.title')}
              </h2>
              <p className="text-ink dark:text-gray-300 leading-relaxed">
                {t('feed.subtitle')}
              </p>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex items-center gap-2">
              <PxButton
                variant={viewMode === 'cards' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setViewMode('cards')}
              >
                {t('feed.view.cards')}
              </PxButton>
              <PxButton
                variant={viewMode === 'swipe' ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setViewMode('swipe')}
              >
                {t('feed.view.swipe')}
              </PxButton>
            </div>
          </div>
          
          {/* Stats */}
          <div className="flex gap-4 text-sm">
            <PxBadge variant="success">
              {mockOpportunities.length} {t('feed.badge.matches')}
            </PxBadge>
            <PxBadge variant="info">
              3 {t('feed.badge.pending')}
            </PxBadge>
          </div>
        </div>

        {/* Content based on view mode */}
        {viewMode === 'swipe' ? (
          /* Swipe Mode */
          <div className="max-w-md mx-auto">
            {mockOpportunities.slice(0, 1).map((opportunity) => (
              <PxSwipeCard
                key={opportunity.id}
                onSwipeLeft={() => handleSwipeLeft(opportunity)}
                onSwipeRight={() => handleSwipeRight(opportunity)}
                onSwipeUp={() => handleSwipeUp(opportunity)}
                className="mb-8"
              >
                <div className="p-6">
                  <div className="text-center mb-4">
                    <PxBadge 
                      variant="premium" 
                      animated 
                      className="mb-2"
                    >
                      {opportunity.matchScore}% {t('feed.match')}
                    </PxBadge>
                    <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
                      {opportunity.title}
                    </h3>
                    <p className="text-ink dark:text-gray-300">
                      <span className="font-semibold">{opportunity.organization}</span> • {opportunity.location}
                    </p>
                  </div>

                  <p className="text-ink dark:text-gray-300 mb-4 leading-relaxed text-center">
                    {opportunity.description}
                  </p>

                  <div className="text-center mb-4">
                    <div className="flex flex-wrap gap-2 justify-center mb-3">
                      {opportunity.causes.map((cause) => (
                        <PxChip key={cause} size="sm" variant="selected">
                          {cause}
                        </PxChip>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {opportunity.skills.map((skill) => (
                        <PxChip key={skill} size="sm">
                          {skill}
                        </PxChip>
                      ))}
                    </div>
                  </div>

                  <div className="text-center text-sm text-gray-500">
                    {opportunity.timeCommitment}
                  </div>
                </div>
              </PxSwipeCard>
            ))}
          </div>
        ) : (
          /* Cards Mode */
          <div className="space-y-6">
            {isLoading ? (
              /* Loading State */
              Array.from({ length: 3 }).map((_, index) => (
                <PxSkeletonCard key={index} />
              ))
            ) : (
              mockOpportunities.map((opportunity) => (
                <PxCard key={opportunity.id} className="p-6 hover:shadow-px-glow transition-all duration-300 dark:bg-dark-surface dark:border-dark-border">
                  <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4 mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
                        {opportunity.title}
                      </h3>
                      <p className="text-ink dark:text-gray-300 mb-2">
                        <span className="font-semibold">{opportunity.organization}</span> • {opportunity.location}
                      </p>
                    </div>
                    <div className="text-right">
                      <PxBadge 
                        variant={opportunity.matchScore >= 90 ? 'premium' : 'success'}
                        animated={opportunity.matchScore >= 90}
                        className="mb-2"
                      >
                        {opportunity.matchScore}% MATCH
                      </PxBadge>
                      <p className="text-sm text-ink dark:text-gray-400">{opportunity.timeCommitment}</p>
                    </div>
                  </div>

                  <p className="text-ink dark:text-gray-300 mb-4 leading-relaxed">
                    {opportunity.description}
                  </p>

                  {/* Causes */}
                  <div className="mb-4">
                    <span className="text-sm font-pixel text-ink dark:text-gray-400 mr-2">{t('feed.causes')}</span>
                    <div className="inline-flex gap-2 flex-wrap">
                      {opportunity.causes.map((cause) => (
                        <PxChip key={cause} size="sm" variant="selected">
                          {cause}
                        </PxChip>
                      ))}
                    </div>
                  </div>

                  {/* Skills */}
                  <div className="mb-6">
                    <span className="text-sm font-pixel text-ink dark:text-gray-400 mr-2">{t('feed.skills')}</span>
                    <div className="inline-flex gap-2 flex-wrap">
                      {opportunity.skills.map((skill) => (
                        <PxChip key={skill} size="sm">
                          {skill}
                        </PxChip>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col sm:flex-row gap-3">
                    <PxButton 
                      variant="primary" 
                      onClick={() => handleApply(opportunity.id)}
                      className="hover:shadow-px-glow"
                    >
                      {t('feed.apply')}
                    </PxButton>
                    <PxButton variant="secondary">
                      {t('feed.learn')}
                    </PxButton>
                    <PxButton variant="secondary">
                      {t('feed.save')}
                    </PxButton>
                  </div>
                </PxCard>
              ))
            )}
          </div>
        )}

        {/* Load More */}
        <div className="text-center mt-8">
          <PxButton 
            variant="secondary" 
            size="lg"
            onClick={() => setIsLoading(true)}
            disabled={isLoading}
          >
            {isLoading ? t('feed.loading') : t('feed.load')}
          </PxButton>
            </div>
          </div>
          
          {/* Sidebar - Activity Feed */}
          <div className="lg:col-span-1">
            <LiveActivityFeed maxItems={8} />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}