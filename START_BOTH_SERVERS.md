# Start Seraaj Platform

## Quick Start Commands

**Open 2 terminal windows and run these commands:**

### Terminal 1 - Backend API (Port 8000)
```bash
cd "C:\Users\Mohamad\Documents\Claude\Seraaj\apps\api"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2 - Frontend Web App (Port 3030)  
```bash
cd "C:\Users\Mohamad\Documents\Claude\Seraaj\apps\web"
npm run dev
```

## URLs to Access

**Frontend (Main App)**: `http://localhost:3030`
**Backend API Docs**: `http://localhost:8000/docs`
**Health Check**: `http://localhost:8000/health`

## Demo Login Credentials

**Volunteers:**
- `layla@example.com` (Password: `Demo123!`)
- `omar@example.com` (Password: `Demo123!`) 
- `fatima@example.com` (Password: `Demo123!`)

**Organizations:**
- `contact@hopeeducation.org` (Password: `Demo123!`)
- `info@cairohealthnetwork.org` (Password: `Demo123!`)

## Features Available

✅ User authentication and registration  
✅ Browse and search volunteer opportunities  
✅ Apply to opportunities  
✅ ML-powered opportunity matching  
✅ Real-time messaging via WebSocket  
✅ File upload and management  
✅ Reviews and ratings system  
✅ Admin dashboard and analytics  
✅ Production-ready API with comprehensive error handling  

The platform is fully functional with realistic demo data!