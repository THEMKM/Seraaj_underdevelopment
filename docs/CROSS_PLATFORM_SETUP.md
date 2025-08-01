# Cross-Platform Development Setup Guide

This guide helps you set up and run the Seraaj v2 development environment on any platform (Windows, macOS, Linux).

## 🚀 Quick Start Options

### Option 1: Python Script (Recommended)
Works on all platforms with Python installed:

```bash
# Start both servers
python start-servers.py

# Start only API server
python start-servers.py --api-only

# Start only frontend server  
python start-servers.py --frontend-only

# Start with debug logging
python start-servers.py --debug
```

### Option 2: Unix Shell Script (Linux/macOS)
For Unix-like systems:

```bash
# Make executable (first time only)
chmod +x start-servers.sh

# Start both servers
./start-servers.sh

# Start only API server
./start-servers.sh --api-only

# Start only frontend server
./start-servers.sh --frontend-only
```

### Option 3: npm Scripts
If you have npm/pnpm installed:

```bash
# Start both servers (cross-platform)
npm run start:servers

# Start only API server
npm run start:servers:api

# Start only frontend server  
npm run start:servers:web

# Start with debug mode
npm run start:servers:debug
```

### Option 4: Windows Batch Files (Windows Only)
For Windows users who prefer batch files:

```cmd
START_SERVERS.bat
```

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** - For API server
- **Node.js 18+** - For frontend server
- **npm/pnpm** - For package management

### Installation by Platform

#### Windows
```powershell
# Install Python from python.org or via Microsoft Store
winget install Python.Python.3

# Install Node.js
winget install OpenJS.NodeJS

# Verify installations
python --version
node --version
npm --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11 node

# Or using MacPorts
sudo port install python311 nodejs18

# Verify installations
python3 --version
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python and Node.js
sudo apt install python3 python3-pip nodejs npm

# Verify installations
python3 --version
node --version
npm --version
```

#### Linux (RHEL/CentOS/Fedora)
```bash
# For RHEL/CentOS
sudo yum install python3 nodejs npm

# For Fedora
sudo dnf install python3 nodejs npm

# Verify installations
python3 --version
node --version
npm --version
```

## 🖥️ Platform-Specific Notes

### Windows
- Use `python` command (usually available after installation)
- Servers run in separate console windows for easy monitoring
- Path separators handled automatically
- Windows Defender may prompt for network access permissions

### macOS
- Use `python3` command to ensure Python 3.x
- Servers run in background with output to terminal
- May need to allow network access in System Preferences → Security & Privacy
- Works with both Intel and Apple Silicon Macs

### Linux
- Use `python3` command on most distributions
- Servers run in background with output to terminal
- Different distributions may have slightly different package names
- Ensure firewall allows local development ports (8000, 3030)

## 🔍 Troubleshooting

### Common Issues

#### "python: command not found"
- **Windows**: Reinstall Python and check "Add Python to PATH" option
- **macOS/Linux**: Use `python3` instead of `python`

#### "node: command not found"
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Restart terminal after installation
- Check PATH environment variable includes Node.js

#### "Permission denied" on Linux/macOS
```bash
# Make scripts executable
chmod +x start-servers.sh
chmod +x start-servers.py
```

#### Port Already in Use
- Check if servers are already running: `lsof -i :8000` (Unix) or `netstat -an | findstr :8000` (Windows)
- Kill existing processes or use different ports
- The Python script will show clear error messages for port conflicts

#### API Server Won't Start
- Ensure you're in the project root directory
- Check that `apps/api` directory exists
- Verify Python dependencies are installed: `cd apps/api && pip install -r requirements.txt`

#### Frontend Server Won't Start
- Ensure you're in the project root directory
- Check that `apps/web` directory exists
- Install frontend dependencies: `cd apps/web && npm install`

### Debug Mode
Enable debug mode for detailed logging:

```bash
python start-servers.py --debug
./start-servers.sh --debug
npm run start:servers:debug
```

## 🌐 Server URLs

Once started, access your servers at:

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend Application**: http://localhost:3030

## 🔐 Demo Credentials

For testing the application:

**Password for all accounts**: `Demo123!`

**Volunteers**:
- layla@example.com (Layla Al-Mansouri)
- omar@example.com (Omar Hassan)
- fatima@example.com (Fatima Al-Zahra)

**Organizations**:
- contact@hopeeducation.org (Hope Education Initiative)
- info@cairohealthnetwork.org (Cairo Community Health Network)

## 🛠️ Development Workflow

### Recommended Setup
1. Use the Python script for consistent cross-platform experience
2. Open separate terminals for monitoring logs if needed
3. Use your IDE's integrated terminal for running commands
4. Keep servers running during development for hot-reload functionality

### Stopping Servers
- **Python/Shell scripts**: Press `Ctrl+C` to gracefully stop all servers
- **npm scripts**: Press `Ctrl+C` in the terminal running the script
- **Windows batch files**: Close the console windows or press `Ctrl+C`

### Next Steps
- Set up your IDE for the project structure
- Review the [API documentation](../API_REFERENCE.md) 
- Check the [Frontend architecture guide](../FRONTEND_ARCHITECTURE.md)
- Read about [Data flow](../DATA_FLOW.md) between components

## 📚 Additional Resources

- [Project Architecture Overview](../ARCHITECTURE.md)
- [API Reference](../API_REFERENCE.md)
- [Development Guidelines](../DEVELOPMENT.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)

---

**Need Help?** 
- Check the troubleshooting section above
- Review server logs for specific error messages
- Ensure all prerequisites are properly installed
- Try the debug mode for detailed logging