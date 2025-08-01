"""
Unified Seeding Service for Seraaj v2
The ONE service to rule all data seeding

This service centralizes ALL seeding functionality:
- Demo users creation (documented accounts)
- Test data generation
- Production-ready seeding
- Database population
- Analytics data generation

Replaces: simple_seed.py, database_seeding.py, utils/data_seeder.py
"""

import os
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
import logging

from database import get_session, create_db_and_tables
from models import (
    User,
    UserRole,
    UserStatus,
    Volunteer,
    Organisation,
    Opportunity,
    OpportunityState,
    Application,
    ApplicationStatus,
    Conversation,
    Message,
    Review,
    AnalyticsEvent,
)
from auth.password_utils import hash_password

logger = logging.getLogger(__name__)


class UnifiedSeedingService:
    """The centralized seeding service for all Seraaj data population needs"""

    def __init__(self):
        self.session = next(get_session())
        logger.info("Unified Seeding Service initialized")

        # MENA-focused realistic data
        self.countries = [
            {"en": "Egypt", "ar": "مصر", "code": "EG"},
            {"en": "Jordan", "ar": "الأردن", "code": "JO"},
            {"en": "Lebanon", "ar": "لبنان", "code": "LB"},
            {"en": "UAE", "ar": "الإمارات", "code": "AE"},
            {"en": "Morocco", "ar": "المغرب", "code": "MA"},
            {"en": "Tunisia", "ar": "تونس", "code": "TN"},
            {"en": "Palestine", "ar": "فلسطين", "code": "PS"},
            {"en": "Saudi Arabia", "ar": "السعودية", "code": "SA"},
        ]

        self.cities = {
            "Egypt": [
                {"en": "Cairo", "ar": "القاهرة"},
                {"en": "Alexandria", "ar": "الإسكندرية"},
            ],
            "Jordan": [{"en": "Amman", "ar": "عمان"}, {"en": "Zarqa", "ar": "الزرقاء"}],
            "Lebanon": [
                {"en": "Beirut", "ar": "بيروت"},
                {"en": "Tripoli", "ar": "طرابلس"},
            ],
            "UAE": [{"en": "Dubai", "ar": "دبي"}, {"en": "Abu Dhabi", "ar": "أبو ظبي"}],
            "Morocco": [
                {"en": "Casablanca", "ar": "الدار البيضاء"},
                {"en": "Rabat", "ar": "الرباط"},
            ],
            "Tunisia": [{"en": "Tunis", "ar": "تونس"}, {"en": "Sfax", "ar": "صفاقس"}],
            "Palestine": [
                {"en": "Gaza", "ar": "غزة"},
                {"en": "Ramallah", "ar": "رام الله"},
            ],
            "Saudi Arabia": [
                {"en": "Riyadh", "ar": "الرياض"},
                {"en": "Jeddah", "ar": "جدة"},
            ],
        }

        self.causes = [
            {"en": "Education", "ar": "التعليم"},
            {"en": "Healthcare", "ar": "الرعاية الصحية"},
            {"en": "Environment", "ar": "البيئة"},
            {"en": "Community Development", "ar": "التنمية المجتمعية"},
            {"en": "Women Empowerment", "ar": "تمكين المرأة"},
            {"en": "Youth Development", "ar": "تنمية الشباب"},
            {"en": "Digital Inclusion", "ar": "الشمول الرقمي"},
            {"en": "Refugee Support", "ar": "دعم اللاجئين"},
            {"en": "Emergency Relief", "ar": "الإغاثة الطارئة"},
            {"en": "Technology Training", "ar": "التدريب التقني"},
        ]

        self.skills = [
            {"en": "Technology Training", "ar": "التدريب التقني"},
            {"en": "Web Development", "ar": "تطوير المواقع"},
            {"en": "Arabic Language", "ar": "اللغة العربية"},
            {"en": "English Language", "ar": "اللغة الإنجليزية"},
            {"en": "French Language", "ar": "اللغة الفرنسية"},
            {"en": "Youth Mentoring", "ar": "توجيه الشباب"},
            {"en": "Healthcare", "ar": "الرعاية الصحية"},
            {"en": "Emergency Response", "ar": "الاستجابة للطوارئ"},
            {"en": "Community Outreach", "ar": "التوعية المجتمعية"},
            {"en": "Teaching", "ar": "التدريس"},
            {"en": "Social Work", "ar": "العمل الاجتماعي"},
            {"en": "Grant Writing", "ar": "كتابة المنح"},
            {"en": "Project Management", "ar": "إدارة المشاريع"},
            {"en": "Data Analysis", "ar": "تحليل البيانات"},
            {"en": "Social Media", "ar": "وسائل التواصل الاجتماعي"},
            {"en": "Event Planning", "ar": "تخطيط الفعاليات"},
            {"en": "Photography", "ar": "التصوير"},
            {"en": "Graphic Design", "ar": "التصميم الجرافيكي"},
            {"en": "Marketing", "ar": "التسويق"},
            {"en": "Fundraising", "ar": "جمع التبرعات"},
        ]

        self.demo_password = "Demo123!"

    def clear_existing_data(self):
        """Clear existing data from database"""
        logger.info("Clearing existing data...")

        # Delete in reverse dependency order to avoid foreign key constraints
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
        logger.info("Existing data cleared")

    def create_demo_accounts(self) -> Dict[str, User]:
        """Create the specific demo accounts documented in DEMO_ACCOUNTS.md"""
        logger.info("Creating documented demo accounts...")

        demo_accounts = {}

        # Admin account
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@seraaj.org",
            hashed_password=hash_password(self.demo_password),
            first_name="Platform",
            last_name="Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc),
        )
        self.session.add(admin)
        demo_accounts["admin"] = admin

        # Volunteer: Layla Al-Mansouri - Tech Professional
        layla = User(
            id=str(uuid.uuid4()),
            email="layla@example.com",
            hashed_password=hash_password(self.demo_password),
            first_name="Layla",
            last_name="Al-Mansouri",
            role=UserRole.VOLUNTEER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=365),
        )
        self.session.add(layla)
        demo_accounts["layla"] = layla

        # Volunteer: Omar Hassan - Healthcare Professional
        omar = User(
            id=str(uuid.uuid4()),
            email="omar@example.com",
            hashed_password=hash_password(self.demo_password),
            first_name="Omar",
            last_name="Hassan",
            role=UserRole.VOLUNTEER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=300),
        )
        self.session.add(omar)
        demo_accounts["omar"] = omar

        # Volunteer: Fatima Al-Zahra - Recent Graduate
        fatima = User(
            id=str(uuid.uuid4()),
            email="fatima@example.com",
            hashed_password=hash_password(self.demo_password),
            first_name="Fatima",
            last_name="Al-Zahra",
            role=UserRole.VOLUNTEER,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=90),
        )
        self.session.add(fatima)
        demo_accounts["fatima"] = fatima

        # Organization: Hope Education Initiative
        hope_edu = User(
            id=str(uuid.uuid4()),
            email="contact@hopeeducation.org",
            hashed_password=hash_password(self.demo_password),
            first_name="Hope Education",
            last_name="Initiative",
            role=UserRole.ORGANIZATION,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=730),
        )
        self.session.add(hope_edu)
        demo_accounts["hope_edu"] = hope_edu

        # Organization: Cairo Community Health Network
        cairo_health = User(
            id=str(uuid.uuid4()),
            email="info@cairohealthnetwork.org",
            hashed_password=hash_password(self.demo_password),
            first_name="Cairo Community",
            last_name="Health Network",
            role=UserRole.ORGANIZATION,
            status=UserStatus.ACTIVE,
            is_verified=True,
            created_at=datetime.now(datetime.timezone.utc) - timedelta(days=1095),
        )
        self.session.add(cairo_health)
        demo_accounts["cairo_health"] = cairo_health

        self.session.commit()
        logger.info(f"Created {len(demo_accounts)} demo accounts")
        return demo_accounts

    def create_demo_volunteers(self, demo_accounts: Dict[str, User]):
        """Create volunteer profiles for demo accounts"""
        logger.info("Creating demo volunteer profiles...")

        # Layla Al-Mansouri - Tech Professional
        layla_profile = Volunteer(
            user_id=demo_accounts["layla"].id,
            full_name="Layla Al-Mansouri",
            full_name_ar="ليلى المنصوري",
            bio="Software Engineer at Emirates Group. Born in Lebanon, raised in Dubai. Passionate about bridging the digital divide in underserved communities. Fluent in Arabic, English, and French.",
            bio_ar="مهندسة برمجيات في مجموعة الإمارات. وُلدت في لبنان ونشأت في دبي. شغوفة بسد الفجوة الرقمية في المجتمعات المحرومة. تتقن العربية والإنجليزية والفرنسية.",
            location="Dubai, UAE",
            location_ar="دبي، الإمارات",
            country="UAE",
            country_ar="الإمارات",
            skills=[
                "Technology Training",
                "Web Development",
                "Arabic Language",
                "English Language",
                "Youth Mentoring",
            ],
            interests=["Digital Inclusion", "Education", "Refugee Support"],
            languages=["Arabic", "English", "French"],
            availability=AvailabilityType.WEEKENDS,
            experience_level=ExperienceLevel.INTERMEDIATE,
            time_commitment_hours=10,
            verified=True,
            rating=4.8,
            total_reviews=15,
            completed_opportunities=8,
            total_volunteer_hours=250,
        )
        self.session.add(layla_profile)

        # Omar Hassan - Healthcare Professional
        omar_profile = Volunteer(
            id=str(uuid.uuid4()),
            user_id=demo_accounts["omar"].id,
            bio="Emergency medicine physician at Cairo University Hospital. Grew up in a working-class neighborhood in Cairo. Deeply committed to healthcare equity.",
            bio_ar="طبيب طوارئ في مستشفى جامعة القاهرة. نشأ في حي شعبي في القاهرة. ملتزم بعمق بالعدالة الصحية.",
            location="Cairo, Egypt",
            location_ar="القاهرة، مصر",
            skills=[
                "Healthcare",
                "Emergency Response",
                "Community Outreach",
                "Teaching",
                "Arabic Language",
            ],
            interests=["Healthcare", "Emergency Relief", "Community Development"],
            languages=["Arabic", "English"],
            availability="flexible",
            experience_level="expert",
            phone="+201234567890",
            profession="Medical Doctor",
            education_level="phd",
            has_car=True,
            can_travel=True,
            total_hours=400,
            completed_opportunities=12,
            rating=4.9,
            is_featured=True,
            created_at=demo_accounts["omar"].created_at,
        )
        self.session.add(omar_profile)

        # Fatima Al-Zahra - Recent Graduate
        fatima_profile = Volunteer(
            id=str(uuid.uuid4()),
            user_id=demo_accounts["fatima"].id,
            bio="Recent university graduate passionate about women's rights and education. Daughter of Palestinian refugees, she understands the power of education to transform lives.",
            bio_ar="خريجة جامعية حديثة شغوفة بحقوق المرأة والتعليم. ابنة لاجئين فلسطينيين، تفهم قوة التعليم في تغيير الحياة.",
            location="Amman, Jordan",
            location_ar="عمان، الأردن",
            skills=[
                "Teaching",
                "English Language",
                "Social Work",
                "Grant Writing",
                "Youth Mentoring",
            ],
            interests=[
                "Women Empowerment",
                "Education",
                "Refugee Support",
                "Youth Development",
            ],
            languages=["Arabic", "English"],
            availability="full-time",
            experience_level="beginner",
            phone="+962787654321",
            profession="Recent Graduate",
            education_level="bachelor",
            has_car=False,
            can_travel=False,
            total_hours=50,
            completed_opportunities=3,
            rating=4.5,
            is_featured=False,
            created_at=demo_accounts["fatima"].created_at,
        )
        self.session.add(fatima_profile)

        self.session.commit()
        logger.info("Created demo volunteer profiles")

    def create_demo_organizations(self, demo_accounts: Dict[str, User]):
        """Create organization profiles for demo accounts"""
        logger.info("Creating demo organization profiles...")

        # Hope Education Initiative
        hope_edu_org = Organisation(
            id=str(uuid.uuid4()),
            user_id=demo_accounts["hope_edu"].id,
            name="Hope Education Initiative",
            name_ar="مبادرة الأمل للتعليم",
            description="Founded by a group of educators and tech professionals to address educational inequality in the UAE and broader MENA region. Focuses on STEM education for underprivileged youth and digital literacy for adults.",
            description_ar="تأسست من قبل مجموعة من المعلمين والمهنيين التقنيين لمعالجة عدم المساواة التعليمية في دولة الإمارات ومنطقة الشرق الأوسط وشمال أفريقيا الأوسع.",
            logo_url="/logos/hope-education.png",
            website="https://hopeeducation.org",
            phone="+971507654321",
            address="Dubai Knowledge Park, Dubai, UAE",
            address_ar="حديقة دبي للمعرفة، دبي، الإمارات",
            city="Dubai",
            city_ar="دبي",
            country="UAE",
            country_ar="الإمارات",
            established_year=2018,
            team_size="25-50",
            causes=["Education", "Digital Inclusion", "Youth Development"],
            is_verified=True,
            verification_date=datetime.now(datetime.timezone.utc),
            rating=4.7,
            total_volunteers=150,
            active_opportunities=8,
            created_at=demo_accounts["hope_edu"].created_at,
        )
        self.session.add(hope_edu_org)

        # Cairo Community Health Network
        cairo_health_org = Organisation(
            id=str(uuid.uuid4()),
            user_id=demo_accounts["cairo_health"].id,
            name="Cairo Community Health Network",
            name_ar="شبكة القاهرة للصحة المجتمعية",
            description="Healthcare network serving Cairo's underserved neighborhoods. Started by a group of doctors and nurses committed to healthcare equity. Operates mobile clinics and community health programs.",
            description_ar="شبكة رعاية صحية تخدم أحياء القاهرة المحرومة. بدأت من قبل مجموعة من الأطباء والممرضات الملتزمين بالعدالة الصحية.",
            logo_url="/logos/cairo-health.png",
            website="https://cairohealthnetwork.org",
            phone="+201098765432",
            address="Downtown Cairo, Cairo, Egypt",
            address_ar="وسط القاهرة، القاهرة، مصر",
            city="Cairo",
            city_ar="القاهرة",
            country="Egypt",
            country_ar="مصر",
            established_year=2010,
            team_size="50-100",
            causes=["Healthcare", "Community Development", "Emergency Relief"],
            is_verified=True,
            verification_date=datetime.now(datetime.timezone.utc),
            rating=4.9,
            total_volunteers=300,
            active_opportunities=12,
            created_at=demo_accounts["cairo_health"].created_at,
        )
        self.session.add(cairo_health_org)

        self.session.commit()
        logger.info("Created demo organization profiles")

    def create_additional_data(self, demo_accounts: Dict[str, User]) -> Dict[str, int]:
        """Create additional realistic data to reach target numbers"""
        logger.info("Creating additional data to reach target numbers...")

        counts = {"volunteers": 0, "organizations": 0, "opportunities": 0}

        # Create additional volunteers (target: 30+ total)
        first_names = [
            "Ahmed",
            "Fatima",
            "Omar",
            "Layla",
            "Hassan",
            "Zeinab",
            "Khalid",
            "Amira",
            "Mohammad",
            "Dina",
            "Youssef",
            "Rana",
            "Ali",
            "Salma",
            "Karim",
            "Nour",
            "Mahmoud",
            "Maryam",
            "Ibrahim",
            "Yasmin",
        ]

        last_names = [
            "Al-Ahmad",
            "Hassan",
            "Al-Zahra",
            "Mansour",
            "Al-Rashid",
            "Khalil",
            "Al-Nouri",
            "Farouk",
            "Al-Mahmoud",
            "Taha",
            "Al-Sharif",
            "Nazir",
            "Al-Khatib",
            "Salah",
        ]

        # Create 27 additional volunteers (3 demo + 27 = 30)
        for i in range(27):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            country = random.choice(self.countries)
            city = random.choice(
                self.cities.get(country["en"], [{"en": "Capital", "ar": "العاصمة"}])
            )
            skills = random.sample([s["en"] for s in self.skills], random.randint(2, 5))
            interests = random.sample(
                [c["en"] for c in self.causes], random.randint(2, 4)
            )

            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=f"{first_name.lower()}.{last_name.lower().replace('al-', '')}_{i}@example.com",
                hashed_password=hash_password("volunteer123"),
                first_name=first_name,
                last_name=last_name,
                role=UserRole.VOLUNTEER,
                status=UserStatus.ACTIVE,
                is_verified=random.random() > 0.3,
                created_at=datetime.now(datetime.timezone.utc)
                - timedelta(days=random.randint(1, 1095)),
            )
            self.session.add(user)
            self.session.flush()

            # Create volunteer profile
            volunteer = Volunteer(
                id=str(uuid.uuid4()),
                user_id=user.id,
                bio=f"Passionate volunteer committed to making a positive impact in {country['en']} through community engagement and social work.",
                bio_ar=f"متطوع شغوف ملتزم بإحداث تأثير إيجابي في {country['ar']} من خلال المشاركة المجتمعية والعمل الاجتماعي.",
                location=f"{city['en']}, {country['en']}",
                location_ar=f"{city['ar']}، {country['ar']}",
                skills=skills,
                interests=interests,
                languages=random.sample(
                    ["Arabic", "English", "French"], random.randint(1, 3)
                ),
                availability=random.choice(
                    ["full-time", "part-time", "weekends", "flexible"]
                ),
                experience_level=random.choice(["beginner", "intermediate", "expert"]),
                phone=f"+{random.randint(20, 971)}{random.randint(100000000, 999999999)}",
                profession=random.choice(
                    [
                        "Student",
                        "Teacher",
                        "Engineer",
                        "Designer",
                        "Developer",
                        "Manager",
                    ]
                ),
                education_level=random.choice(["high_school", "bachelor", "master"]),
                has_car=random.random() > 0.6,
                can_travel=random.random() > 0.7,
                total_hours=random.randint(0, 300),
                completed_opportunities=random.randint(0, 15),
                rating=round(random.uniform(3.5, 5.0), 1),
                is_featured=random.random() > 0.9,
                created_at=user.created_at,
            )
            self.session.add(volunteer)
            counts["volunteers"] += 1

        # Create additional organizations (target: 15+ total)
        org_names = [
            {"en": "Future Leaders", "ar": "قادة المستقبل"},
            {"en": "Unity Initiative", "ar": "مبادرة الوحدة"},
            {"en": "Green Horizon", "ar": "الأفق الأخضر"},
            {"en": "Helping Hands", "ar": "الأيدي المساعدة"},
            {"en": "Bright Tomorrow", "ar": "غد مشرق"},
            {"en": "Open Hearts", "ar": "القلوب المفتوحة"},
            {"en": "Strong Roots", "ar": "الجذور القوية"},
            {"en": "New Path", "ar": "الطريق الجديد"},
            {"en": "Rising Stars", "ar": "النجوم الصاعدة"},
            {"en": "Peace Builders", "ar": "بناة السلام"},
            {"en": "Dream Makers", "ar": "صناع الأحلام"},
        ]

        # Create 13 additional organizations (2 demo + 13 = 15)
        for i in range(13):
            org_name = random.choice(org_names)
            country = random.choice(self.countries)
            city = random.choice(
                self.cities.get(country["en"], [{"en": "Capital", "ar": "العاصمة"}])
            )
            org_causes = random.sample([c["en"] for c in self.causes], random.randint(2, 4))

            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=f"info@{org_name['en'].lower().replace(' ', '')}{i}.org",
                hashed_password=hash_password("org123"),
                first_name=org_name["en"],
                last_name="Organization",
                role=UserRole.ORGANIZATION,
                status=UserStatus.ACTIVE,
                is_verified=random.random() > 0.2,
                created_at=datetime.now(datetime.timezone.utc)
                - timedelta(days=random.randint(90, 1825)),
            )
            self.session.add(user)
            self.session.flush()

            # Create organization profile
            org = Organisation(
                id=str(uuid.uuid4()),
                user_id=user.id,
                name=f"{org_name['en']} {country['en']}",
                name_ar=f"{org_name['ar']} {country['ar']}",
                description=f"Empowering communities through innovative programs and sustainable development initiatives in {country['en']}.",
                description_ar=f"تمكين المجتمعات من خلال البرامج المبتكرة ومبادرات التنمية المستدامة في {country['ar']}.",
                logo_url=f"/logos/org-{i}.png",
                website=f"https://{org_name['en'].lower().replace(' ', '')}.{country['code'].lower()}",
                phone=f"+{random.randint(20, 971)}{random.randint(100000000, 999999999)}",
                address=f"{random.randint(1, 999)} Main Street, {city['en']}, {country['en']}",
                address_ar=f"{random.randint(1, 999)} الشارع الرئيسي، {city['ar']}، {country['ar']}",
                city=city["en"],
                city_ar=city["ar"],
                country=country["en"],
                country_ar=country["ar"],
                established_year=random.randint(2005, 2022),
                team_size=random.choice(["5-10", "10-25", "25-50"]),
                causes=org_causes,
                is_verified=random.random() > 0.3,
                verification_date=(
                    datetime.now(datetime.timezone.utc) if random.random() > 0.3 else None
                ),
                rating=round(random.uniform(3.5, 5.0), 1),
                total_volunteers=random.randint(10, 200),
                active_opportunities=random.randint(1, 15),
                created_at=user.created_at,
            )
            self.session.add(org)
            counts["organizations"] += 1

        self.session.commit()
        logger.info(f"Created {counts['volunteers']} additional volunteers and {counts['organizations']} additional organizations")
        return counts

    def create_opportunities(self) -> int:
        """Create 30+ realistic opportunities"""
        logger.info("Creating opportunities...")

        # Get all organizations
        organizations = self.session.exec(select(Organisation)).all()

        opportunity_titles = [
            {"en": "English Tutor for Refugee Children", "ar": "مدرس إنجليزية لأطفال اللاجئين"},
            {"en": "Social Media Manager", "ar": "مدير وسائل التواصل الاجتماعي"},
            {"en": "Youth Mentor Program", "ar": "برنامج توجيه الشباب"},
            {"en": "Grant Writing Specialist", "ar": "أخصائي كتابة المنح"},
            {"en": "Community Event Coordinator", "ar": "منسق فعاليات المجتمع"},
            {"en": "Digital Marketing Specialist", "ar": "أخصائي التسويق الرقمي"},
            {"en": "Healthcare Support Volunteer", "ar": "متطوع دعم الرعاية الصحية"},
            {"en": "Environmental Awareness Coordinator", "ar": "منسق التوعية البيئية"},
            {"en": "Translation Services Volunteer", "ar": "متطوع خدمات الترجمة"},
            {"en": "Photography Volunteer", "ar": "متطوع تصوير"},
            {"en": "Workshop Facilitator", "ar": "ميسر ورشة عمل"},
            {"en": "Research Assistant", "ar": "مساعد بحث"},
            {"en": "Computer Skills Trainer", "ar": "مدرب مهارات الحاسوب"},
            {"en": "Fundraising Campaign Manager", "ar": "مدير حملة جمع التبرعات"},
            {"en": "Content Creator", "ar": "منشئ محتوى"},
        ]

        opportunities_created = 0

        # Create 35 opportunities distributed among organizations
        for i in range(35):
            org = random.choice(organizations)
            title = random.choice(opportunity_titles)
            skills = random.sample([s["en"] for s in self.skills], random.randint(2, 5))
            causes = random.sample(org.causes, min(random.randint(1, 2), len(org.causes)))

            start_date = datetime.now(datetime.timezone.utc) + timedelta(
                days=random.randint(1, 60)
            )
            end_date = start_date + timedelta(days=random.randint(30, 365))

            opportunity = Opportunity(
                id=str(uuid.uuid4()),
                org_id=org.id,
                title=title["en"],
                title_ar=title["ar"],
                description=f"Join our team to make a meaningful impact through {title['en'].lower()} work with {org.name}. This role involves working directly with our community members to deliver essential services and support.",
                description_ar=f"انضم إلى فريقنا لإحداث تأثير مفيد من خلال عمل {title['ar'].lower()} مع {org.name_ar}.",
                skills_required=skills,
                categories=[causes[0] if causes else "Community Development"],
                location=f"{org.city}, {org.country}",
                location_ar=f"{org.city_ar}، {org.country_ar}",
                time_commitment=f"{random.randint(2, 20)} hours per week",
                start_date=start_date.date(),
                end_date=end_date.date(),
                max_volunteers=random.randint(1, 5),
                is_remote=random.random() > 0.7,
                state=random.choice([
                    OpportunityState.ACTIVE,
                    OpportunityState.ACTIVE,
                    OpportunityState.ACTIVE,  # More likely to be active
                    OpportunityState.FILLED,
                ]),
                urgency=random.choice(["low", "medium", "high"]),
                created_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 30)),
            )
            self.session.add(opportunity)
            opportunities_created += 1

        self.session.commit()
        logger.info(f"Created {opportunities_created} opportunities")
        return opportunities_created

    def create_applications_and_conversations(self) -> Dict[str, int]:
        """Create realistic applications and some conversations"""
        logger.info("Creating applications and conversations...")

        volunteers = self.session.exec(select(Volunteer)).all()
        opportunities = self.session.exec(
            select(Opportunity).where(Opportunity.state == OpportunityState.ACTIVE)
        ).all()

        applications_created = 0
        conversations_created = 0

        # Create 50+ applications
        for i in range(60):
            volunteer = random.choice(volunteers)
            opportunity = random.choice(opportunities)

            # Avoid duplicate applications
            existing = self.session.exec(
                select(Application).where(
                    Application.volunteer_id == volunteer.user_id,
                    Application.opportunity_id == opportunity.id,
                )
            ).first()

            if existing:
                continue

            application = Application(
                id=str(uuid.uuid4()),
                volunteer_id=volunteer.user_id,
                opportunity_id=opportunity.id,
                status=random.choice([
                    ApplicationStatus.PENDING,
                    ApplicationStatus.PENDING,  # More likely to be pending
                    ApplicationStatus.ACCEPTED,
                    ApplicationStatus.REJECTED,
                ]),
                cover_letter="I am excited to contribute to this meaningful cause and apply my skills to make a difference in the community.",
                applied_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 30)),
            )
            self.session.add(application)
            applications_created += 1

            # Sometimes create a conversation between volunteer and organization
            if random.random() > 0.7:  # 30% chance
                org = self.session.exec(
                    select(Organisation).where(Organisation.id == opportunity.org_id)
                ).first()

                if org:
                    conversation = Conversation(
                        id=str(uuid.uuid4()),
                        participants=[volunteer.user_id, org.user_id],
                        subject=f"Regarding: {opportunity.title}",
                        created_at=application.applied_at + timedelta(hours=random.randint(1, 48)),
                    )
                    self.session.add(conversation)
                    self.session.flush()

                    # Add a message
                    message = Message(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation.id,
                        sender_id=volunteer.user_id,
                        content="Hello, I'm very interested in this opportunity and would love to learn more about it.",
                        sent_at=conversation.created_at + timedelta(minutes=5),
                    )
                    self.session.add(message)
                    conversations_created += 1

        self.session.commit()
        logger.info(f"Created {applications_created} applications and {conversations_created} conversations")
        return {"applications": applications_created, "conversations": conversations_created}

    def create_reviews(self) -> int:
        """Create some reviews between volunteers and organizations"""
        logger.info("Creating reviews...")

        # Get completed applications
        applications = self.session.exec(
            select(Application).where(Application.status == ApplicationStatus.ACCEPTED)
        ).all()

        reviews_created = 0

        # Create reviews for some completed applications
        for application in applications[:20]:  # First 20 accepted applications
            if random.random() > 0.5:  # 50% chance
                volunteer = self.session.exec(
                    select(Volunteer).where(Volunteer.user_id == application.volunteer_id)
                ).first()
                
                opportunity = self.session.exec(
                    select(Opportunity).where(Opportunity.id == application.opportunity_id)
                ).first()

                org = self.session.exec(
                    select(Organisation).where(Organisation.id == opportunity.org_id)
                ).first()

                if volunteer and org:
                    # Organization reviews volunteer
                    org_review = Review(
                        id=str(uuid.uuid4()),
                        reviewer_id=org.user_id,
                        reviewee_id=volunteer.user_id,
                        opportunity_id=opportunity.id,
                        rating=round(random.uniform(3.5, 5.0), 1),
                        comment=f"Excellent work from {volunteer.user.first_name}. Very professional and dedicated to the cause.",
                        review_type="organization_to_volunteer",
                        created_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(1, 30)),
                    )
                    self.session.add(org_review)
                    reviews_created += 1

                    # Sometimes volunteer reviews back
                    if random.random() > 0.6:  # 40% chance
                        vol_review = Review(
                            id=str(uuid.uuid4()),
                            reviewer_id=volunteer.user_id,
                            reviewee_id=org.user_id,
                            opportunity_id=opportunity.id,
                            rating=round(random.uniform(3.8, 5.0), 1),
                            comment="Great organization with clear communication and meaningful impact. Highly recommend!",
                            review_type="volunteer_to_organization",
                            created_at=org_review.created_at + timedelta(days=random.randint(1, 7)),
                        )
                        self.session.add(vol_review)
                        reviews_created += 1

        self.session.commit()
        logger.info(f"Created {reviews_created} reviews")
        return reviews_created

    def create_analytics_events(self) -> int:
        """Create some analytics events for the dashboard"""
        logger.info("Creating analytics events...")

        users = self.session.exec(select(User)).all()
        events_created = 0

        event_types = [
            "user_login",
            "user_register", 
            "opportunity_view",
            "application_submit",
            "profile_update",
            "search_performed",
            "message_sent",
            "review_submitted",
        ]

        # Create 100 analytics events over the past 30 days
        for i in range(100):
            user = random.choice(users)
            event_type = random.choice(event_types)
            
            event = AnalyticsEvent(
                id=str(uuid.uuid4()),
                user_id=user.id,
                event_type=event_type,
                event_data={
                    "user_role": user.role.value,
                    "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
                    "session_id": f"session_{random.randint(1000, 9999)}",
                },
                created_at=datetime.now(datetime.timezone.utc) - timedelta(days=random.randint(0, 30)),
            )
            self.session.add(event)
            events_created += 1

        self.session.commit()
        logger.info(f"Created {events_created} analytics events")
        return events_created

    def seed_all_data(self, clear_existing: bool = True) -> Dict[str, Any]:
        """Main method to seed all data"""
        logger.info("Starting unified database seeding...")

        try:
            # Clear existing data if requested
            if clear_existing:
                self.clear_existing_data()
            else:
                existing_admin = self.session.exec(
                    select(User).where(User.email == "admin@seraaj.org")
                ).first()
                if existing_admin:
                    logger.info("Demo accounts already exist; skipping seeding")
                    return {
                        "status": "skipped",
                        "total_volunteers": len(self.session.exec(select(Volunteer)).all()),
                        "total_organizations": len(self.session.exec(select(Organisation)).all()),
                    }

            # Create demo accounts (as documented)
            demo_accounts = self.create_demo_accounts()

            # Create demo profiles
            self.create_demo_volunteers(demo_accounts)
            self.create_demo_organizations(demo_accounts)

            # Create additional data to reach targets
            additional_counts = self.create_additional_data(demo_accounts)

            # Create opportunities
            opportunities_count = self.create_opportunities()

            # Create applications and conversations
            app_conv_counts = self.create_applications_and_conversations()

            # Create reviews
            reviews_count = self.create_reviews()

            # Create analytics events
            analytics_count = self.create_analytics_events()

            results = {
                "demo_accounts": len(demo_accounts),
                "total_volunteers": 3 + additional_counts["volunteers"],  # 3 demo + additional
                "total_organizations": 2 + additional_counts["organizations"],  # 2 demo + additional
                "opportunities": opportunities_count,
                "applications": app_conv_counts["applications"],
                "conversations": app_conv_counts["conversations"],
                "reviews": reviews_count,
                "analytics_events": analytics_count,
                "status": "success",
            }

            logger.info("Database seeding completed successfully!")
            logger.info(f"Results: {results}")

            return results

        except Exception as e:
            logger.error(f"Error during database seeding: {e}")
            self.session.rollback()
            raise
        finally:
            self.session.close()


