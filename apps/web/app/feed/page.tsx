"use client";

import { PxButton, PxCard, PxChip, PxSwipeCard, PxBadge, PxSkeletonCard } from "../../components/ui";
import { AppLayout } from "../../components/layout/AppLayout";
import { LiveActivityFeed } from "../../components/feed/LiveActivityFeed";
import { useLanguage } from "../../contexts/LanguageContext";
import { useAuth } from "../../contexts/AuthContext";
import { useWebSocket } from "../../contexts/WebSocketContext";
import { useState, useEffect } from "react";
import { opportunities, Opportunity } from "../../lib/api";

export default function FeedPage() {
  const { t } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const { isConnected } = useWebSocket();
  
  const [currentOpportunities, setCurrentOpportunities] = useState<Opportunity[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [viewMode, setViewMode] = useState<'swipe' | 'list'>('swipe');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    remote: false,
    skills: [] as string[],
    search: ''
  });

  // Fetch opportunities on component mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchOpportunities();
    }
  }, [isAuthenticated, filters]);

  const fetchOpportunities = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await opportunities.getAll({
        ...filters,
        limit: 20
      });
      
      if (response.success && response.data) {
        setCurrentOpportunities(response.data);
        setCurrentIndex(0);
      } else {
        setError(response.error || 'Failed to load opportunities');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Error fetching opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (direction: 'left' | 'right') => {
    const currentOpp = currentOpportunities[currentIndex];
    
    if (direction === 'right' && currentOpp) {
      // User is interested - could save to favorites or apply
      try {
        console.log('User interested in:', currentOpp.title);
        // Optionally apply or save
        // await opportunities.apply(currentOpp.id);
      } catch (err) {
        console.error('Error handling interest:', err);
      }
    }
    
    // Move to next opportunity
    if (currentIndex < currentOpportunities.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      // Load more opportunities or show completion
      await fetchOpportunities();
    }
  };

  const handleApply = async (opportunityId: string) => {
    try {
      const response = await opportunities.apply(opportunityId);
      if (response.success) {
        // Show success message
        console.log('Application submitted successfully');
        // Move to next opportunity
        handleSwipe('right');
      } else {
        setError(response.error || 'Failed to apply');
      }
    } catch (err) {
      setError('Failed to submit application');
      console.error('Error applying:', err);
    }
  };

  // Show loading state for unauthenticated users
  if (!isAuthenticated) {
    return (
      <AppLayout userType="volunteer">
        <div className="max-w-4xl mx-auto px-4 py-8 text-center">
          <PxCard className="p-8">
            <h2 className="text-2xl font-pixel text-ink dark:text-white mb-4">
              Please Login
            </h2>
            <p className="text-ink dark:text-gray-400 mb-6">
              You need to be logged in to view opportunities.
            </p>
            <PxButton 
              variant="primary"
              onClick={() => window.location.href = '/auth/login'}
            >
              Login
            </PxButton>
          </PxCard>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout userType={user?.role?.toLowerCase() || "volunteer"}>
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
              {t('feed.title')} ✨
            </h1>
            <p className="text-ink dark:text-gray-400">
              {t('feed.subtitle')} {currentOpportunities.length} opportunities available
            </p>
            <div className="flex items-center gap-2 mt-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-xs text-ink dark:text-gray-400">
                {isConnected ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <PxButton
              variant={viewMode === 'swipe' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setViewMode('swipe')}
            >
              🃏 SWIPE
            </PxButton>
            <PxButton
              variant={viewMode === 'list' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              📋 LIST
            </PxButton>
            <PxButton
              variant="outline"
              size="sm"
              onClick={() => fetchOpportunities()}
              disabled={loading}
            >
              🔄 REFRESH
            </PxButton>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-3">
            <PxButton
              variant={filters.remote ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilters(prev => ({ ...prev, remote: !prev.remote }))}
            >
              🌐 Remote Only
            </PxButton>
            <input
              type="text"
              placeholder="Search opportunities..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="px-3 py-1 border border-ink dark:border-dark-border rounded text-sm"
            />
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6">
            <PxCard className="p-4 bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800">
              <p className="text-red-700 dark:text-red-300">
                ⚠️ {error}
              </p>
              <PxButton
                variant="outline"
                size="sm"
                onClick={() => fetchOpportunities()}
                className="mt-2"
              >
                Try Again
              </PxButton>
            </PxCard>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Feed */}
          <div className="lg:col-span-2">
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <PxSkeletonCard key={i} />
                ))}
              </div>
            ) : currentOpportunities.length === 0 ? (
              <PxCard className="p-8 text-center">
                <h3 className="text-xl font-pixel text-ink dark:text-white mb-4">
                  No Opportunities Found
                </h3>
                <p className="text-ink dark:text-gray-400 mb-6">
                  Try adjusting your filters or check back later for new opportunities.
                </p>
                <PxButton
                  variant="primary"
                  onClick={() => fetchOpportunities()}
                >
                  Refresh
                </PxButton>
              </PxCard>
            ) : viewMode === 'swipe' ? (
              // Swipe Mode
              <div className="relative h-96">
                {currentOpportunities.slice(currentIndex, currentIndex + 2).map((opportunity, index) => (
                  <PxSwipeCard
                    key={opportunity.id}
                    className={`absolute inset-0 ${index === 1 ? 'z-0 scale-95' : 'z-10'}`}
                    onSwipe={handleSwipe}
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
                            {opportunity.title}
                          </h3>
                          <p className="text-sm text-ink dark:text-gray-400">
                            Organization • {opportunity.is_remote ? 'Remote' : 'On-site'}
                          </p>
                        </div>
                        <PxBadge variant="success" size="sm">
                          {opportunity.status}
                        </PxBadge>
                      </div>
                      
                      <p className="text-ink dark:text-gray-300 mb-4 line-clamp-3">
                        {opportunity.description}
                      </p>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        {opportunity.skills_required.slice(0, 3).map((skill) => (
                          <PxChip key={skill} size="sm">
                            {skill}
                          </PxChip>
                        ))}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-ink dark:text-gray-400">
                          <p>{opportunity.min_hours} hours minimum</p>
                          <p>{opportunity.start_date} - {opportunity.end_date}</p>
                        </div>
                        
                        <div className="flex gap-2">
                          <PxButton
                            variant="outline"
                            size="sm"
                            onClick={() => handleSwipe('left')}
                          >
                            ⏭️ SKIP
                          </PxButton>
                          <PxButton
                            variant="primary"
                            size="sm"
                            onClick={() => handleApply(opportunity.id)}
                          >
                            ✨ APPLY
                          </PxButton>
                        </div>
                      </div>
                    </div>
                  </PxSwipeCard>
                ))}
              </div>
            ) : (
              // List Mode
              <div className="space-y-4">
                {currentOpportunities.map((opportunity) => (
                  <PxCard key={opportunity.id} className="p-6 hover:shadow-px-glow transition-all duration-300">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-pixel text-ink dark:text-white mb-2">
                          {opportunity.title}
                        </h3>
                        <p className="text-sm text-ink dark:text-gray-400">
                          Organization • {opportunity.is_remote ? 'Remote' : 'On-site'}
                        </p>
                      </div>
                      <PxBadge variant="success" size="sm">
                        {opportunity.status}
                      </PxBadge>
                    </div>
                    
                    <p className="text-ink dark:text-gray-300 mb-4">
                      {opportunity.description}
                    </p>
                    
                    <div className="flex flex-wrap gap-2 mb-4">
                      {opportunity.skills_required.map((skill) => (
                        <PxChip key={skill} size="sm">
                          {skill}
                        </PxChip>
                      ))}
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-ink dark:text-gray-400">
                        <p>{opportunity.min_hours} hours minimum</p>
                        <p>{opportunity.start_date} - {opportunity.end_date}</p>
                      </div>
                      
                      <PxButton
                        variant="primary"
                        size="sm"
                        onClick={() => handleApply(opportunity.id)}
                      >
                        ✨ APPLY
                      </PxButton>
                    </div>
                  </PxCard>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <LiveActivityFeed />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}