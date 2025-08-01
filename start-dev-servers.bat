@echo off
echo Starting Seraaj v2 Development Servers
echo ======================================

echo.
echo Starting API Server (Port 8000)...
echo.
cd /D "%~dp0apps\api"
start "Seraaj API" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo Waiting 5 seconds for API server to start...
timeout /t 5 /nobreak

echo.
echo Starting Frontend Server (Port 3030)...
echo.
cd /D "%~dp0apps\web"
start "Seraaj Frontend" cmd /k "npm run dev"

echo.
echo ======================================
echo Both servers are starting!
echo ======================================
echo.
echo API Server: http://localhost:8000
echo Frontend: http://localhost:3030
echo API Docs: http://localhost:8000/docs
echo.
echo Demo Login Credentials (Password: Demo123!):
echo.
echo Volunteers:
echo   - layla@example.com (Layla Al-Mansouri)
echo   - omar@example.com (Omar Hassan)  
echo   - fatima@example.com (Fatima Al-Zahra)
echo.
echo Organizations:
echo   - contact@hopeeducation.org (Hope Education Initiative)
echo   - info@cairohealthnetwork.org (Cairo Community Health Network)
echo.
echo Admin:
echo   - admin@seraaj.org (System Administrator)
echo.
echo Press any key to close this window...
pause