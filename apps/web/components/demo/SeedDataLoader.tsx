"use client";

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { PxCard, PxButton, PxBadge, PxProgress } from '../ui';
import { SEED_DATA, generateRandomId, getRandomItem, getRandomItems, generateRandomDate } from '../../lib/seedData';

interface SeedDataLoaderProps {
  onDataLoaded?: (data: any) => void;
  className?: string;
}

export const SeedDataLoader: React.FC<SeedDataLoaderProps> = ({ onDataLoaded, className }) => {
  const { t } = useLanguage();
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [loadedData, setLoadedData] = useState<any>(null);

  const seedSteps = [
    { key: 'organizations', label: 'Loading Organizations...', count: 50 },
    { key: 'volunteers', label: 'Creating Volunteer Profiles...', count: 200 },
    { key: 'opportunities', label: 'Generating Opportunities...', count: 150 },
    { key: 'applications', label: 'Simulating Applications...', count: 500 },
    { key: 'messages', label: 'Creating Conversations...', count: 300 },
    { key: 'analytics', label: 'Generating Analytics Data...', count: 1 }
  ];

  const generateExpandedOrganizations = () => {
    const baseOrgs = SEED_DATA.organizations;
    const expandedOrgs = [...baseOrgs];

    // Generate additional organizations
    for (let i = 0; i < 45; i++) {
      const country = getRandomItem(SEED_DATA.countries);
      const city = getRandomItem(SEED_DATA.cities[country.en] || [{ en: 'Capital', ar: 'العاصمة' }]);
      const causes = getRandomItems(SEED_DATA.causes, Math.floor(Math.random() * 3) + 1);
      
      const orgNames = [
        'Future Foundation', 'Unity Initiative', 'Progress Center', 
        'Community Bridge', 'Rising Hope', 'New Dawn', 'Bright Tomorrow',
        'Helping Hands', 'Golden Hearts', 'Open Doors', 'Strong Roots'
      ];
      
      const orgName = getRandomItem(orgNames);
      
      expandedOrgs.push({
        id: generateRandomId('org'),
        name: `${orgName} ${country.en}`,
        nameAr: `${orgName} ${country.ar}`,
        description: `Empowering communities through innovative programs and sustainable development initiatives in ${country.en}.`,
        descriptionAr: `تمكين المجتمعات من خلال البرامج المبتكرة ومبادرات التنمية المستدامة في ${country.ar}.`,
        logo: `/logos/org-${i + 6}.png`,
        website: `https://${orgName.toLowerCase().replace(' ', '')}.${country.en.toLowerCase()}`,
        email: `info@${orgName.toLowerCase().replace(' ', '')}.org`,
        location: city.en,
        locationAr: city.ar,
        country: country.en,
        countryAr: country.ar,
        causes: causes.map(c => c.en),
        established: 2010 + Math.floor(Math.random() * 12),
        teamSize: getRandomItem(['5-10', '10-25', '25-50', '50-100']),
        verified: Math.random() > 0.3,
        rating: 3.5 + Math.random() * 1.5,
        totalOpportunities: Math.floor(Math.random() * 50) + 10,
        activeOpportunities: Math.floor(Math.random() * 15) + 3,
        totalVolunteers: Math.floor(Math.random() * 200) + 50
      });
    }

    return expandedOrgs;
  };

  const generateExpandedVolunteers = () => {
    const baseVols = SEED_DATA.volunteers;
    const expandedVols = [...baseVols];

    const firstNames = [
      'Fatima', 'Ahmed', 'Layla', 'Omar', 'Zeinab', 'Hassan', 'Nour', 'Khalid',
      'Amira', 'Mohammad', 'Dina', 'Youssef', 'Rana', 'Ali', 'Salma', 'Karim'
    ];
    
    const lastNames = [
      'Al-Ahmad', 'Hassan', 'Al-Zahra', 'Mansour', 'Al-Rashid', 'Khalil',
      'Al-Nouri', 'Farouk', 'Al-Mahmoud', 'Taha', 'Al-Sharif', 'Nazir'
    ];

    for (let i = 0; i < 195; i++) {
      const country = getRandomItem(SEED_DATA.countries);
      const city = getRandomItem(SEED_DATA.cities[country.en] || [{ en: 'Capital', ar: 'العاصمة' }]);
      const firstName = getRandomItem(firstNames);
      const lastName = getRandomItem(lastNames);
      const skills = getRandomItems(SEED_DATA.skills, Math.floor(Math.random() * 4) + 2);
      const interests = getRandomItems(SEED_DATA.causes, Math.floor(Math.random() * 3) + 2);

      expandedVols.push({
        id: generateRandomId('vol'),
        name: `${firstName} ${lastName}`,
        nameAr: `${firstName} ${lastName}`,
        email: `${firstName.toLowerCase()}.${lastName.toLowerCase().replace('al-', '')}@example.com`,
        avatar: `/avatars/user-${i + 6}.jpg`,
        location: city.en,
        locationAr: city.ar,
        country: country.en,
        countryAr: country.ar,
        bio: `Passionate volunteer committed to making a positive impact in ${country.en} through community engagement.`,
        bioAr: `متطوع شغوف ملتزم بإحداث تأثير إيجابي في ${country.ar} من خلال المشاركة المجتمعية.`,
        skills: skills.map(s => s.en),
        interests: interests.map(i => i.en),
        languages: getRandomItems(['Arabic', 'English', 'French', 'Spanish'], Math.floor(Math.random() * 3) + 1),
        availability: getRandomItem(['full-time', 'part-time', 'weekends', 'flexible']),
        experience: getRandomItem(['beginner', 'intermediate', 'expert']),
        joinDate: generateRandomDate(365),
        completedOpportunities: Math.floor(Math.random() * 20),
        rating: 3.5 + Math.random() * 1.5,
        verified: Math.random() > 0.4
      });
    }

    return expandedVols;
  };

  const generateExpandedOpportunities = (organizations: any[]) => {
    const baseOpps = SEED_DATA.opportunities;
    const expandedOpps = [...baseOpps];

    const oppTitles = [
      'Community Outreach Coordinator', 'Digital Marketing Specialist', 'Youth Mentor',
      'Event Planning Assistant', 'Research Volunteer', 'Translation Services',
      'Photography Volunteer', 'Fundraising Campaign Manager', 'Workshop Facilitator',
      'Social Media Content Creator', 'Grant Writing Specialist', 'Program Assistant'
    ];

    for (let i = 0; i < 147; i++) {
      const org = getRandomItem(organizations);
      const title = getRandomItem(oppTitles);
      const causes = getRandomItems(SEED_DATA.causes, Math.floor(Math.random() * 2) + 1);
      const skills = getRandomItems(SEED_DATA.skills, Math.floor(Math.random() * 3) + 2);

      expandedOpps.push({
        id: generateRandomId('opp'),
        title: title,
        titleAr: title, // In production, would have proper Arabic translations
        description: `Join our team to make a meaningful impact through ${title.toLowerCase()} work with ${org.name}.`,
        descriptionAr: `انضم إلى فريقنا لإحداث تأثير ذي معنى من خلال عمل ${title} مع ${org.nameAr}.`,
        organizationId: org.id,
        organizationName: org.name,
        organizationLogo: org.logo,
        location: org.location,
        locationAr: org.locationAr,
        country: org.country,
        countryAr: org.countryAr,
        remote: Math.random() > 0.7,
        causes: causes.map(c => c.en),
        skillsRequired: skills.map(s => s.en),
        timeCommitment: getRandomItem(['2 hours/week', '4 hours/week', '6 hours/week', '8 hours/week']),
        duration: getRandomItem(['1 month', '3 months', '6 months', '12 months']),
        urgency: getRandomItem(['low', 'medium', 'high']),
        volunteersNeeded: Math.floor(Math.random() * 10) + 1,
        volunteersApplied: Math.floor(Math.random() * 25),
        volunteersAccepted: Math.floor(Math.random() * 8),
        status: getRandomItem(['active', 'active', 'active', 'filled', 'closed']), // Bias toward active
        postedDate: generateRandomDate(90),
        applicationDeadline: generateRandomDate(-30), // Future date
        startDate: generateRandomDate(-15), // Future date
        requirements: [
          'Strong communication skills',
          'Reliable and committed',
          'Team player mentality',
          'Relevant experience preferred'
        ],
        benefits: [
          'Professional development',
          'Networking opportunities',
          'Certificate of completion',
          'Transportation allowance'
        ],
        images: [`/opportunities/opp-${i + 4}-1.jpg`, `/opportunities/opp-${i + 4}-2.jpg`],
        featured: Math.random() > 0.8,
        verified: Math.random() > 0.2
      });
    }

    return expandedOpps;
  };

  const generateApplications = (volunteers: any[], opportunities: any[]) => {
    const applications = [];
    
    for (let i = 0; i < 500; i++) {
      const volunteer = getRandomItem(volunteers);
      const opportunity = getRandomItem(opportunities.filter(o => o.status === 'active'));
      
      applications.push({
        id: generateRandomId('app'),
        volunteerId: volunteer.id,
        opportunityId: opportunity.id,
        status: getRandomItem(['pending', 'accepted', 'rejected', 'withdrawn']),
        appliedDate: generateRandomDate(60),
        coverLetter: `I am excited to apply for this opportunity because...`,
        matchScore: 60 + Math.random() * 40,
        reviewedBy: opportunity.organizationId,
        reviewDate: generateRandomDate(30)
      });
    }

    return applications;
  };

  const generateMessages = (volunteers: any[], organizations: any[]) => {
    const conversations = [];
    const messages = [];

    for (let i = 0; i < 300; i++) {
      const volunteer = getRandomItem(volunteers);
      const org = getRandomItem(organizations);
      const conversationId = generateRandomId('conv');

      conversations.push({
        id: conversationId,
        participantIds: [volunteer.id, org.id],
        lastMessage: 'Thank you for your interest in volunteering with us!',
        lastMessageTime: generateRandomDate(7),
        unreadCount: Math.floor(Math.random() * 3),
        status: 'active'
      });

      // Generate 2-5 messages per conversation
      const messageCount = Math.floor(Math.random() * 4) + 2;
      for (let j = 0; j < messageCount; j++) {
        messages.push({
          id: generateRandomId('msg'),
          conversationId: conversationId,
          senderId: j % 2 === 0 ? volunteer.id : org.id,
          content: getRandomItem([
            'Hello, I\'m interested in learning more about this opportunity.',
            'Thank you for your application. We\'d like to schedule an interview.',
            'I have some questions about the time commitment.',
            'Great! I look forward to contributing to your mission.',
            'Could you tell me more about the training provided?'
          ]),
          timestamp: generateRandomDate(14),
          status: getRandomItem(['sent', 'delivered', 'read']),
          type: 'text'
        });
      }
    }

    return { conversations, messages };
  };

  const generateAnalyticsData = () => {
    return {
      userGrowth: Array.from({ length: 12 }, (_, i) => ({
        month: new Date(2023, i).toLocaleDateString('en', { month: 'short' }),
        volunteers: 100 + i * 50 + Math.floor(Math.random() * 100),
        organizations: 10 + i * 5 + Math.floor(Math.random() * 10)
      })),
      topSkills: SEED_DATA.skills.slice(0, 10).map(skill => ({
        skill: skill.en,
        count: Math.floor(Math.random() * 200) + 50,
        growth: Math.floor(Math.random() * 30) - 10
      })),
      regionStats: SEED_DATA.countries.map(country => ({
        country: country.en,
        volunteers: Math.floor(Math.random() * 500) + 100,
        organizations: Math.floor(Math.random() * 50) + 10,
        opportunities: Math.floor(Math.random() * 100) + 20
      }))
    };
  };

  const loadSeedData = async () => {
    setIsLoading(true);
    setProgress(0);
    
    try {
      for (let i = 0; i < seedSteps.length; i++) {
        const step = seedSteps[i];
        setCurrentStep(step.label);
        setProgress((i / seedSteps.length) * 100);

        // Simulate loading time
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

        // Generate data for each step
        let stepData;
        switch (step.key) {
          case 'organizations':
            stepData = generateExpandedOrganizations();
            break;
          case 'volunteers':
            stepData = generateExpandedVolunteers();
            break;
          case 'opportunities':
            stepData = generateExpandedOpportunities(loadedData?.organizations || SEED_DATA.organizations);
            break;
          case 'applications':
            stepData = generateApplications(
              loadedData?.volunteers || SEED_DATA.volunteers,
              loadedData?.opportunities || SEED_DATA.opportunities
            );
            break;
          case 'messages':
            stepData = generateMessages(
              loadedData?.volunteers || SEED_DATA.volunteers,
              loadedData?.organizations || SEED_DATA.organizations
            );
            break;
          case 'analytics':
            stepData = generateAnalyticsData();
            break;
        }

        setLoadedData(prev => ({ ...prev, [step.key]: stepData }));
      }

      setProgress(100);
      setCurrentStep('Demo data loaded successfully!');
      
      // Store in localStorage for persistence
      const finalData = {
        organizations: generateExpandedOrganizations(),
        volunteers: generateExpandedVolunteers(),
        opportunities: generateExpandedOpportunities(generateExpandedOrganizations()),
        applications: generateApplications(generateExpandedVolunteers(), generateExpandedOpportunities(generateExpandedOrganizations())),
        messages: generateMessages(generateExpandedVolunteers(), generateExpandedOrganizations()),
        analytics: generateAnalyticsData(),
        loadedAt: new Date().toISOString()
      };
      
      localStorage.setItem('seraaj_demo_data', JSON.stringify(finalData));
      setLoadedData(finalData);
      
      if (onDataLoaded) {
        onDataLoaded(finalData);
      }

    } catch (error) {
      // Error loading seed data handled by error state
      setCurrentStep('Error loading demo data');
    } finally {
      setIsLoading(false);
    }
  };

  const clearSeedData = () => {
    localStorage.removeItem('seraaj_demo_data');
    setLoadedData(null);
    setProgress(0);
    setCurrentStep('');
  };

  const existingData = localStorage.getItem('seraaj_demo_data');

  return (
    <div className={`space-y-6 ${className}`}>
      <PxCard className="p-6">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary dark:bg-neon-cyan rounded-lg flex items-center justify-center">
            <span className="text-3xl">🌱</span>
          </div>
          <h2 className="text-2xl font-pixel text-ink dark:text-white mb-2">
            {t('demo.seedData.title')}
          </h2>
          <p className="text-ink dark:text-gray-400 mb-6">
            {t('demo.seedData.description')}
          </p>

          {existingData && !isLoading && (
            <PxBadge variant="success" className="mb-4">
              {t('demo.seedData.loaded')} {JSON.parse(existingData).loadedAt.split('T')[0]}
            </PxBadge>
          )}

          {isLoading && (
            <div className="mb-6">
              <PxProgress value={progress} className="mb-3" />
              <p className="text-sm text-ink dark:text-gray-400">{currentStep}</p>
            </div>
          )}

          <div className="flex gap-3 justify-center">
            <PxButton
              variant="primary"
              onClick={loadSeedData}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <span>🚀</span>
              {isLoading ? t('demo.seedData.loading') : t('demo.seedData.generate')}
            </PxButton>

            {existingData && (
              <PxButton
                variant="secondary"
                onClick={clearSeedData}
                disabled={isLoading}
              >
                {t('demo.seedData.clear')}
              </PxButton>
            )}
          </div>
        </div>
      </PxCard>

      {(loadedData || existingData) && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {seedSteps.map((step) => (
            <PxCard key={step.key} className="p-4 text-center">
              <h4 className="font-pixel text-sm text-ink dark:text-white mb-1">
                {step.key.toUpperCase()}
              </h4>
              <p className="text-2xl font-pixel text-primary dark:text-neon-cyan">
                {step.count}
              </p>
              <p className="text-xs text-ink dark:text-gray-400">Generated</p>
            </PxCard>
          ))}
        </div>
      )}
    </div>
  );
};