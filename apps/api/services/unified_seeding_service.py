# -*- coding: utf-8 -*-
"""
🏛️ SUPREME UNIFIED SEEDING SERVICE 🏛️
The ONE service to rule all data seeding - blessed by the gods of code

This divine service consolidates ALL seeding functionality:
- Demo users creation
- Test data generation  
- Production-ready seeding
- Database population
- Analytics data generation

NO MORE DUPLICATE SCRIPTS! ONE SERVICE TO RULE THEM ALL!
"""
import asyncio
import sys
import os
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlmodel import Session, create_engine, select

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_session, create_db_and_tables
from models import (
    User, UserRole, UserStatus, Volunteer, Organisation, 
    Opportunity, OpportunityState, Application, ApplicationStatus,
    Conversation, Message, AnalyticsEvent, Review
)
from auth.password_utils import hash_password
from utils.encoding_config import divine_print
from config.settings import settings

class UnifiedSeedingService:
    """🔥 THE SUPREME SEEDING SERVICE - One service to rule them all! 🔥"""
    
    def __init__(self):
        self.session = next(get_session())
        divine_print("Supreme Seeding Service initialized", "⚡")
        
        # MENA-focused data for realistic seeding
        self.countries = [
            {"en": "Egypt", "ar": "مصر", "code": "EG"},
            {"en": "Jordan", "ar": "الأردن", "code": "JO"},
            {"en": "Lebanon", "ar": "لبنان", "code": "LB"},
            {"en": "Morocco", "ar": "المغرب", "code": "MA"},
            {"en": "Tunisia", "ar": "تونس", "code": "TN"},
            {"en": "UAE", "ar": "الإمارات", "code": "AE"},
        ]
        
        self.cities = {
            "Egypt": [{"en": "Cairo", "ar": "القاهرة"}, {"en": "Alexandria", "ar": "الإسكندرية"}],
            "Jordan": [{"en": "Amman", "ar": "عمان"}, {"en": "Zarqa", "ar": "الزرقاء"}],
            "Lebanon": [{"en": "Beirut", "ar": "بيروت"}, {"en": "Tripoli", "ar": "طرابلس"}],
            "Morocco": [{"en": "Casablanca", "ar": "الدار البيضاء"}, {"en": "Rabat", "ar": "الرباط"}],
            "Tunisia": [{"en": "Tunis", "ar": "تونس"}, {"en": "Sfax", "ar": "صفاقس"}],
            "UAE": [{"en": "Dubai", "ar": "دبي"}, {"en": "Abu Dhabi", "ar": "أبو ظبي"}],
        }
        
        self.causes = [
            {"en": "Education", "ar": "التعليم"},
            {"en": "Healthcare", "ar": "الرعاية الصحية"},
            {"en": "Environment", "ar": "البيئة"},
            {"en": "Community Development", "ar": "تنمية المجتمع"},
            {"en": "Women Empowerment", "ar": "تمكين المرأة"},
            {"en": "Youth Development", "ar": "تنمية الشباب"}
        ]
        
        self.skills = [
            "Arabic", "English", "French", "Project Management", "Teaching",
            "Healthcare", "Social Work", "Marketing", "Technology", "Design",
            "Writing", "Translation", "Event Planning", "Fundraising"
        ]
    
    def clear_all_data(self):
        """🧹 Clear all existing data - prepare for divine seeding"""
        divine_print("Clearing existing data for divine renewal", "🧹")
        
        try:
            # Clear in reverse dependency order
            self.session.query(Message).delete()
            self.session.query(Conversation).delete()
            self.session.query(Review).delete()
            self.session.query(AnalyticsEvent).delete()
            self.session.query(Application).delete()
            self.session.query(Opportunity).delete()
            self.session.query(Volunteer).delete()
            self.session.query(Organisation).delete()
            self.session.query(User).delete()
            
            self.session.commit()
            divine_print("All data purged successfully", "✅")
            
        except Exception as e:
            divine_print(f"Error during data purge: {e}", "❌")
            self.session.rollback()
            raise
    
    def create_demo_users(self, count: int = 10) -> List[User]:
        """👥 Create demo users with diverse profiles"""
        divine_print(f"Creating {count} divine demo users", "👥")
        
        users = []
        
        # Create admin user
        admin = User(
            email="admin@seraaj.org",
            first_name="System",
            last_name="Administrator", 
            role=UserRole.ADMIN,
            hashed_password=hash_password("admin123"),
            is_verified=True,
            profile_completion=100.0,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=365)
        )
        self.session.add(admin)
        users.append(admin)
        
        # Create diverse demo users
        for i in range(count - 1):
            country = random.choice(self.countries)
            city = random.choice(self.cities.get(country["en"], [{"en": "City", "ar": "مدينة"}]))
            
            role = random.choice([UserRole.VOLUNTEER, UserRole.ORGANIZATION])
            
            user = User(
                email=f"user{i+1}@demo.seraaj.org",
                first_name=self._get_random_first_name(),
                last_name=self._get_random_last_name(),
                role=role,
                hashed_password=hash_password("Demo123!"),
                is_verified=random.choice([True, False]),
                profile_completion=random.uniform(30.0, 100.0),
                created_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 365))
            )
            self.session.add(user)
            users.append(user)
        
        self.session.commit()
        divine_print(f"✅ {len(users)} demo users created successfully", "✅")
        return users
    
    def create_volunteer_profiles(self, users: List[User]) -> List[Volunteer]:
        """🤝 Create volunteer profiles for volunteer users"""
        volunteers = []
        volunteer_users = [u for u in users if u.role == UserRole.VOLUNTEER]
        
        divine_print(f"Creating {len(volunteer_users)} volunteer profiles", "🤝")
        
        for user in volunteer_users:
            country = random.choice(self.countries)
            city = random.choice(self.cities.get(country["en"], [{"en": "City", "ar": "مدينة"}]))
            user_skills = random.sample(self.skills, random.randint(2, 6))
            
            volunteer = Volunteer(
                user_id=user.id,
                bio=f"Passionate volunteer from {city['en']}, {country['en']}. Committed to making a positive impact in the MENA region.",
                skills=user_skills,
                experience_level="intermediate",
                availability="weekends",
                location=f"{city['en']}, {country['en']}",
                phone_number=f"+{country['code']}{random.randint(100000000, 999999999)}",
                date_of_birth=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(6570, 18250)),  # 18-50 years
                gender=random.choice(["male", "female", "prefer_not_to_say"]),
                education_level=random.choice(["high_school", "bachelor", "master", "phd"]),
                languages_spoken=["Arabic", "English"] + random.sample(["French", "German", "Spanish"], random.randint(0, 2)),
                emergency_contact_name=f"Emergency Contact {random.randint(1, 100)}",
                emergency_contact_phone=f"+{country['code']}{random.randint(100000000, 999999999)}",
                has_volunteered_before=random.choice([True, False]),
                motivation="I want to contribute to positive change in my community and help those in need.",
                volunteer_hours_completed=random.randint(0, 500),
                rating_average=random.uniform(3.0, 5.0),
                is_background_checked=random.choice([True, False])
            )
            
            self.session.add(volunteer)
            volunteers.append(volunteer)
        
        self.session.commit()
        divine_print(f"✅ {len(volunteers)} volunteer profiles created", "✅")
        return volunteers
    
    def create_organization_profiles(self, users: List[User]) -> List[Organisation]:
        """🏢 Create organization profiles"""
        organizations = []
        org_users = [u for u in users if u.role == UserRole.ORGANIZATION]
        
        divine_print(f"Creating {len(org_users)} organization profiles", "🏢")
        
        for user in org_users:
            country = random.choice(self.countries)
            city = random.choice(self.cities.get(country["en"], [{"en": "City", "ar": "مدينة"}]))
            org_causes = random.sample(self.causes, random.randint(1, 3))
            
            organization = Organisation(
                user_id=user.id,
                name=f"{random.choice(['Hope', 'Future', 'Unity', 'Progress', 'Bright'])} {random.choice(['Foundation', 'Initiative', 'Organization', 'Center'])} - {country['en']}",
                description=f"A dedicated nonprofit organization in {city['en']}, {country['en']} working towards positive social impact.",
                mission="To create sustainable positive change in our community through collaborative efforts and innovative solutions.",
                vision="A thriving, equitable society where everyone has opportunities to succeed and contribute.",
                website=f"https://www.example-org-{random.randint(1000, 9999)}.org",
                phone_number=f"+{country['code']}{random.randint(100000000, 999999999)}",
                address=f"{random.randint(1, 999)} Main Street, {city['en']}, {country['en']}",
                registration_number=f"REG-{country['code']}-{random.randint(100000, 999999)}",
                tax_id=f"TAX-{random.randint(1000000, 9999999)}",
                founded_date=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(365, 7300)),  # 1-20 years ago
                organization_size=random.choice(["small", "medium", "large"]),
                annual_budget_range=random.choice(["under_10k", "10k_50k", "50k_100k", "100k_500k", "over_500k"]),
                causes_supported=[cause["en"] for cause in org_causes],
                target_demographics=random.sample(["youth", "women", "elderly", "families", "students"], random.randint(1, 3)),
                geographic_scope=random.choice(["local", "national", "regional", "international"]),
                is_verified=random.choice([True, False]),
                verification_documents_uploaded=random.choice([True, False]),
                rating_average=random.uniform(3.5, 5.0),
                total_volunteers_managed=random.randint(5, 200),
                total_opportunities_created=random.randint(1, 50)
            )
            
            self.session.add(organization)
            organizations.append(organization)
        
        self.session.commit()
        divine_print(f"✅ {len(organizations)} organization profiles created", "✅")
        return organizations
    
    def create_opportunities(self, organizations: List[Organisation], count: int = 20) -> List[Opportunity]:
        """🎯 Create diverse volunteer opportunities"""
        divine_print(f"Creating {count} divine opportunities", "🎯")
        
        opportunities = []
        
        opportunity_templates = [
            {
                "title": "Community Teaching Program",
                "description": "Help teach basic literacy and numeracy skills to underserved communities.",
                "skills": ["Teaching", "Arabic", "English", "Patience"],
                "cause": "Education"
            },
            {
                "title": "Healthcare Support Initiative", 
                "description": "Assist medical professionals in community health screenings and awareness campaigns.",
                "skills": ["Healthcare", "Communication", "Organization"],
                "cause": "Healthcare"
            },
            {
                "title": "Environmental Conservation Project",
                "description": "Participate in tree planting, waste management, and environmental education programs.",
                "skills": ["Environmental Awareness", "Physical Labor", "Team Work"],
                "cause": "Environment"
            },
            {
                "title": "Women's Empowerment Workshop",
                "description": "Facilitate skills training and entrepreneurship workshops for women in the community.",
                "skills": ["Training", "Business", "Communication", "Arabic"],
                "cause": "Women Empowerment"
            },
            {
                "title": "Youth Mentorship Program",
                "description": "Mentor young people in career development, life skills, and personal growth.",
                "skills": ["Mentoring", "Communication", "Life Coaching"],
                "cause": "Youth Development"
            }
        ]
        
        for i in range(count):
            org = random.choice(organizations)
            template = random.choice(opportunity_templates)
            
            start_date = datetime.now(datetime.timezone.utc) + timedelta(days=random.randint(1, 90))
            end_date = start_date + timedelta(days=random.randint(7, 180))
            
            opportunity = Opportunity(
                title=f"{template['title']} - {random.choice(['Phase', 'Initiative', 'Project', 'Program'])} {i+1}",
                description=template['description'] + f" This is a {random.randint(1, 12)} month commitment opportunity.",
                org_id=org.user_id,
                skills_required=template['skills'],
                start_date=start_date,
                end_date=end_date,
                location=org.address or f"Location {i+1}",
                remote_allowed=random.choice([True, False]),
                time_commitment=f"{random.randint(2, 20)} hours per week",
                volunteers_needed=random.randint(1, 15),
                state=random.choice(list(OpportunityState)),
                urgency_level="medium",
                cause_area=template['cause'],
                requirements=f"Minimum {random.randint(0, 3)} years experience preferred. Must be committed and reliable.",
                benefits="Gain valuable experience, make meaningful connections, and contribute to positive social impact.",
                training_provided=random.choice([True, False]),
                background_check_required=random.choice([True, False]),
                minimum_age=random.choice([16, 18, 21]),
                created_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 60)),
                featured=random.choice([True, False]),
                view_count=random.randint(0, 500),
                application_count=random.randint(0, 25)
            )
            
            self.session.add(opportunity)
            opportunities.append(opportunity)
        
        self.session.commit()
        divine_print(f"✅ {count} opportunities created successfully", "✅")
        return opportunities
    
    def create_applications(self, volunteers: List[Volunteer], opportunities: List[Opportunity], count: int = 50):
        """📝 Create volunteer applications"""
        divine_print(f"Creating {count} applications", "📝")
        
        applications = []
        
        for i in range(count):
            volunteer = random.choice(volunteers)
            opportunity = random.choice(opportunities)
            
            # Avoid duplicate applications
            existing = self.session.exec(
                select(Application).where(
                    Application.volunteer_id == volunteer.user_id,
                    Application.opp_id == opportunity.id
                )
            ).first()
            
            if existing:
                continue
            
            application = Application(
                volunteer_id=volunteer.user_id,
                opp_id=opportunity.id,
                cover_letter=f"I am very interested in this {opportunity.cause_area.lower()} opportunity. My skills in {', '.join(opportunity.skills_required[:2])} make me a great fit for this role. I am committed to making a positive impact.",
                status=random.choice(list(ApplicationStatus)),
                applied_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 30)),
                availability_notes=f"Available {random.choice(['weekdays', 'weekends', 'evenings', 'flexible schedule'])}",
                experience_relevance=f"I have {random.randint(0, 10)} years of relevant experience in this field.",
                motivation="I am passionate about contributing to positive change in my community.",
                additional_info="Thank you for considering my application. I look forward to contributing to your organization's mission."
            )
            
            self.session.add(application)
            applications.append(application)
        
        self.session.commit()
        divine_print(f"✅ {len(applications)} applications created", "✅")
        return applications
    
    def _get_random_first_name(self) -> str:
        """Get random first name (mix of Arabic and international names)"""
        names = [
            "Ahmed", "Fatima", "Mohammed", "Aisha", "Omar", "Zara",
            "Khalid", "Layla", "Hassan", "Nour", "Ali", "Maryam",
            "Sarah", "John", "Maria", "David", "Anna", "Michael"
        ]
        return random.choice(names)
    
    def _get_random_last_name(self) -> str:
        """Get random last name"""
        names = [
            "Al-Rahman", "Hassan", "Ahmed", "Al-Zahra", "Smith", "Johnson",
            "Al-Masri", "Al-Jordani", "Brown", "Wilson", "Garcia", "Al-Maghribi"
        ]
        return random.choice(names)
    
    def seed_all_data(self, 
                     user_count: int = 15,
                     opportunity_count: int = 25, 
                     application_count: int = 75,
                     clear_existing: bool = True):
        """🚀 SUPREME SEEDING FUNCTION - Create all data with divine efficiency"""
        
        divine_print("🏛️ SUPREME UNIFIED SEEDING BEGINS 🏛️", "🚀")
        
        try:
            # Clear existing data if requested
            if clear_existing:
                self.clear_all_data()
            
            # Initialize database tables
            create_db_and_tables()
            divine_print("Database tables initialized", "🗄️")
            
            # Create users
            users = self.create_demo_users(user_count)
            
            # Create profiles
            volunteers = self.create_volunteer_profiles(users)
            organizations = self.create_organization_profiles(users)
            
            # Create opportunities
            opportunities = self.create_opportunities(organizations, opportunity_count)
            
            # Create applications
            applications = self.create_applications(volunteers, opportunities, application_count)
            
            divine_print("🎉 SUPREME SEEDING COMPLETED SUCCESSFULLY! 🎉", "🏆")
            divine_print(f"Created: {len(users)} users, {len(volunteers)} volunteers, {len(organizations)} orgs, {len(opportunities)} opportunities, {len(applications)} applications", "📊")
            
            return {
                "users": len(users),
                "volunteers": len(volunteers),
                "organizations": len(organizations),
                "opportunities": len(opportunities),
                "applications": len(applications)
            }
            
        except Exception as e:
            divine_print(f"❌ Error during supreme seeding: {e}", "❌")
            self.session.rollback()
            raise
        finally:
            self.session.close()


def main():
    """🎯 Main execution function for command line usage"""
    divine_print("🏛️ SUPREME UNIFIED SEEDING SERVICE 🏛️", "⚡")
    
    seeder = UnifiedSeedingService()
    
    # Test different seeding scenarios
    print("\n1. Quick Demo Seeding (10 users)")
    print("2. Full Demo Seeding (20 users)")  
    print("3. Production Seeding (50 users)")
    print("4. Test Emoji Support")
    
    choice = input("\nChoose seeding type (1-4): ").strip()
    
    if choice == "1":
        seeder.seed_all_data(user_count=10, opportunity_count=15, application_count=30)
    elif choice == "2":
        seeder.seed_all_data(user_count=20, opportunity_count=30, application_count=60)
    elif choice == "3":
        seeder.seed_all_data(user_count=50, opportunity_count=75, application_count=150)
    elif choice == "4":
        from utils.encoding_config import test_emoji_support
        test_emoji_support()
    else:
        divine_print("Invalid choice. Using default seeding.", "⚠️")
        seeder.seed_all_data()


if __name__ == "__main__":
    main()