"""
Database seeding utilities for replacing mock data with real database entries
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta, date, time
from sqlmodel import Session, select
import logging

from database import get_session
from models import (
    User, UserRole, UserStatus, Volunteer, Organisation, 
    Opportunity, Application, Review, SkillVerification
)
from models.skill_verification import VerificationStatus, SkillLevel, VerificationMethod
from calendar_module.scheduler import CalendarEvent, EventType, EventStatus

logger = logging.getLogger(__name__)


class DataSeeder:
    """Database seeding for development and testing"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def seed_sample_data(self, force: bool = False) -> Dict[str, Any]:
        """Seed database with sample data if tables are empty"""
        
        results = {
            "users_created": 0,
            "organizations_created": 0,
            "volunteers_created": 0,
            "opportunities_created": 0,
            "applications_created": 0,
            "calendar_events_created": 0,
            "reviews_created": 0,
            "skills_created": 0,
            "verifications_created": 0
        }
        
        # Check if data already exists
        existing_users = self.session.exec(select(User)).first()
        if existing_users and not force:
            logger.info("Database already contains data, skipping seeding")
            return results
        
        logger.info("Starting database seeding...")
        
        # Get sample skills data
        skills_data = await self._get_sample_skills()
        results["skills_created"] = len(skills_data)
        
        # Create sample users (organizations and volunteers)
        organizations = await self._create_sample_organizations()
        volunteers = await self._create_sample_volunteers()
        results["users_created"] = len(organizations) + len(volunteers)
        results["organizations_created"] = len(organizations)
        results["volunteers_created"] = len(volunteers)
        
        # Create sample opportunities
        opportunities = await self._create_sample_opportunities(organizations)
        results["opportunities_created"] = len(opportunities)
        
        # Create sample applications
        applications = await self._create_sample_applications(volunteers, opportunities)
        results["applications_created"] = len(applications)
        
        # Create sample calendar events
        events = await self._create_sample_calendar_events(organizations + volunteers, opportunities)
        results["calendar_events_created"] = len(events)
        
        # Create sample reviews
        reviews = await self._create_sample_reviews(volunteers, organizations)
        results["reviews_created"] = len(reviews)
        
        # Create sample skill verifications
        verifications = await self._create_sample_verifications(volunteers, skills_data)
        results["verifications_created"] = len(verifications)
        
        self.session.commit()
        logger.info(f"Database seeding completed: {results}")
        
        return results
    
    async def _get_sample_skills(self) -> List[dict]:
        """Get sample skills data (no database model needed)"""
        skills_data = [
            {"name": "Python Programming", "category": "Technical"},
            {"name": "Project Management", "category": "Management"},
            {"name": "Graphic Design", "category": "Creative"},
            {"name": "Arabic Translation", "category": "Language"},
            {"name": "Social Media", "category": "Marketing"},
            {"name": "Teaching", "category": "Education"},
            {"name": "Data Analysis", "category": "Technical"},
            {"name": "Community Outreach", "category": "Social"}
        ]
        return skills_data
    
    async def _create_sample_organizations(self) -> List[User]:
        """Create sample organization users"""
        organizations_data = [
            {
                "email": "info@educationforall.org",
                "first_name": "Education",
                "last_name": "For All",
                "role": UserRole.ORGANIZATION,
                "status": UserStatus.ACTIVE,
                "is_verified": True,
                "location": "Cairo, Egypt",
                "bio": "Providing quality education to underserved communities across MENA"
            },
            {
                "email": "contact@cleanwater.ngo",
                "first_name": "Clean Water",
                "last_name": "Initiative",
                "role": UserRole.ORGANIZATION,
                "status": UserStatus.ACTIVE,
                "is_verified": True,
                "location": "Amman, Jordan",
                "bio": "Ensuring access to clean water in rural communities"
            },
            {
                "email": "help@youthempowerment.org",
                "first_name": "Youth",
                "last_name": "Empowerment Hub",
                "role": UserRole.ORGANIZATION,
                "status": UserStatus.ACTIVE,
                "is_verified": True,
                "location": "Beirut, Lebanon",
                "bio": "Empowering young people through skills development and mentorship"
            }
        ]
        
        organizations = []
        for org_data in organizations_data:
            # Create user
            user = User(**org_data, password_hash="$2b$12$demo_hash_for_development")
            self.session.add(user)
            self.session.flush()  # Get user ID
            
            # Create organization profile
            org_profile = Organisation(
                user_id=user.id,
                name=f"{user.first_name} {user.last_name}",
                description=user.bio,
                website=f"https://{user.email.split('@')[1]}",
                organization_type="NGO",
                registration_number=f"NGO-{user.id:06d}",
                verification_documents=["certificate.pdf", "registration.pdf"],
                is_verified=True,
                verification_date=datetime.now(datetime.timezone.utc) - timedelta(days=30),
                trust_score=85.0 + (user.id * 5) % 15
            )
            self.session.add(org_profile)
            
            organizations.append(user)
        
        return organizations
    
    async def _create_sample_volunteers(self) -> List[User]:
        """Create sample volunteer users"""
        volunteers_data = [
            {
                "email": "ahmed.hassan@email.com",
                "first_name": "Ahmed",
                "last_name": "Hassan",
                "role": UserRole.VOLUNTEER,
                "status": UserStatus.ACTIVE,
                "location": "Cairo, Egypt",
                "bio": "Software developer passionate about education technology"
            },
            {
                "email": "fatima.ali@email.com",
                "first_name": "Fatima",
                "last_name": "Ali",
                "role": UserRole.VOLUNTEER,
                "status": UserStatus.ACTIVE,
                "location": "Dubai, UAE",
                "bio": "Marketing professional dedicated to social causes"
            },
            {
                "email": "omar.khalil@email.com",
                "first_name": "Omar",
                "last_name": "Khalil",
                "role": UserRole.VOLUNTEER,
                "status": UserStatus.ACTIVE,
                "location": "Casablanca, Morocco",
                "bio": "Graphic designer helping nonprofits with visual identity"
            },
            {
                "email": "layla.mahmoud@email.com",
                "first_name": "Layla",
                "last_name": "Mahmoud",
                "role": UserRole.VOLUNTEER,
                "status": UserStatus.ACTIVE,
                "location": "Tunis, Tunisia",
                "bio": "Teacher focused on community education programs"
            }
        ]
        
        volunteers = []
        for vol_data in volunteers_data:
            # Create user
            user = User(**vol_data, password_hash="$2b$12$demo_hash_for_development") 
            self.session.add(user)
            self.session.flush()  # Get user ID
            
            # Create volunteer profile
            volunteer_profile = Volunteer(
                user_id=user.id,
                skills=["Python Programming", "Project Management", "Graphic Design", "Teaching"][user.id % 4:user.id % 4 + 2],
                experience_years=2 + (user.id % 8),
                availability_hours=10 + (user.id % 20),
                preferred_causes=["Education", "Environment", "Health", "Technology"][user.id % 4:user.id % 4 + 2],
                languages=["Arabic", "English", "French"][:(user.id % 3) + 1],
                resume_file=f"resume_{user.id}.pdf",
                portfolio_links=["https://github.com/user", "https://portfolio.example.com"],
                emergency_contact="Emergency Contact Name",
                emergency_phone="+1234567890",
                background_check_status="completed",
                background_check_date=datetime.now(datetime.timezone.utc) - timedelta(days=60)
            )
            self.session.add(volunteer_profile)
            
            volunteers.append(user)
        
        return volunteers
    
    async def _create_sample_opportunities(self, organizations: List[User]) -> List[Opportunity]:
        """Create sample opportunities"""
        opportunities = []
        
        for i, org_user in enumerate(organizations):
            # Get organization profile
            org_profile = self.session.exec(
                select(Organisation).where(Organisation.user_id == org_user.id)
            ).first()
            
            opp_data = [
                {
                    "title": f"Education Technology Developer - {org_profile.name}",
                    "description": "Help build educational platforms for underserved communities",
                    "requirements": ["Python Programming", "Web Development", "UI/UX Design"],
                    "location": org_user.location,
                    "time_commitment": "10-15 hours per week",
                    "skills_required": ["Python Programming", "Project Management"],
                    "cause_area": "Education",
                    "is_remote": True,
                    "start_date": datetime.now(datetime.timezone.utc) + timedelta(days=7),
                    "end_date": datetime.now(datetime.timezone.utc) + timedelta(days=90),
                    "max_volunteers": 3,
                    "is_active": True
                },
                {
                    "title": f"Community Outreach Coordinator - {org_profile.name}",
                    "description": "Coordinate community outreach programs and events",
                    "requirements": ["Communication Skills", "Event Planning", "Local Language"],
                    "location": org_user.location,
                    "time_commitment": "8-12 hours per week",
                    "skills_required": ["Community Outreach", "Project Management"],
                    "cause_area": "Community Development",
                    "is_remote": False,
                    "start_date": datetime.now(datetime.timezone.utc) + timedelta(days=14),
                    "end_date": datetime.now(datetime.timezone.utc) + timedelta(days=120),
                    "max_volunteers": 2,
                    "is_active": True
                }
            ]
            
            for opp_info in opp_data:
                opportunity = Opportunity(
                    **opp_info,
                    organization_id=org_user.id,
                    created_by=org_user.id
                )
                self.session.add(opportunity)
                opportunities.append(opportunity)
        
        return opportunities
    
    async def _create_sample_applications(self, volunteers: List[User], opportunities: List[Opportunity]) -> List[Application]:
        """Create sample applications"""
        applications = []
        
        # Create applications for first few opportunities
        for i, opportunity in enumerate(opportunities[:4]):
            for j, volunteer in enumerate(volunteers):
                if j > i:  # Don't apply to all opportunities
                    break
                    
                application = Application(
                    opportunity_id=opportunity.id,
                    volunteer_id=volunteer.id,
                    motivation="I'm excited to contribute to this meaningful cause and apply my skills to make a difference.",
                    relevant_experience="Previous volunteer work with similar organizations and technical background.",
                    availability="Flexible schedule, can commit to required hours",
                    additional_info="Happy to provide references and portfolio upon request",
                    status="pending" if j % 3 == 0 else "accepted" if j % 3 == 1 else "reviewed"
                )
                self.session.add(application)
                applications.append(application)
        
        return applications
    
    async def _create_sample_calendar_events(self, users: List[User], opportunities: List[Opportunity]) -> List[CalendarEvent]:
        """Create sample calendar events"""
        events = []
        
        # Create events for the next few weeks
        start_date = datetime.now(datetime.timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        
        for i in range(10):  # Create 10 sample events
            event_date = start_date + timedelta(days=i * 2)
            user = users[i % len(users)]
            opportunity = opportunities[i % len(opportunities)] if opportunities else None
            
            event = CalendarEvent(
                title=f"Team Meeting - {opportunity.title if opportunity else 'General Planning'}",
                description=f"Regular team coordination meeting",
                event_type=EventType.MEETING,
                start_datetime=event_date,
                end_datetime=event_date + timedelta(hours=1),
                location="Online" if i % 2 == 0 else user.location,
                virtual_meeting_url="https://meet.example.com/room123" if i % 2 == 0 else None,
                organizer_id=user.id,
                user_id=user.id,
                participant_ids=[u.id for u in users[:3]],
                opportunity_id=opportunity.id if opportunity else None,
                status=EventStatus.SCHEDULED,
                reminder_minutes=30
            )
            self.session.add(event)
            events.append(event)
        
        return events
    
    async def _create_sample_reviews(self, volunteers: List[User], organizations: List[User]) -> List[Review]:
        """Create sample reviews"""
        reviews = []
        
        # Create reviews between volunteers and organizations
        for i, volunteer in enumerate(volunteers[:2]):  # First 2 volunteers
            for j, org in enumerate(organizations[:2]):  # First 2 organizations
                
                # Organization reviews volunteer
                org_review = Review(
                    reviewer_id=org.id,
                    reviewee_id=volunteer.id,
                    opportunity_id=1,  # Reference first opportunity
                    rating=4.0 + (i + j) * 0.2,
                    comment=f"Great work from {volunteer.first_name}. Very professional and dedicated to the cause.",
                    review_type="organization_to_volunteer"
                )
                self.session.add(org_review)
                reviews.append(org_review)
                
                # Volunteer reviews organization
                vol_review = Review(
                    reviewer_id=volunteer.id,
                    reviewee_id=org.id,
                    opportunity_id=1,
                    rating=4.2 + (i + j) * 0.15,
                    comment=f"Excellent organization with clear communication and meaningful impact.",
                    review_type="volunteer_to_organization"
                )
                self.session.add(vol_review)
                reviews.append(vol_review)
        
        return reviews
    
    async def _create_sample_verifications(self, volunteers: List[User], skills_data: List[dict]) -> List[SkillVerification]:
        """Create sample skill verifications"""
        verifications = []
        
        for volunteer in volunteers:
            # Each volunteer gets 1-2 skill verifications
            volunteer_skill_indices = list(range(volunteer.id % len(skills_data), min(volunteer.id % len(skills_data) + 2, len(skills_data))))
            
            for skill_index in volunteer_skill_indices:
                skill = skills_data[skill_index]
                verification = SkillVerification(
                    volunteer_id=volunteer.id,
                    skill_name=skill["name"],
                    skill_category=skill["category"],
                    skill_level=SkillLevel.INTERMEDIATE,
                    verification_method=VerificationMethod.PORTFOLIO,
                    status=VerificationStatus.APPROVED if volunteer.id % 3 != 0 else VerificationStatus.PENDING,
                    confidence_score=75.0 + (volunteer.id + skill_index) % 25,
                    verification_metadata={
                        "method": "portfolio_review",
                        "reviewer": "system",
                        "evidence_type": "portfolio"
                    }
                )
                self.session.add(verification)
                verifications.append(verification)
        
        return verifications


# Utility function to seed data
async def seed_development_data(force: bool = False) -> Dict[str, Any]:
    """Seed database with development data"""
    
    with next(get_session()) as session:
        seeder = DataSeeder(session)
        return await seeder.seed_sample_data(force=force)


if __name__ == "__main__":
    # Run seeding directly
    import asyncio
    
    async def main():
        result = await seed_development_data(force=True)
        print(f"Seeding completed: {result}")
    
    asyncio.run(main())