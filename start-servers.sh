#!/bin/bash
# Cross-Platform Seraaj v2 Development Server Launcher (Unix/Linux/macOS)
# =========================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
FRONTEND_PORT=3030
API_HOST="127.0.0.1"

# Process tracking
API_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ ! -z "$API_PID" ]; then
        if kill -0 "$API_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Stopping API server (PID: $API_PID)${NC}"
            kill "$API_PID"
        fi
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Stopping Frontend server (PID: $FRONTEND_PID)${NC}"
            kill "$FRONTEND_PID"
        fi
    fi
    
    echo -e "${PURPLE}👋 Goodbye!${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Help function
show_help() {
    cat << EOF
Seraaj v2 Development Server Launcher (Unix/Linux/macOS)
========================================================

Usage: $0 [OPTIONS]

Options:
    --api-only      Start only the API server
    --frontend-only Start only the frontend server
    --debug         Enable debug mode with verbose output
    --help          Show this help message

Examples:
    $0                    # Start both servers
    $0 --api-only         # Start only API server
    $0 --frontend-only    # Start only frontend server
    $0 --debug            # Start with debug logging

EOF
}

# Parse command line arguments
API_ONLY=false
FRONTEND_ONLY=false
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-only)
            API_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Detect operating system
OS=$(uname -s)
echo -e "${BLUE}🖥️  Platform: $OS${NC}"

# Check dependencies
echo -e "${CYAN}🔍 Checking dependencies...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python.${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js.${NC}"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm: v$NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm not found. Please install npm.${NC}"
    exit 1
fi

# Find project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📁 Project Root: $PROJECT_ROOT${NC}"

# Validate project structure
if [ ! -d "$PROJECT_ROOT/apps/api" ]; then
    echo -e "${RED}❌ API directory not found: $PROJECT_ROOT/apps/api${NC}"
    exit 1
fi

if [ ! -d "$PROJECT_ROOT/apps/web" ]; then
    echo -e "${RED}❌ Frontend directory not found: $PROJECT_ROOT/apps/web${NC}"
    exit 1
fi

echo ""

# Start API server
if [ "$FRONTEND_ONLY" != true ]; then
    echo -e "${PURPLE}🚀 Starting API Server (Port $API_PORT)...${NC}"
    
    cd "$PROJECT_ROOT/apps/api"
    
    if [ "$DEBUG" = true ]; then
        $PYTHON_CMD -m uvicorn main:app --host $API_HOST --port $API_PORT --reload --log-level debug &
    else
        $PYTHON_CMD -m uvicorn main:app --host $API_HOST --port $API_PORT --reload &
    fi
    
    API_PID=$!
    echo -e "${GREEN}✅ API Server started (PID: $API_PID)${NC}"
    
    # Wait for API server to start
    sleep 3
fi

# Start Frontend server
if [ "$API_ONLY" != true ]; then
    echo -e "${PURPLE}🎨 Starting Frontend Server (Port $FRONTEND_PORT)...${NC}"
    
    cd "$PROJECT_ROOT/apps/web"
    
    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}✅ Frontend Server started (PID: $FRONTEND_PID)${NC}"
    
    # Wait for frontend server to start
    sleep 2
fi

# Display server information
echo ""
echo -e "${CYAN}=================================================="
echo -e "🌟 Seraaj v2 Development Servers Running!"
echo -e "==================================================${NC}"
echo ""
echo -e "${BLUE}📍 Server URLs:${NC}"
echo -e "   API Server:    http://localhost:$API_PORT"
echo -e "   API Docs:      http://localhost:$API_PORT/docs"
echo -e "   Frontend:      http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${YELLOW}🔐 Demo Login Credentials (Password: Demo123!):${NC}"
echo ""
echo -e "${GREEN}   👥 Volunteers:${NC}"
echo -e "     • layla@example.com (Layla Al-Mansouri)"
echo -e "     • omar@example.com (Omar Hassan)"
echo -e "     • fatima@example.com (Fatima Al-Zahra)"
echo ""
echo -e "${GREEN}   🏢 Organizations:${NC}"
echo -e "     • contact@hopeeducation.org (Hope Education Initiative)"
echo -e "     • info@cairohealthnetwork.org (Cairo Community Health Network)"
echo ""
echo -e "${PURPLE}💡 Press Ctrl+C to stop all servers${NC}"
echo -e "${CYAN}==================================================${NC}"

# Wait for servers and user interrupt
while true; do
    sleep 1
    
    # Check if API server is still running
    if [ ! -z "$API_PID" ] && ! kill -0 "$API_PID" 2>/dev/null; then
        echo -e "\n${YELLOW}⚠️  API server has stopped unexpectedly${NC}"
        API_PID=""
    fi
    
    # Check if Frontend server is still running
    if [ ! -z "$FRONTEND_PID" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "\n${YELLOW}⚠️  Frontend server has stopped unexpectedly${NC}"
        FRONTEND_PID=""
    fi
    
    # If both servers have stopped, exit
    if [ -z "$API_PID" ] && [ -z "$FRONTEND_PID" ]; then
        echo -e "\n${RED}❌ All servers have stopped.${NC}"
        exit 1
    fi
done