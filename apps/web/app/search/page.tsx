"use client";

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { AppLayout } from '../../components/layout/AppLayout';
import { AdvancedSearch, SearchFilters } from '../../components/search/AdvancedSearch';
import { SearchResults, Opportunity } from '../../components/search/SearchResults';
import { SavedSearches, SavedSearch } from '../../components/search/SavedSearches';
import { useLanguage } from '../../contexts/LanguageContext';

// Mock data for demonstration
const mockOpportunities: Opportunity[] = [
  {
    id: 1,
    title: "English Tutor for Refugee Children",
    organization: "Hope Foundation",
    location: "Amman, Jordan",
    remote: false,
    timeCommitment: "4 hours/week",
    causes: ["Education", "Refugees"],
    skills: ["Teaching", "English", "Patience"],
    type: ["Direct Service", "Training & Workshops"],
    matchScore: 95,
    description: "Help refugee children improve their English skills through one-on-one tutoring sessions. Make a direct impact on their educational journey and future opportunities.",
    datePosted: "2024-01-20",
    urgency: "high",
    applicants: 12,
    featured: true
  },
  {
    id: 2,
    title: "Social Media Manager for Environmental Campaign",
    organization: "Green Lebanon Initiative",
    location: "Beirut, Lebanon",
    remote: true,
    timeCommitment: "6 hours/week",
    causes: ["Environment", "Awareness"],
    skills: ["Social Media", "Content Creation", "Arabic"],
    type: ["Creative Projects", "Advocacy"],
    matchScore: 87,
    description: "Create engaging content to raise awareness about environmental issues in Lebanon. Help us reach wider audiences through creative digital campaigns.",
    datePosted: "2024-01-18",
    urgency: "medium",
    applicants: 8,
    featured: false
  },
  {
    id: 3,
    title: "Community Health Educator",
    organization: "Cairo Medical Aid",
    location: "Cairo, Egypt",
    remote: false,
    timeCommitment: "8 hours/week",
    causes: ["Health", "Community Development"],
    skills: ["Public Health", "Arabic", "Presentation"],
    type: ["Direct Service", "Community Outreach"],
    matchScore: 82,
    description: "Conduct health education workshops in underserved communities. Train community members on basic health practices and disease prevention.",
    datePosted: "2024-01-15",
    urgency: "low",
    applicants: 15,
    featured: false
  },
  {
    id: 4,
    title: "Web Developer for NGO Platform",
    organization: "Tech for Good MENA",
    location: "Dubai, UAE",
    remote: true,
    timeCommitment: "10+ hours/week",
    causes: ["Technology for Good", "Community Development"],
    skills: ["Web Development", "React", "Node.js"],
    type: ["Technology Solutions", "Capacity Building"],
    matchScore: 78,
    description: "Help build a platform connecting NGOs with volunteers across the MENA region. Use your technical skills to amplify social impact.",
    datePosted: "2024-01-22",
    urgency: "medium",
    applicants: 6,
    featured: true
  },
  {
    id: 5,
    title: "Event Coordinator for Youth Program",
    organization: "Jordan Youth Network",
    location: "Amman, Jordan",
    remote: false,
    timeCommitment: "Flexible schedule",
    causes: ["Youth Development", "Education"],
    skills: ["Event Planning", "Project Management", "Arabic"],
    type: ["Event Planning", "Direct Service"],
    matchScore: 73,
    description: "Organize workshops and events for young people in Jordan. Help create memorable experiences that build skills and confidence.",
    datePosted: "2024-01-19",
    urgency: "low",
    applicants: 9,
    featured: false
  }
];

const initialFilters: SearchFilters = {
  query: '',
  location: '',
  causes: [],
  skills: [],
  timeCommitment: [],
  type: [],
  remote: false,
  sortBy: 'relevance',
  datePosted: 'any'
};

