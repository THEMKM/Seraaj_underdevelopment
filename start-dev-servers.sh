#!/bin/bash

echo "Starting Seraaj v2 Development Servers"
echo "======================================"
echo

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting API Server (Port 8000)..."
echo
cd "$SCRIPT_DIR/apps/api"
gnome-terminal --title="Seraaj API" -- bash -c "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload; exec bash" &

echo
echo "Waiting 5 seconds for API server to start..."
sleep 5

echo
echo "Starting Frontend Server (Port 3030)..."
echo
cd "$SCRIPT_DIR/apps/web"
gnome-terminal --title="Seraaj Frontend" -- bash -c "npm run dev; exec bash" &

echo
echo "======================================"
echo "Both servers are starting!"
echo "======================================"
echo
echo "API Server: http://localhost:8000"
echo "Frontend: http://localhost:3030"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Demo Login Credentials (Password: Demo123!):"
echo
echo "Volunteers:"
echo "  - layla@example.com (Layla Al-Mansouri)"
echo "  - omar@example.com (Omar Hassan)"  
echo "  - fatima@example.com (Fatima Al-Zahra)"
echo
echo "Organizations:"
echo "  - contact@hopeeducation.org (Hope Education Initiative)"
echo "  - info@cairohealthnetwork.org (Cairo Community Health Network)"
echo
echo "Admin:"
echo "  - admin@seraaj.org (System Administrator)"
echo
echo "Press Ctrl+C to stop this script (servers will continue running in separate terminals)"
echo "To stop servers, close their terminal windows or use Ctrl+C in each terminal"

# Keep script running
while true; do
    sleep 1
done