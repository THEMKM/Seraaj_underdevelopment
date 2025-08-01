"use client";

import { useState } from "react";
import { PxButton, PxCard, PxChip } from "../../../components/ui";

// Mock data for demonstration
const mockApplications = [
  {
    id: 1,
    opportunityTitle: "English Tutor for Refugee Children",
    volunteer: {
      name: "Sarah Ahmed",
      skills: ["Teaching", "English", "Patience"],
      matchScore: 95,
      experience: "3 years teaching experience"
    },
    status: "applied",
    appliedAt: "2 hours ago"
  },
  {
    id: 2,
    opportunityTitle: "English Tutor for Refugee Children",
    volunteer: {
      name: "Omar Hassan",
      skills: ["Teaching", "Arabic", "English"],
      matchScore: 87,
      experience: "Former school teacher"
    },
    status: "recommended",
    appliedAt: "5 hours ago"
  },
  {
    id: 3,
    opportunityTitle: "Community Outreach Coordinator",
    volunteer: {
      name: "Layla Mansour",
      skills: ["Communication", "Arabic", "Event Planning"],
      matchScore: 92,
      experience: "NGO volunteer for 2 years"
    },
    status: "interviewing",
    appliedAt: "1 day ago"
  },
  {
    id: 4,
    opportunityTitle: "Community Outreach Coordinator",
    volunteer: {
      name: "Ahmed Ali",
      skills: ["Leadership", "Arabic", "Community Work"],
      matchScore: 88,
      experience: "Community organizer"
    },
    status: "accepted",
    appliedAt: "3 days ago"
  }
];

const columns = [
  { id: "applied", title: "APPLIED", color: "bg-white" },
  { id: "recommended", title: "RECOMMENDED", color: "bg-primary" },
  { id: "interviewing", title: "INTERVIEWING", color: "bg-pixel-mint" },
  { id: "accepted", title: "ACCEPTED", color: "bg-pixel-coral" }
];

export default function OrgDashboard() {
  const [applications, setApplications] = useState(mockApplications);

  const getApplicationsByStatus = (status: string) => {
    return applications.filter(app => app.status === status);
  };

  const moveApplication = (applicationId: number, newStatus: string) => {
    setApplications(prev => 
      prev.map(app => 
        app.id === applicationId ? { ...app, status: newStatus } : app
      )
    );
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b-2 border-ink bg-primary">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-pixel text-ink">HOPE FOUNDATION</h1>
              <p className="text-ink">Organization Dashboard</p>
            </div>
            <nav className="flex items-center gap-4">
              <PxButton variant="primary" size="sm">
                POST NEW ROLE
              </PxButton>
              <PxButton variant="secondary" size="sm">
                SETTINGS
              </PxButton>
              <PxButton variant="secondary" size="sm">
                LOG OUT
              </PxButton>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-pixel text-ink mb-4">APPLICATION PIPELINE</h2>
          <p className="text-ink leading-relaxed">
            Manage your volunteer applications with drag-and-drop simplicity.
          </p>
        </div>

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {columns.map((column) => {
            const columnApplications = getApplicationsByStatus(column.id);
            
            return (
              <div key={column.id} className="space-y-4">
                {/* Column Header */}
                <div className={`${column.color} border-2 border-ink clip-px p-4`}>
                  <h3 className="font-pixel text-ink text-center">
                    {column.title} ({columnApplications.length})
                  </h3>
                </div>

                {/* Applications */}
                <div className="space-y-4">
                  {columnApplications.map((application) => (
                    <PxCard key={application.id} className="p-4">
                      {/* Recommended Badge */}
                      {application.status === "recommended" && (
                        <div className="bg-pixel-coral text-white px-2 py-1 font-pixel text-xs clip-px mb-3 text-center">
                          ⭐ RECOMMENDED
                        </div>
                      )}

                      {/* Volunteer Info */}
                      <div className="mb-3">
                        <h4 className="font-pixel text-ink text-sm mb-1">
                          {application.volunteer.name}
                        </h4>
                        <p className="text-xs text-ink mb-2">
                          {application.volunteer.experience}
                        </p>
                        <div className="bg-primary px-2 py-1 border border-ink clip-px inline-block">
                          <span className="font-pixel text-xs text-ink">
                            {application.volunteer.matchScore}% MATCH
                          </span>
                        </div>
                      </div>

                      {/* Skills */}
                      <div className="mb-4">
                        <div className="flex gap-1 flex-wrap">
                          {application.volunteer.skills.slice(0, 3).map((skill) => (
                            <PxChip key={skill} size="sm">
                              {skill}
                            </PxChip>
                          ))}
                        </div>
                      </div>

                      {/* Opportunity */}
                      <p className="text-xs text-ink mb-3">
                        Applied for: {application.opportunityTitle}
                      </p>
                      <p className="text-xs text-gray-600 mb-4">
                        {application.appliedAt}
                      </p>

                      {/* Actions */}
                      <div className="space-y-2">
                        {column.id === "applied" && (
                          <>
                            <PxButton 
                              size="sm" 
                              variant="primary" 
                              className="w-full text-xs"
                              onClick={() => moveApplication(application.id, "recommended")}
                            >
                              RECOMMEND
                            </PxButton>
                            <PxButton 
                              size="sm" 
                              variant="secondary" 
                              className="w-full text-xs"
                            >
                              VIEW PROFILE
                            </PxButton>
                          </>
                        )}
                        
                        {column.id === "recommended" && (
                          <>
                            <PxButton 
                              size="sm" 
                              variant="primary" 
                              className="w-full text-xs"
                              onClick={() => moveApplication(application.id, "interviewing")}
                            >
                              INTERVIEW
                            </PxButton>
                            <PxButton 
                              size="sm" 
                              variant="secondary" 
                              className="w-full text-xs"
                            >
                              MESSAGE
                            </PxButton>
                          </>
                        )}
                        
                        {column.id === "interviewing" && (
                          <>
                            <PxButton 
                              size="sm" 
                              variant="primary" 
                              className="w-full text-xs"
                              onClick={() => moveApplication(application.id, "accepted")}
                            >
                              ACCEPT
                            </PxButton>
                            <PxButton 
                              size="sm" 
                              variant="danger" 
                              className="w-full text-xs"
                            >
                              REJECT
                            </PxButton>
                          </>
                        )}
                        
                        {column.id === "accepted" && (
                          <PxButton 
                            size="sm" 
                            variant="secondary" 
                            className="w-full text-xs"
                          >
                            CONTACT
                          </PxButton>
                        )}
                      </div>
                    </PxCard>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <PxCard className="p-6 text-center">
            <h3 className="font-pixel text-ink mb-2">ACTIVE ROLES</h3>
            <p className="text-3xl font-pixel text-primary">3</p>
          </PxCard>
          
          <PxCard className="p-6 text-center">
            <h3 className="font-pixel text-ink mb-2">TOTAL APPLICATIONS</h3>
            <p className="text-3xl font-pixel text-primary">24</p>
          </PxCard>
          
          <PxCard className="p-6 text-center">
            <h3 className="font-pixel text-ink mb-2">VOLUNTEERS ONBOARDED</h3>
            <p className="text-3xl font-pixel text-primary">12</p>
          </PxCard>
        </div>
      </main>
    </div>
  );
}