"use client";

import React, { useState } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { ProfileManagement, ProfileData, ProfileVersion } from '../../components/profile/ProfileManagement';

// Mock profile data
const mockProfile: ProfileData = {
  id: '1',
  userType: 'volunteer',
  name: 'Ahmed Hassan',
  email: 'ahmed.hassan@email.com',
  location: 'Amman, Jordan',
  bio: 'Passionate educator and community advocate with 5+ years of experience in youth development and educational programs. I believe in the power of education to transform communities and am dedicated to creating inclusive learning environments for all.',
  avatar: undefined,
  skills: ['Teaching', 'Mentoring', 'Public Speaking', 'Arabic', 'English', 'Project Management'],
  causes: ['Education', 'Youth Development', 'Refugees', 'Community Development'],
  interests: ['Direct Service', 'Training & Workshops', 'Mentoring', 'Community Outreach'],
  availability: '6-10',
  experience: 'I have been volunteering with educational organizations for over 5 years, starting with local community centers in Amman. My most impactful project was developing a literacy program for refugee children that served over 200 families. I also led a team of 15 volunteers in organizing summer camps that combined education with recreational activities.\n\nI am particularly skilled at working with diverse groups and creating engaging learning experiences that adapt to different learning styles and cultural backgrounds.',
  languages: ['Arabic', 'English', 'French'],
  completionScore: 85,
  lastUpdated: '2024-01-22T10:30:00Z',
  version: 3,
  isPublic: true,
  isVerified: true,
  verificationLevel: 'verified'
};

// Mock version history
const mockVersions: ProfileVersion[] = [
  {
    id: 'v3',
    version: 3,
    data: mockProfile,
    timestamp: '2024-01-22T10:30:00Z',
    changes: [
      'Updated bio with recent project experience',
      'Added French to languages',
      'Updated availability from 3-5 to 6-10 hours/week',
      'Added Project Management skill'
    ],
    updatedBy: 'Ahmed Hassan'
  },
  {
    id: 'v2',
    version: 2,
    data: {
      ...mockProfile,
      bio: 'Passionate educator with experience in youth development programs.',
      languages: ['Arabic', 'English'],
      availability: '3-5',
      skills: ['Teaching', 'Mentoring', 'Public Speaking', 'Arabic', 'English'],
      experience: 'I have been volunteering with educational organizations for over 5 years, starting with local community centers in Amman.',
      completionScore: 70,
      lastUpdated: '2024-01-15T14:20:00Z',
      version: 2
    },
    timestamp: '2024-01-15T14:20:00Z',
    changes: [
      'Added volunteer experience section',
      'Updated skills list',
      'Added interests and availability'
    ],
    updatedBy: 'Ahmed Hassan'
  },
  {
    id: 'v1',
    version: 1,
    data: {
      ...mockProfile,
      bio: 'Teacher interested in volunteering.',
      skills: ['Teaching'],
      causes: ['Education'],
      interests: [],
      availability: undefined,
      experience: undefined,
      languages: ['Arabic'],
      completionScore: 35,
      lastUpdated: '2024-01-10T09:15:00Z',
      version: 1
    },
    timestamp: '2024-01-10T09:15:00Z',
    changes: [
      'Created initial profile',
      'Added basic information',
      'Set profile to public'
    ],
    updatedBy: 'Ahmed Hassan'
  }
];

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData>(mockProfile);
  const [versions, setVersions] = useState<ProfileVersion[]>(mockVersions);

  const handleSave = (updatedProfile: ProfileData) => {
    // Create a new version
    const newVersion: ProfileVersion = {
      id: `v${updatedProfile.version + 1}`,
      version: updatedProfile.version + 1,
      data: { ...updatedProfile, version: updatedProfile.version + 1 },
      timestamp: new Date().toISOString(),
      changes: generateChangeList(profile, updatedProfile),
      updatedBy: profile.name
    };

    setProfile({ ...updatedProfile, version: updatedProfile.version + 1 });
    setVersions(prev => [newVersion, ...prev]);
  };

  const handleRevert = (versionId: string) => {
    const version = versions.find(v => v.id === versionId);
    if (version) {
      // Create a new version based on the reverted data
      const revertedProfile = {
        ...version.data,
        version: profile.version + 1,
        lastUpdated: new Date().toISOString()
      };

      const newVersion: ProfileVersion = {
        id: `v${revertedProfile.version}`,
        version: revertedProfile.version,
        data: revertedProfile,
        timestamp: new Date().toISOString(),
        changes: [`Reverted to version ${version.version}`],
        updatedBy: profile.name
      };

      setProfile(revertedProfile);
      setVersions(prev => [newVersion, ...prev]);
    }
  };

  const generateChangeList = (oldProfile: ProfileData, newProfile: ProfileData): string[] => {
    const changes: string[] = [];

    // Basic fields
    if (oldProfile.name !== newProfile.name) changes.push('Updated name');
    if (oldProfile.email !== newProfile.email) changes.push('Updated email');
    if (oldProfile.location !== newProfile.location) changes.push('Updated location');
    if (oldProfile.bio !== newProfile.bio) changes.push('Updated bio');

    // Skills
    const oldSkills = oldProfile.skills || [];
    const newSkills = newProfile.skills || [];
    const addedSkills = newSkills.filter(s => !oldSkills.includes(s));
    const removedSkills = oldSkills.filter(s => !newSkills.includes(s));
    
    if (addedSkills.length > 0) changes.push(`Added skills: ${addedSkills.join(', ')}`);
    if (removedSkills.length > 0) changes.push(`Removed skills: ${removedSkills.join(', ')}`);

    // Causes
    const oldCauses = oldProfile.causes || [];
    const newCauses = newProfile.causes || [];
    const addedCauses = newCauses.filter(c => !oldCauses.includes(c));
    const removedCauses = oldCauses.filter(c => !newCauses.includes(c));
    
    if (addedCauses.length > 0) changes.push(`Added causes: ${addedCauses.join(', ')}`);
    if (removedCauses.length > 0) changes.push(`Removed causes: ${removedCauses.join(', ')}`);

    // Other fields
    if (oldProfile.availability !== newProfile.availability) changes.push('Updated availability');
    if (oldProfile.experience !== newProfile.experience) changes.push('Updated experience');
    if (oldProfile.isPublic !== newProfile.isPublic) {
      changes.push(`Set profile to ${newProfile.isPublic ? 'public' : 'private'}`);
    }

    // Languages
    const oldLanguages = oldProfile.languages || [];
    const newLanguages = newProfile.languages || [];
    if (JSON.stringify(oldLanguages.sort()) !== JSON.stringify(newLanguages.sort())) {
      changes.push('Updated languages');
    }

    return changes.length > 0 ? changes : ['Minor updates'];
  };

  return (
    <AppLayout userType="volunteer">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <ProfileManagement
          profile={profile}
          versions={versions}
          onSave={handleSave}
          onRevert={handleRevert}
        />
      </div>
    </AppLayout>
  );
}