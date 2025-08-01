"""
Comprehensive Database Seeding Service for Seraaj v2
Creates production-ready demo data for the MENA volunteer marketplace
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session, select
import logging

from database import get_session, engine
from models import (
    User, UserRole, UserStatus, Organisation, VolunteerProfile, 
    Opportunity, OpportunityStatus, Application, ApplicationStatus,
    Conversation, Message, AnalyticsRecord, ForumPost, ForumReply
)
from auth.password_utils import hash_password

logger = logging.getLogger(__name__)

class DatabaseSeeder:
    def __init__(self):
        self.session = next(get_session())
        
        # MENA-focused seed data
        self.countries = [
            {"en": "Egypt", "ar": "مصر", "code": "EG"},
            {"en": "Jordan", "ar": "الأردن", "code": "JO"},
            {"en": "Lebanon", "ar": "لبنان", "code": "LB"},
            {"en": "Palestine", "ar": "فلسطين", "code": "PS"},
            {"en": "UAE", "ar": "الإمارات", "code": "AE"},
            {"en": "Saudi Arabia", "ar": "السعودية", "code": "SA"},
            {"en": "Morocco", "ar": "المغرب", "code": "MA"},
            {"en": "Tunisia", "ar": "تونس", "code": "TN"},
            {"en": "Iraq", "ar": "العراق", "code": "IQ"},
            {"en": "Syria", "ar": "سوريا", "code": "SY"}
        ]
        
        self.cities = {
            "Egypt": [{"en": "Cairo", "ar": "القاهرة"}, {"en": "Alexandria", "ar": "الإسكندرية"}, {"en": "Giza", "ar": "الجيزة"}],
            "Jordan": [{"en": "Amman", "ar": "عمان"}, {"en": "Zarqa", "ar": "الزرقاء"}, {"en": "Irbid", "ar": "إربد"}],
            "Lebanon": [{"en": "Beirut", "ar": "بيروت"}, {"en": "Tripoli", "ar": "طرابلس"}, {"en": "Sidon", "ar": "صيدا"}],
            "Palestine": [{"en": "Gaza", "ar": "غزة"}, {"en": "Ramallah", "ar": "رام الله"}, {"en": "Nablus", "ar": "نابلس"}],
            "UAE": [{"en": "Dubai", "ar": "دبي"}, {"en": "Abu Dhabi", "ar": "أبو ظبي"}, {"en": "Sharjah", "ar": "الشارقة"}],
            "Saudi Arabia": [{"en": "Riyadh", "ar": "الرياض"}, {"en": "Jeddah", "ar": "جدة"}, {"en": "Mecca", "ar": "مكة"}],
            "Morocco": [{"en": "Casablanca", "ar": "الدار البيضاء"}, {"en": "Rabat", "ar": "الرباط"}, {"en": "Marrakech", "ar": "مراكش"}],
            "Tunisia": [{"en": "Tunis", "ar": "تونس"}, {"en": "Sfax", "ar": "صفاقس"}, {"en": "Sousse", "ar": "سوسة"}],
            "Iraq": [{"en": "Baghdad", "ar": "بغداد"}, {"en": "Basra", "ar": "البصرة"}, {"en": "Mosul", "ar": "الموصل"}],
            "Syria": [{"en": "Damascus", "ar": "دمشق"}, {"en": "Aleppo", "ar": "حلب"}, {"en": "Homs", "ar": "حمص"}]
        }
        
        self.causes = [
            {"en": "Education", "ar": "التعليم"}, {"en": "Healthcare", "ar": "الرعاية الصحية"},
            {"en": "Environment", "ar": "البيئة"}, {"en": "Youth Development", "ar": "تنمية الشباب"},
            {"en": "Women Empowerment", "ar": "تمكين المرأة"}, {"en": "Poverty Relief", "ar": "مكافحة الفقر"},
            {"en": "Refugee Support", "ar": "دعم اللاجئين"}, {"en": "Community Development", "ar": "التنمية المجتمعية"},
            {"en": "Digital Literacy", "ar": "الثقافة الرقمية"}, {"en": "Mental Health", "ar": "الصحة النفسية"},
            {"en": "Elder Care", "ar": "رعاية المسنين"}, {"en": "Child Protection", "ar": "حماية الطفل"}
        ]
        
        self.skills = [
            {"en": "Arabic Translation", "ar": "الترجمة العربية"}, {"en": "English Translation", "ar": "الترجمة الإنجليزية"},
            {"en": "Teaching", "ar": "التدريس"}, {"en": "Social Media", "ar": "وسائل التواصل الاجتماعي"},
            {"en": "Grant Writing", "ar": "كتابة المنح"}, {"en": "Event Planning", "ar": "تخطيط الفعاليات"},
            {"en": "Photography", "ar": "التصوير"}, {"en": "Graphic Design", "ar": "التصميم الجرافيكي"},
            {"en": "Web Development", "ar": "تطوير المواقع"}, {"en": "Project Management", "ar": "إدارة المشاريع"},
            {"en": "Fundraising", "ar": "جمع التبرعات"}, {"en": "Public Speaking", "ar": "التحدث أمام الجمهور"},
            {"en": "Research", "ar": "البحث"}, {"en": "Writing", "ar": "الكتابة"},
            {"en": "Marketing", "ar": "التسويق"}, {"en": "Data Analysis", "ar": "تحليل البيانات"}
        ]
        
        self.first_names = [
            "Ahmed", "Fatima", "Omar", "Layla", "Hassan", "Zeinab", "Khalid", "Amira",
            "Mohammad", "Dina", "Youssef", "Rana", "Ali", "Salma", "Karim", "Nour",
            "Mahmoud", "Maryam", "Ibrahim", "Yasmin", "Adel", "Heba", "Tareq", "Reem",
            "Sami", "Lina", "Walid", "Nada", "Fadi", "Jana", "Rami", "Lara"
        ]
        
        self.last_names = [
            "Al-Ahmad", "Hassan", "Al-Zahra", "Mansour", "Al-Rashid", "Khalil",
            "Al-Nouri", "Farouk", "Al-Mahmoud", "Taha", "Al-Sharif", "Nazir",
            "Al-Khatib", "Salah", "Al-Masri", "Qasemi", "Al-Amiri", "Habib",
            "Al-Zayed", "Kassem", "Al-Sabah", "Darwish", "Al-Mutawa", "Bishara"
        ]
        
        self.org_names = [
            {"en": "Hope Foundation", "ar": "مؤسسة الأمل"},
            {"en": "Unity Initiative", "ar": "مبادرة الوحدة"},
            {"en": "Future Leaders", "ar": "قادة المستقبل"},
            {"en": "Community Bridge", "ar": "جسر المجتمع"},
            {"en": "Rising Dawn", "ar": "الفجر الصاعد"},
            {"en": "Green Horizon", "ar": "الأفق الأخضر"},
            {"en": "Helping Hands", "ar": "الأيدي المساعدة"},
            {"en": "Bright Tomorrow", "ar": "غد مشرق"},
            {"en": "Open Hearts", "ar": "القلوب المفتوحة"},
            {"en": "Strong Roots", "ar": "الجذور القوية"},
            {"en": "New Path", "ar": "الطريق الجديد"},
            {"en": "Golden Circle", "ar": "الدائرة الذهبية"},
            {"en": "Rising Stars", "ar": "النجوم الصاعدة"},
            {"en": "Peace Builders", "ar": "بناة السلام"},
            {"en": "Dream Makers", "ar": "صناع الأحلام"}
        ]

    def get_random_item(self, items: List[Dict]) -> Dict:
        """Get random item from list"""
        return random.choice(items)

    def get_random_items(self, items: List[Dict], count: int) -> List[Dict]:
        """Get multiple random items from list"""
        return random.sample(items, min(count, len(items)))

    def generate_random_date(self, days_back: int) -> datetime:
        """Generate random date within specified days back"""
        return datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(0, days_back))


    def clear_existing_data(self):
        """Clear existing data from database"""
        logger.info("Clearing existing data...")
        
        # Delete in reverse dependency order
        self.session.query(Message).delete()
        self.session.query(Conversation).delete()
        self.session.query(ForumReply).delete()
        self.session.query(ForumPost).delete()
        self.session.query(AnalyticsRecord).delete()
        self.session.query(Application).delete()
        self.session.query(Opportunity).delete()
        self.session.query(VolunteerProfile).delete()
        self.session.query(Organisation).delete()
        self.session.query(User).delete()
        
        self.session.commit()
        logger.info("Existing data cleared")

    def create_mock_accounts(self) -> Dict[str, User]:
        """Create specific mock accounts for testing"""
        logger.info("Creating mock accounts...")
        
        mock_accounts = {}
        
        # Admin account
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@seraaj.com",
            hashed_password=hash_password("admin123"),
            first_name="System",
            last_name="Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc),
            last_login=datetime.now(datetime.timezone.utc)
        )
        self.session.add(admin)
        mock_accounts["admin"] = admin
        
        # Moderator account
        moderator = User(
            id=str(uuid.uuid4()),
            email="moderator@seraaj.com",
            hashed_password=hash_password("mod123"),
            first_name="Content",
            last_name="Moderator",
            role=UserRole.MODERATOR,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc)
        )
        self.session.add(moderator)
        mock_accounts["moderator"] = moderator
        
        # Active volunteer
        volunteer1 = User(
            id=str(uuid.uuid4()),
            email="volunteer1@demo.com",
            hashed_password=hash_password("vol123"),
            first_name="Fatima",
            last_name="Al-Zahra",
            role=UserRole.VOLUNTEER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=self.generate_random_date(365),
            last_login=self.generate_random_date(1)
        )
        self.session.add(volunteer1)
        mock_accounts["volunteer1"] = volunteer1
        
        # New volunteer
        volunteer2 = User(
            id=str(uuid.uuid4()),
            email="volunteer2@demo.com",
            hashed_password=hash_password("vol123"),
            first_name="Ahmed",
            last_name="Hassan",
            role=UserRole.VOLUNTEER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=self.generate_random_date(30),
            last_login=self.generate_random_date(1)
        )
        self.session.add(volunteer2)
        mock_accounts["volunteer2"] = volunteer2
        
        # Large organization
        org1_user = User(
            id=str(uuid.uuid4()),
            email="org1@demo.com",
            hashed_password=hash_password("org123"),
            first_name="Organization",
            last_name="Manager",
            role=UserRole.ORGANIZATION,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=self.generate_random_date(730)
        )
        self.session.add(org1_user)
        mock_accounts["org1"] = org1_user
        
        # Small organization
        org2_user = User(
            id=str(uuid.uuid4()),
            email="org2@demo.com",
            hashed_password=hash_password("org123"),
            first_name="Small Nonprofit",
            last_name="Coordinator",
            role=UserRole.ORGANIZATION,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=self.generate_random_date(180)
        )
        self.session.add(org2_user)
        mock_accounts["org2"] = org2_user
        
        self.session.commit()
        logger.info(f"Created {len(mock_accounts)} mock accounts")
        return mock_accounts

    def create_organizations(self, mock_accounts: Dict[str, User]) -> List[Organisation]:
        """Create organization profiles"""
        logger.info("Creating organizations...")
        
        organizations = []
        
        # Create organizations for mock accounts
        org1 = Organisation(
            id=str(uuid.uuid4()),
            user_id=mock_accounts["org1"].id,
            name="Hope Foundation Egypt",
            name_ar="مؤسسة الأمل مصر",
            description="Leading nonprofit organization focused on education and youth development across Egypt and the MENA region.",
            description_ar="منظمة غير ربحية رائدة تركز على التعليم وتنمية الشباب في مصر ومنطقة الشرق الأوسط وشمال أفريقيا.",
            logo_url="/logos/hope-foundation.png",
            website="https://hopefoundation.eg",
            phone="+20123456789",
            address="123 Tahrir Square, Cairo, Egypt",
            address_ar="123 ميدان التحرير، القاهرة، مصر",
            city="Cairo",
            city_ar="القاهرة",
            country="Egypt",
            country_ar="مصر",
            established_year=2010,
            team_size="50-100",
            causes=["Education", "Youth Development", "Community Development"],
            is_verified=True,
            verification_date=datetime.now(datetime.timezone.utc),
            rating=4.8,
            total_volunteers=250,
            active_opportunities=15,
            created_at=self.generate_random_date(730)
        )
        self.session.add(org1)
        organizations.append(org1)
        
        org2 = Organisation(
            id=str(uuid.uuid4()),
            user_id=mock_accounts["org2"].id,
            name="Green Horizon Jordan",
            name_ar="الأفق الأخضر الأردن",
            description="Environmental nonprofit working on sustainability and climate action in Jordan.",
            description_ar="منظمة بيئية غير ربحية تعمل على الاستدامة والعمل المناخي في الأردن.",
            logo_url="/logos/green-horizon.png",
            website="https://greenhorizon.jo",
            phone="+962987654321",
            address="456 Rainbow Street, Amman, Jordan",
            address_ar="456 شارع الرينبو، عمان، الأردن",
            city="Amman",
            city_ar="عمان",
            country="Jordan",
            country_ar="الأردن",
            established_year=2018,
            team_size="10-25",
            causes=["Environment", "Community Development"],
            is_verified=True,
            verification_date=datetime.now(datetime.timezone.utc),
            rating=4.2,
            total_volunteers=85,
            active_opportunities=6,
            created_at=self.generate_random_date(180)
        )
        self.session.add(org2)
        organizations.append(org2)
        
        # Create additional organizations
        for i in range(48):  # Total 50 organizations
            country = self.get_random_item(self.countries)
            city = self.get_random_item(self.cities.get(country["en"], [{"en": "Capital", "ar": "العاصمة"}]))
            org_name = self.get_random_item(self.org_names)
            causes = self.get_random_items(self.causes, random.randint(2, 4))
            
            # Create user for organization
            user = User(
                id=str(uuid.uuid4()),
                email=f"org{i+3}@example.com",
                hashed_password=hash_password(f"password{i+3}"),
                first_name=f"Manager",
                last_name=f"{org_name['en']}",
                role=UserRole.ORGANIZATION,
                status=UserStatus.ACTIVE,
                is_verified=random.random() > 0.2,
                created_at=self.generate_random_date(random.randint(90, 1095))
            )
            self.session.add(user)
            
            org = Organisation(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=f"{org_name['en']} {country['en']}",
                name_ar=f"{org_name['ar']} {country['ar']}",
                description=f"Empowering communities through innovative programs and sustainable development initiatives in {country['en']}.",
                description_ar=f"تمكين المجتمعات من خلال البرامج المبتكرة ومبادرات التنمية المستدامة في {country['ar']}.",
                logo_url=f"/logos/org-{i+3}.png",
                website=f"https://{org_name['en'].lower().replace(' ', '')}.{country['code'].lower()}",
                phone=f"+{random.randint(20, 971)}{random.randint(100000000, 999999999)}",
                address=f"{random.randint(1, 999)} Main Street, {city['en']}, {country['en']}",
                address_ar=f"{random.randint(1, 999)} الشارع الرئيسي، {city['ar']}، {country['ar']}",
                city=city["en"],
                city_ar=city["ar"],
                country=country["en"],
                country_ar=country["ar"],
                established_year=random.randint(2005, 2020),
                team_size=random.choice(["5-10", "10-25", "25-50", "50-100"]),
                causes=[cause["en"] for cause in causes],
                is_verified=random.random() > 0.3,
                verification_date=datetime.now(datetime.timezone.utc) if random.random() > 0.3 else None,
                rating=round(random.uniform(3.5, 5.0), 1),
                total_volunteers=random.randint(20, 300),
                active_opportunities=random.randint(2, 20),
                created_at=self.generate_random_date(random.randint(90, 1095))
            )
            self.session.add(org)
            organizations.append(org)
        
        self.session.commit()
        logger.info(f"Created {len(organizations)} organizations")
        return organizations

    def create_volunteers(self, mock_accounts: Dict[str, User]) -> List[VolunteerProfile]:
        """Create volunteer profiles"""
        logger.info("Creating volunteer profiles...")
        
        volunteers = []
        
        # Create profiles for mock volunteers
        vol1_profile = VolunteerProfile(
            id=str(uuid.uuid4()),
            user_id=mock_accounts["volunteer1"].id,
            bio="Experienced educator and community organizer passionate about empowering women and youth in the MENA region. Fluent in Arabic and English with 5+ years of volunteer experience.",
            bio_ar="مربية ومنظمة مجتمعية ذات خبرة شغوفة بتمكين المرأة والشباب في منطقة الشرق الأوسط وشمال أفريقيا. تتقن العربية والإنجليزية مع أكثر من 5 سنوات من الخبرة التطوعية.",
            location="Cairo, Egypt",
            location_ar="القاهرة، مصر",
            skills=["Teaching", "Arabic Translation", "Event Planning", "Public Speaking"],
            interests=["Education", "Women Empowerment", "Youth Development"],
            languages=["Arabic", "English", "French"],
            availability="part-time",
            experience_level="expert",
            phone="+201234567890",
            linkedin_url="https://linkedin.com/in/fatima-alzahra",
            portfolio_url="https://fatima-portfolio.com",
            emergency_contact_name="Omar Al-Zahra",
            emergency_contact_phone="+201987654321",
            date_of_birth=datetime(1990, 5, 15),
            education_level="bachelor",
            profession="Teacher",
            has_car=True,
            can_travel=True,
            background_check_status="approved",
            background_check_date=datetime.now(datetime.timezone.utc),
            total_hours=450,
            completed_opportunities=15,
            rating=4.9,
            is_featured=True,
            created_at=self.generate_random_date(365)
        )
        self.session.add(vol1_profile)
        volunteers.append(vol1_profile)
        
        vol2_profile = VolunteerProfile(
            id=str(uuid.uuid4()),
            user_id=mock_accounts["volunteer2"].id,
            bio="Recent graduate eager to contribute to social causes and gain experience in nonprofit work. Strong background in digital marketing and social media.",
            bio_ar="خريج حديث متحمس للمساهمة في القضايا الاجتماعية واكتساب الخبرة في العمل غير الربحي. خلفية قوية في التسويق الرقمي ووسائل التواصل الاجتماعي.",
            location="Amman, Jordan",
            location_ar="عمان، الأردن",
            skills=["Social Media", "Graphic Design", "Writing", "Marketing"],
            interests=["Youth Development", "Digital Literacy", "Community Development"],
            languages=["Arabic", "English"],
            availability="flexible",
            experience_level="beginner",
            phone="+962987654321",
            linkedin_url="https://linkedin.com/in/ahmed-hassan",
            date_of_birth=datetime(1998, 8, 22),
            education_level="bachelor",
            profession="Marketing Coordinator",
            has_car=False,
            can_travel=False,
            background_check_status="pending",
            total_hours=25,
            completed_opportunities=2,
            rating=4.3,
            is_featured=False,
            created_at=self.generate_random_date(30)
        )
        self.session.add(vol2_profile)
        volunteers.append(vol2_profile)
        
        # Create additional volunteers
        for i in range(198):  # Total 200 volunteers
            country = self.get_random_item(self.countries)
            city = self.get_random_item(self.cities.get(country["en"], [{"en": "Capital", "ar": "العاصمة"}]))
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            skills = self.get_random_items(self.skills, random.randint(2, 6))
            interests = self.get_random_items(self.causes, random.randint(2, 4))
            
            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=f"{first_name.lower()}.{last_name.lower().replace('al-', '')}@example.com",
                hashed_password=hash_password(f"password{i+3}"),
                first_name=first_name,
                last_name=last_name,
                role=UserRole.VOLUNTEER,
                status=UserStatus.ACTIVE,
                is_verified=random.random() > 0.4,
                created_at=self.generate_random_date(random.randint(1, 730))
            )
            self.session.add(user)
            
            # Create volunteer profile
            volunteer = VolunteerProfile(
                id=str(uuid.uuid4()),
                user_id=user.id,
                bio=f"Passionate volunteer committed to making a positive impact in {country['en']} through community engagement and social work.",
                bio_ar=f"متطوع شغوف ملتزم بإحداث تأثير إيجابي في {country['ar']} من خلال المشاركة المجتمعية والعمل الاجتماعي.",
                location=f"{city['en']}, {country['en']}",
                location_ar=f"{city['ar']}، {country['ar']}",
                skills=[skill["en"] for skill in skills],
                interests=[interest["en"] for interest in interests],
                languages=random.sample(["Arabic", "English", "French", "Spanish"], random.randint(1, 3)),
                availability=random.choice(["full-time", "part-time", "weekends", "flexible"]),
                experience_level=random.choice(["beginner", "intermediate", "expert"]),
                phone=f"+{random.randint(20, 971)}{random.randint(100000000, 999999999)}",
                date_of_birth=datetime(random.randint(1980, 2002), random.randint(1, 12), random.randint(1, 28)),
                education_level=random.choice(["high_school", "bachelor", "master", "phd"]),
                profession=random.choice(["Student", "Teacher", "Engineer", "Designer", "Developer", "Manager", "Consultant"]),
                has_car=random.random() > 0.6,
                can_travel=random.random() > 0.7,
                background_check_status=random.choice(["approved", "pending", "rejected"]),
                background_check_date=datetime.now(datetime.timezone.utc) if random.random() > 0.5 else None,
                total_hours=random.randint(0, 500),
                completed_opportunities=random.randint(0, 20),
                rating=round(random.uniform(3.0, 5.0), 1),
                is_featured=random.random() > 0.9,
                created_at=self.generate_random_date(random.randint(1, 730))
            )
            self.session.add(volunteer)
            volunteers.append(volunteer)
        
        self.session.commit()
        logger.info(f"Created {len(volunteers)} volunteer profiles")
        return volunteers

    def seed_all_data(self):
        """Main method to seed all data"""
        logger.info("Starting comprehensive database seeding...")
        
        try:
            # Clear existing data
            self.clear_existing_data()
            
            # Create mock accounts
            mock_accounts = self.create_mock_accounts()
            
            # Create organizations
            organizations = self.create_organizations(mock_accounts)
            
            # Create volunteers  
            volunteers = self.create_volunteers(mock_accounts)
            
            # Create opportunities
            opportunities = self.create_opportunities(organizations)
            
            # Create applications
            applications = self.create_applications(volunteers, opportunities)
            
            # Create conversations and messages
            conversations, messages = self.create_conversations_and_messages(volunteers, organizations)
            
            # Create forum posts and replies
            posts, replies = self.create_forum_content(mock_accounts, volunteers, organizations)
            
            # Create analytics records
            analytics = self.create_analytics_records(volunteers, organizations, opportunities)
            
            logger.info("Database seeding completed successfully!")
            logger.info(f"Created: {len(mock_accounts)} mock accounts, {len(organizations)} organizations, {len(volunteers)} volunteers")
            logger.info(f"Created: {len(opportunities)} opportunities, {len(applications)} applications")
            logger.info(f"Created: {len(conversations)} conversations, {len(messages)} messages")
            logger.info(f"Created: {len(posts)} forum posts, {len(replies)} replies, {len(analytics)} analytics records")
            
        except Exception as e:
            logger.error(f"Error during database seeding: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def create_opportunities(self, organizations: List[Organisation]) -> List[Opportunity]:
        """Create volunteer opportunities"""
        logger.info("Creating opportunities...")
        
        opportunities = []
        
        opportunity_titles = [
            {"en": "Community Outreach Coordinator", "ar": "منسق التوعية المجتمعية"},
            {"en": "Digital Marketing Specialist", "ar": "أخصائي التسويق الرقمي"},
            {"en": "Youth Mentor", "ar": "موجه الشباب"},
            {"en": "Event Planning Assistant", "ar": "مساعد تخطيط الفعاليات"},
            {"en": "Research Volunteer", "ar": "متطوع بحث"},
            {"en": "Translation Services", "ar": "خدمات الترجمة"},
            {"en": "Photography Volunteer", "ar": "متطوع تصوير"},
            {"en": "Fundraising Campaign Manager", "ar": "مدير حملة جمع التبرعات"},
            {"en": "Workshop Facilitator", "ar": "ميسر ورشة عمل"},
            {"en": "Social Media Content Creator", "ar": "منشئ محتوى وسائل التواصل الاجتماعي"},
            {"en": "Grant Writing Specialist", "ar": "أخصائي كتابة المنح"},
            {"en": "Program Assistant", "ar": "مساعد برنامج"},
            {"en": "English Teacher", "ar": "مدرس لغة إنجليزية"},
            {"en": "Computer Skills Trainer", "ar": "مدرب مهارات الحاسوب"},
            {"en": "Environmental Awareness Coordinator", "ar": "منسق التوعية البيئية"}
        ]
        
        for i in range(150):
            org = random.choice(organizations)
            title = self.get_random_item(opportunity_titles)
            skills = self.get_random_items(self.skills, random.randint(2, 5))
            causes = random.sample(org.causes, min(random.randint(1, 2), len(org.causes)))
            
            start_date = self.generate_random_date(-random.randint(5, 60))  # Future dates
            end_date = start_date + timedelta(days=random.randint(30, 365))
            
            opportunity = Opportunity(
                id=str(uuid.uuid4()),
                org_id=org.id,
                title=title["en"],
                description=f"Join our team to make a meaningful impact through {title['en'].lower()} work with {org.name}. This role involves working directly with our community members to deliver essential services and support.",
                skills_required=[skill["en"] for skill in skills],
                skills_weighted={skill["en"]: random.randint(1, 5) for skill in skills},
                categories_weighted={cause: random.randint(1, 3) for cause in causes},
                availability_required={
                    "monday": random.sample(["morning", "afternoon", "evening"], random.randint(1, 2)),
                    "tuesday": random.sample(["morning", "afternoon", "evening"], random.randint(0, 2)),
                    "wednesday": random.sample(["morning", "afternoon", "evening"], random.randint(1, 2))
                },
                min_hours=random.randint(2, 20),
                start_date=start_date.date(),
                end_date=end_date.date(),
                is_remote=random.random() > 0.7,
                status=random.choice([OpportunityStatus.OPEN, OpportunityStatus.OPEN, OpportunityStatus.OPEN, OpportunityStatus.FILLED, OpportunityStatus.CLOSED])
            )
            self.session.add(opportunity)
            opportunities.append(opportunity)
        
        self.session.commit()
        logger.info(f"Created {len(opportunities)} opportunities")
        return opportunities

    def create_applications(self, volunteers: List[VolunteerProfile], opportunities: List[Opportunity]) -> List[Application]:
        """Create volunteer applications"""
        logger.info("Creating applications...")
        
        applications = []
        
        # Create 500 applications
        for i in range(500):
            volunteer = random.choice(volunteers)
            # Only apply to open opportunities
            open_opportunities = [opp for opp in opportunities if opp.status == OpportunityStatus.OPEN]
            if not open_opportunities:
                continue
                
            opportunity = random.choice(open_opportunities)
            
            # Avoid duplicate applications
            existing = any(app.volunteer_id == volunteer.user_id and app.opportunity_id == opportunity.id 
                          for app in applications)
            if existing:
                continue
            
            application = Application(
                id=str(uuid.uuid4()),
                volunteer_id=volunteer.user_id,
                opportunity_id=opportunity.id,
                status=random.choice([ApplicationStatus.PENDING, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]),
                match_score=random.uniform(0.6, 1.0),
                applied_at=self.generate_random_date(60)
            )
            self.session.add(application)
            applications.append(application)
        
        self.session.commit()
        logger.info(f"Created {len(applications)} applications")
        return applications

    def create_conversations_and_messages(self, volunteers: List[VolunteerProfile], organizations: List[Organisation]) -> tuple:
        """Create conversations and messages"""
        logger.info("Creating conversations and messages...")
        
        conversations = []
        messages = []
        
        message_templates = [
            "Hello, I'm interested in learning more about this volunteer opportunity.",
            "Thank you for your application. We'd like to schedule an interview.",
            "I have some questions about the time commitment required.",
            "Great! I look forward to contributing to your mission.",
            "Could you tell me more about the training provided?",
            "When would be a good time to start?",
            "Do you provide any certificates upon completion?",
            "I'm excited to be part of your team!",
            "What are the next steps in the process?",
            "Thank you for considering my application."
        ]
        
        # Create 300 conversations
        for i in range(300):
            volunteer = random.choice(volunteers)
            organization = random.choice(organizations)
            
            conversation = Conversation(
                id=str(uuid.uuid4()),
                participant_ids=[volunteer.user_id, organization.user_id]
            )
            self.session.add(conversation)
            conversations.append(conversation)
            
            # Create 2-5 messages per conversation
            message_count = random.randint(2, 5)
            for j in range(message_count):
                sender_id = volunteer.user_id if j % 2 == 0 else organization.user_id
                
                message = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation.id,
                    sender_id=sender_id,
                    content=random.choice(message_templates),
                    timestamp=self.generate_random_date(14)
                )
                self.session.add(message)
                messages.append(message)
        
        self.session.commit()
        logger.info(f"Created {len(conversations)} conversations and {len(messages)} messages")
        return conversations, messages

    def create_forum_content(self, mock_accounts: Dict[str, User], volunteers: List[VolunteerProfile], organizations: List[Organisation]) -> tuple:
        """Create forum posts and replies"""
        logger.info("Creating forum content...")
        
        posts = []
        replies = []
        
        post_titles = [
            "Best practices for volunteer onboarding",
            "How to measure volunteer impact effectively",
            "Building long-term volunteer relationships",
            "Using technology to enhance volunteer experiences",
            "Volunteer recognition and appreciation ideas",
            "Managing remote volunteers successfully",
            "Creating inclusive volunteer programs",
            "Fundraising strategies for small nonprofits",
            "Social media tips for nonprofit organizations",
            "Volunteer recruitment in the digital age"
        ]
        
        # Create forum posts
        for i in range(20):
            # Random author from volunteers or organizations
            all_users = [v.user_id for v in volunteers[:10]] + [o.user_id for o in organizations[:5]]
            author_id = random.choice(all_users)
            
            post = ForumPost(
                id=str(uuid.uuid4()),
                author_id=author_id,
                title=random.choice(post_titles),
                content=f"This is a detailed discussion about {random.choice(post_titles).lower()}. I'd love to hear your thoughts and experiences on this topic.",
                created_at=self.generate_random_date(90),
                upvotes=random.randint(0, 50),
                downvotes=random.randint(0, 5)
            )
            self.session.add(post)
            posts.append(post)
            
            # Create replies for each post
            reply_count = random.randint(1, 8)
            for j in range(reply_count):
                reply_author_id = random.choice(all_users)
                
                reply = ForumReply(
                    id=str(uuid.uuid4()),
                    post_id=post.id,
                    author_id=reply_author_id,
                    content=f"Thank you for sharing this. In my experience, {random.choice(['this approach works well', 'I\'ve found success with', 'it\'s important to consider', 'we should also think about'])}...",
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48)),
                    upvotes=random.randint(0, 20),
                    downvotes=random.randint(0, 2)
                )
                self.session.add(reply)
                replies.append(reply)
        
        self.session.commit()
        logger.info(f"Created {len(posts)} forum posts and {len(replies)} replies")
        return posts, replies

    def create_analytics_records(self, volunteers: List[VolunteerProfile], organizations: List[Organisation], opportunities: List[Opportunity]) -> List[AnalyticsRecord]:
        """Create analytics records"""
        logger.info("Creating analytics records...")
        
        analytics = []
        
        # Create analytics records for completed volunteer work
        for i in range(200):
            volunteer = random.choice(volunteers)
            organization = random.choice(organizations)
            opportunity = random.choice(opportunities)
            
            record = AnalyticsRecord(
                id=str(uuid.uuid4()),
                volunteer_id=volunteer.user_id,
                organization_id=organization.user_id,
                opportunity_id=opportunity.id,
                hours=random.randint(1, 40),
                metrics={
                    "satisfaction_rating": random.randint(3, 5),
                    "skills_gained": random.randint(1, 5),
                    "impact_rating": random.randint(3, 5),
                    "would_recommend": random.random() > 0.2
                },
                created_at=self.generate_random_date(365)
            )
            self.session.add(record)
            analytics.append(record)
        
        self.session.commit()
        logger.info(f"Created {len(analytics)} analytics records")
        return analytics


def seed_database():
    """Main function to seed the database"""
    seeder = DatabaseSeeder()
    seeder.seed_all_data()


if __name__ == "__main__":
    seed_database()