def seed_database(clear_existing: bool = True) -> Dict[str, Any]:
    """Convenience function to seed the database"""
    seeder = UnifiedSeedingService()
    return seeder.seed_all_data(clear_existing=clear_existing)


def should_seed_on_startup() -> bool:
    """Check if seeding should run on startup based on environment variable"""
    return os.getenv("SEED_DB", "false").lower() in ("true", "1", "yes")


if __name__ == "__main__":
    # Ensure database tables exist
    create_db_and_tables()
    
    # Run seeding
    results = seed_database(clear_existing=True)
    print(f"\nSeeding completed successfully!")
    print(f"Created: {results['total_volunteers']} volunteers, {results['total_organizations']} organizations")
    print(f"Created: {results['opportunities']} opportunities, {results['applications']} applications")
    print(f"Created: {results['conversations']} conversations, {results['reviews']} reviews")
    print(f"Created: {results['analytics_events']} analytics events")
    
    print("\nDemo Credentials:")
    print("Admin: admin@seraaj.org | Demo123!")
    print("Volunteers:")
    print("  - layla@example.com | Demo123! (Tech Professional)")
    print("  - omar@example.com | Demo123! (Healthcare Professional)")
    print("  - fatima@example.com | Demo123! (Recent Graduate)")
    print("Organizations:")
    print("  - contact@hopeeducation.org | Demo123! (Education NGO)")
    print("  - info@cairohealthnetwork.org | Demo123! (Healthcare NGO)")