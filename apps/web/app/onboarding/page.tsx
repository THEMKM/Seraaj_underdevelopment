"use client";

import React from 'react';
import { OnboardingFlow, OnboardingData } from '../../components/onboarding/OnboardingFlow';
import { useRouter } from 'next/navigation';

export default function OnboardingPage() {
  const router = useRouter();

  const handleComplete = (data: OnboardingData) => {
    console.log('Onboarding completed:', data);
    
    // Save onboarding data to localStorage for now
    // In production, this would be saved to the API
    localStorage.setItem('onboardingData', JSON.stringify(data));
    localStorage.setItem('onboardingCompleted', 'true');
    
    // Redirect based on user type
    if (data.userType === 'volunteer') {
      router.push('/feed');
    } else {
      router.push('/dashboard');
    }
  };

  const handleSkip = () => {
    // Allow users to skip onboarding and go to feed
    router.push('/feed');
  };

  return (
    <OnboardingFlow 
      onComplete={handleComplete}
      onSkip={handleSkip}
    />
  );
}