export default function SearchPage() {
  const { t } = useLanguage();
  const searchParams = useSearchParams();
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [filteredOpportunities, setFilteredOpportunities] = useState<Opportunity[]>(mockOpportunities);
  const [isLoading, setIsLoading] = useState(false);
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([
    {
      id: '1',
      name: 'Education in Amman',
      filters: { ...initialFilters, location: 'Amman, Jordan', causes: ['Education'] },
      alertEnabled: true,
      newResultsCount: 3,
      lastRun: '2024-01-21',
      created: '2024-01-15'
    },
    {
      id: '2',
      name: 'Remote Tech Opportunities',
      filters: { ...initialFilters, remote: true, skills: ['Web Development', 'Social Media'] },
      alertEnabled: false,
      newResultsCount: 0,
      lastRun: '2024-01-20',
      created: '2024-01-10'
    }
  ]);

  // Initialize filters from URL parameters
  useEffect(() => {
    const query = searchParams.get('q') || '';
    const cause = searchParams.get('cause') || '';
    
    if (query || cause) {
      setFilters(prev => ({
        ...prev,
        query,
        causes: cause ? [cause] : []
      }));
    }
  }, [searchParams]);

  // Filter and sort opportunities based on current filters
  const applyFilters = () => {
    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      let filtered = [...mockOpportunities];

      // Apply query filter
      if (filters.query.trim()) {
        const query = filters.query.toLowerCase();
        filtered = filtered.filter(opp => 
          opp.title.toLowerCase().includes(query) ||
          opp.organization.toLowerCase().includes(query) ||
          opp.description.toLowerCase().includes(query) ||
          opp.causes.some(cause => cause.toLowerCase().includes(query)) ||
          opp.skills.some(skill => skill.toLowerCase().includes(query))
        );
      }

      // Apply location filter
      if (filters.location) {
        filtered = filtered.filter(opp => opp.location === filters.location);
      }

      // Apply remote filter
      if (filters.remote) {
        filtered = filtered.filter(opp => opp.remote);
      }

      // Apply causes filter
      if (filters.causes.length > 0) {
        filtered = filtered.filter(opp => 
          filters.causes.some(cause => opp.causes.includes(cause))
        );
      }

      // Apply skills filter
      if (filters.skills.length > 0) {
        filtered = filtered.filter(opp => 
          filters.skills.some(skill => opp.skills.includes(skill))
        );
      }

      // Apply time commitment filter
      if (filters.timeCommitment.length > 0) {
        filtered = filtered.filter(opp => 
          filters.timeCommitment.includes(opp.timeCommitment)
        );
      }

      // Apply type filter
      if (filters.type.length > 0) {
        filtered = filtered.filter(opp => 
          filters.type.some(type => opp.type.includes(type))
        );
      }

      // Apply date filter
      if (filters.datePosted !== 'any') {
        const now = new Date();
        const cutoffDate = new Date();
        
        switch (filters.datePosted) {
          case 'today':
            cutoffDate.setDate(now.getDate() - 1);
            break;
          case 'week':
            cutoffDate.setDate(now.getDate() - 7);
            break;
          case 'month':
            cutoffDate.setMonth(now.getMonth() - 1);
            break;
        }
        
        filtered = filtered.filter(opp => new Date(opp.datePosted) >= cutoffDate);
      }

      // Apply sorting
      switch (filters.sortBy) {
        case 'date':
          filtered.sort((a, b) => new Date(b.datePosted).getTime() - new Date(a.datePosted).getTime());
          break;
        case 'match-score':
          filtered.sort((a, b) => b.matchScore - a.matchScore);
          break;
        case 'time-commitment':
          // Sort by time commitment (ascending)
          const timeOrder = ['1-2 hours/week', '3-5 hours/week', '6-10 hours/week', '10+ hours/week'];
          filtered.sort((a, b) => {
            const aIndex = timeOrder.indexOf(a.timeCommitment);
            const bIndex = timeOrder.indexOf(b.timeCommitment);
            return aIndex - bIndex;
          });
          break;
        default: // relevance
          filtered.sort((a, b) => b.matchScore - a.matchScore);
      }

      setFilteredOpportunities(filtered);
      setIsLoading(false);
    }, 800);
  };

  // Apply filters when they change
  useEffect(() => {
    applyFilters();
  }, [filters]);

  const handleApply = (opportunityId: number) => {
    console.log('Apply to opportunity:', opportunityId);
    // Redirect to application page or show application modal
    window.location.href = `/opportunities/${opportunityId}/apply`;
  };

  const handleSave = (opportunityId: number) => {
    console.log('Save opportunity:', opportunityId);
    // Add to saved opportunities - could use local storage or API
    const savedOpportunities = JSON.parse(localStorage.getItem('savedOpportunities') || '[]');
    if (!savedOpportunities.includes(opportunityId)) {
      savedOpportunities.push(opportunityId);
      localStorage.setItem('savedOpportunities', JSON.stringify(savedOpportunities));
      alert('Opportunity saved to your favorites!');
    } else {
      alert('Opportunity is already in your favorites!');
    }
  };

  const handleLoadSearch = (search: SavedSearch) => {
    setFilters(search.filters);
    // Update last run date
    setSavedSearches(prev => 
      prev.map(s => s.id === search.id 
        ? { ...s, lastRun: new Date().toISOString().split('T')[0], newResultsCount: 0 }
        : s
      )
    );
  };

  const handleSaveCurrentSearch = (name: string, searchFilters: SearchFilters) => {
    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name,
      filters: searchFilters,
      alertEnabled: false,
      newResultsCount: 0,
      lastRun: new Date().toISOString().split('T')[0],
      created: new Date().toISOString().split('T')[0]
    };
    setSavedSearches(prev => [...prev, newSearch]);
  };

  const handleDeleteSearch = (searchId: string) => {
    setSavedSearches(prev => prev.filter(s => s.id !== searchId));
  };

  const handleToggleAlert = (searchId: string, enabled: boolean) => {
    setSavedSearches(prev => 
      prev.map(s => s.id === searchId ? { ...s, alertEnabled: enabled } : s)
    );
  };

  return (
    <AppLayout userType="volunteer">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-pixel text-ink dark:text-white mb-2">
            {t('search.title', { fallback: 'SEARCH OPPORTUNITIES' })}
          </h1>
          <p className="text-ink dark:text-gray-300">
            {t('search.subtitle', { fallback: 'Find volunteer opportunities that match your interests and skills' })}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Saved Searches */}
          <div className="lg:col-span-1 space-y-6">
            <SavedSearches
              savedSearches={savedSearches}
              onLoadSearch={handleLoadSearch}
              onSaveCurrentSearch={handleSaveCurrentSearch}
              onDeleteSearch={handleDeleteSearch}
              onToggleAlert={handleToggleAlert}
              currentFilters={filters}
            />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Search Interface */}
            <AdvancedSearch
              filters={filters}
              onFiltersChange={setFilters}
              onSearch={applyFilters}
              isOpen={isAdvancedOpen}
              onToggle={() => setIsAdvancedOpen(!isAdvancedOpen)}
            />

            {/* Search Results */}
            <SearchResults
              opportunities={filteredOpportunities}
              isLoading={isLoading}
              filters={filters}
              totalResults={filteredOpportunities.length}
              onApply={handleApply}
              onSave={handleSave}
              hasMore={false}
            />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}