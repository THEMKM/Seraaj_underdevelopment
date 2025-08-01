@echo off
cls
echo.
echo  🌅 ================================= 🌅
echo     SERAAJ v2 MVP - 8-BIT OPTIMISM
echo  🌅 ================================= 🌅
echo.
echo 🚀 Starting on CLEAN PORTS to avoid conflicts...
echo    Frontend: http://localhost:3030
echo    API:      http://localhost:8080
echo.

echo 📦 Installing dependencies...
call pnpm install >nul 2>&1

echo 🔧 Setting up environment files...
copy apps\api\.env.example apps\api\.env >nul 2>&1
copy apps\web\.env.local.example apps\web\.env.local >nul 2>&1

echo 📝 Updated .env.local with new ports...
echo NEXT_PUBLIC_API_URL=http://localhost:8080 > apps\web\.env.local
echo PORT=3030 >> apps\web\.env.local

echo.
echo ⚡ READY TO START! ⚡
echo.
echo 🟢 STEP 1: Start API Server (in new terminal)
echo    cd apps\api
echo    pip install -r requirements.txt
echo    uvicorn main:app --reload --host 0.0.0.0 --port 8080
echo.
echo 🟢 STEP 2: Start Frontend (in another terminal)  
echo    cd apps\web
echo    pnpm dev
echo.
echo 📍 Then access: http://localhost:3030
echo    (Should show SERAAJ with 8-Bit Optimism design!)
echo.
echo Press any key to continue...
pause >nul