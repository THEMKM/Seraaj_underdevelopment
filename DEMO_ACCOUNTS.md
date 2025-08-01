# Seraaj Demo Accounts & Test Data

This document provides login credentials and backstories for all demo accounts in the Seraaj volunteer marketplace platform.

## 🎯 **Quick Start**

All demo accounts use the password: **`Demo123!`**

## 📊 **Current Test Data**

### **Volunteer Opportunities Available (5)**

1. **English Tutor for Refugee Children** (On-site, 4 hours/week)
2. **Social Media Manager** (Remote, 6 hours/week)  
3. **Youth Mentor Program** (On-site, 3 hours/week)
4. **Grant Writing Specialist** (Remote, 8 hours/week)
5. **Community Event Coordinator** (On-site, 10 hours/week)

## 👥 **Demo Account Types**

### **Volunteer Accounts**

#### **Layla Al-Mansouri** - Tech Professional
- **Email**: `layla@example.com`
- **Password**: `Demo123!`
- **Location**: Dubai, UAE
- **Profession**: Software Engineer at Emirates Group
- **Backstory**: Born in Lebanon, raised in Dubai. Passionate about bridging the digital divide in underserved communities. Fluent in Arabic, English, and French. Started volunteering after witnessing the impact of technology training on refugee children.
- **Skills**: Technology Training, Web Development, Arabic Language, English Language, Youth Mentoring
- **Interests**: Digital Inclusion, Education, Refugee Support
- **Availability**: Weekends
- **Experience**: Intermediate level

#### **Omar Hassan** - Healthcare Professional  
- **Email**: `omar@example.com`
- **Password**: `Demo123!`
- **Location**: Cairo, Egypt
- **Profession**: Medical Doctor at Cairo University Hospital
- **Backstory**: Emergency medicine physician who grew up in a working-class neighborhood in Cairo. Deeply committed to healthcare equity. Volunteers in rural clinics during his time off and trains community health workers.
- **Skills**: Healthcare, Emergency Response, Community Outreach, Teaching, Arabic Language
- **Interests**: Healthcare, Emergency Relief, Community Development
- **Availability**: Flexible schedule
- **Experience**: Expert level

#### **Fatima Al-Zahra** - Recent Graduate
- **Email**: `fatima@example.com`
- **Password**: `Demo123!`
- **Location**: Amman, Jordan
- **Profession**: Recent Graduate in International Relations
- **Backstory**: Recent university graduate passionate about women's rights and education. Daughter of Palestinian refugees, she understands the power of education to transform lives. Currently seeking full-time work while dedicating time to volunteer activities.
- **Skills**: Teaching, English Language, Social Work, Grant Writing, Youth Mentoring
- **Interests**: Women's Empowerment, Education, Refugee Support, Youth Development
- **Availability**: Full-time availability
- **Experience**: Beginner level

### **Organization Accounts**

#### **Hope Education Initiative** - Education NGO
- **Email**: `contact@hopeeducation.org`
- **Password**: `Demo123!`
- **Location**: Dubai, UAE
- **Type**: NGO (Medium-sized)
- **Founded**: 2018
- **Mission**: "Bridging educational gaps through innovative learning programs and technology access"
- **Backstory**: Founded by a group of educators and tech professionals to address educational inequality in the UAE and broader MENA region. Focuses on STEM education for underprivileged youth and digital literacy for adults.
- **Focus Areas**: Education, Digital Inclusion, Youth Development, Technology Training
- **Target Population**: Underprivileged youth aged 8-18, adult learners
- **Achievements**: 
  - Reached 2,500+ students
  - Established 15 learning centers
  - 100% college acceptance rate for graduates
- **Current Needs**: Volunteer teachers, Technology trainers, Curriculum developers, Fundraising support

#### **Cairo Community Health Network** - Healthcare NGO
- **Email**: `info@cairohealthnetwork.org`
- **Password**: `Demo123!`
- **Location**: Cairo, Egypt
- **Type**: Healthcare NGO (Large-sized)
- **Founded**: 2010
- **Mission**: "Ensuring quality healthcare access for all Cairo residents regardless of economic status"
- **Backstory**: Healthcare network serving Cairo's underserved neighborhoods. Started by a group of doctors and nurses committed to healthcare equity. Operates mobile clinics and community health programs.
- **Focus Areas**: Healthcare, Community Development, Emergency Relief, Health Education
- **Target Population**: Low-income families, elderly, children, chronic disease patients
- **Achievements**:
  - Served 50,000+ patients
  - Operates 8 mobile clinics
  - Reduced infant mortality by 40% in partner areas
- **Current Needs**: Medical volunteers, Health educators, Data analysts, Community health workers

### **Admin Accounts**

#### **Platform Administrator**
- **Email**: `admin@seraaj.org`
- **Password**: `Demo123!`
- **Role**: System Administrator
- **Permissions**: Full platform access, user management, content moderation, analytics access

## 🔗 **API Endpoints Available**

### **Authentication**
- `POST /v1/auth/login` - User login
- `POST /v1/auth/register` - User registration
- `GET /v1/auth/me` - Get current user profile

### **Opportunities**
- `GET /v1/opportunities/` - List all opportunities
- `GET /v1/opportunities/search` - Search opportunities
- `GET /v1/opportunities/search?q=keyword` - Search opportunities with query parameters
- `GET /v1/opportunities/{id}` - Get specific opportunity

### **Applications**
- `GET /v1/applications/` - List applications
- `POST /v1/applications/` - Submit application
- `GET /v1/applications/{id}` - Get specific application

### **Profiles**
- `GET /v1/profiles/volunteer` - Volunteer profiles
- `GET /v1/profiles/organization` - Organization profiles

### **Matching (ML-Powered)**
- `GET /v1/match/opportunities` - Get ML-matched opportunities for volunteer

### **Reviews & Ratings**
- `GET /v1/reviews/` - List reviews
- `POST /v1/reviews/` - Submit review

### **File Management**
- `POST /v1/files/upload` - Upload files
- `GET /v1/files/{id}` - Download files

### **Admin Features**
- `GET /v1/admin/users` - User management
- `GET /v1/admin/analytics` - Platform analytics

## 🧪 **Testing Scenarios**

### **Volunteer Journey**
1. **Login** as Layla (`layla@example.com`)
2. **Browse opportunities** using search
3. **Apply** to "English Tutor for Refugee Children"
4. **View application status**
5. **Rate and review** after completion

### **Organization Journey**
1. **Login** as Hope Education (`contact@hopeeducation.org`)
2. **View applications** for posted opportunities
3. **Accept/reject** volunteer applications
4. **Rate volunteers** after project completion

### **ML Matching Test**
1. **Login** as any volunteer
2. **GET** `/v1/match/opportunities` to see ML-powered matches
3. **Verify** skills-based matching algorithm

### **Real-time Features Test**
1. **Login** as volunteer and organization
2. **Test WebSocket messaging** between accounts
3. **Verify** real-time notifications

## 🌍 **Geographic Coverage**

Demo data covers major MENA cities:
- **Dubai, UAE** - Tech and education focus
- **Cairo, Egypt** - Healthcare and community development
- **Amman, Jordan** - Refugee support and women's empowerment

## 📱 **Frontend Integration**

The Next.js frontend at `apps/web/` is configured to work with these demo accounts:

### **API Configuration**
- **Base URL**: `http://localhost:8000`
- **Authentication**: JWT-based with refresh tokens
- **WebSocket**: `ws://localhost:8000/ws`

### **Demo Flow**
1. **Start backend**: `cd apps/api && python -m uvicorn main:app --reload`
2. **Start frontend**: `cd apps/web && npm run dev`
3. **Visit**: `http://localhost:3000`
4. **Login** with any demo account above

## 🔄 **Data Reset**

To reset demo data:
```bash
cd apps/api
rm seraaj_dev.db  # Delete existing database
python -m uvicorn main:app --reload  # Restart server (auto-creates tables)
python create_test_opportunities.py  # Add test opportunities
```

## 📊 **System Status**

### **✅ Working Features**
- User authentication and registration
- Opportunity browsing and search
- Application submission and management
- Profile management (volunteers & organizations)
- ML-powered opportunity matching
- File upload and management
- Reviews and ratings system
- Admin dashboard and analytics
- Real-time messaging via WebSocket

### **🔧 Production-Ready Components**
- FastAPI backend with comprehensive error handling
- SQLite database with 47+ tables
- JWT authentication with token refresh
- Rate limiting and security middleware
- Comprehensive logging and monitoring
- API documentation at `/docs`

---

**Last Updated**: July 29, 2025  
**Platform Version**: Seraaj v2.0.0  
**Status**: Production-ready demo environment