#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Seraaj v2 Development Server Launcher
====================================================

This script provides a cross-platform way to start both the API and frontend servers
for development. It works on Windows, macOS, and Linux.

Usage:
    python start-servers.py [--api-only] [--frontend-only] [--debug]

Options:
    --api-only      Start only the API server
    --frontend-only Start only the frontend server  
    --debug         Enable debug mode with verbose output
    --help          Show this help message
"""

import sys
import os
import subprocess
import time
import signal
import argparse
from pathlib import Path
import platform

# Fix Windows encoding issue for proper emoji display
if sys.platform.startswith('win'):
    # Set UTF-8 encoding for Windows console
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # Enable ANSI escape sequences on Windows 10+
    import os
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8
    os.system('cls')  # Clear screen to apply encoding


def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    is_windows = system == 'windows'
    is_mac = system == 'darwin'
    is_linux = system == 'linux'
    
    return {
        'system': system,
        'is_windows': is_windows,
        'is_mac': is_mac,
        'is_linux': is_linux,
        'python_cmd': 'python' if is_windows else 'python3',
        'shell': is_windows
    }


def find_project_root():
    """Find the project root directory"""
    current = Path(__file__).parent.absolute()
    
    # Look for indicators that this is the project root
    indicators = ['apps', 'CLAUDE.md', 'package.json']
    
    for indicator in indicators:
        if (current / indicator).exists():
            return current
    
    # If not found, assume current directory is project root
    return current


def check_dependencies(platform_info):
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    try:
        result = subprocess.run([platform_info['python_cmd'], '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except FileNotFoundError:
        print(f"❌ Python not found. Please install Python or update PATH.")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js or update PATH.")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ npm not found. Please install npm or update PATH.")
        return False
    
    return True


def start_api_server(project_root, platform_info, debug=False):
    """Start the API server"""
    api_dir = project_root / 'apps' / 'api'
    
    if not api_dir.exists():
        print(f"❌ API directory not found: {api_dir}")
        return None
    
    print("🚀 Starting API Server (Port 8000)...")
    
    cmd = [
        platform_info['python_cmd'], '-m', 'uvicorn', 'main:app',
        '--host', '127.0.0.1',
        '--port', '8000',
        '--reload'
    ]
    
    if debug:
        cmd.extend(['--log-level', 'debug'])
    
    try:
        if platform_info['is_windows']:
            # On Windows, create new console window
            process = subprocess.Popen(
                cmd,
                cwd=api_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix-like systems, run in background
            process = subprocess.Popen(
                cmd,
                cwd=api_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print(f"✅ API Server started (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None


def start_frontend_server(project_root, platform_info, debug=False):
    """Start the frontend server"""
    frontend_dir = project_root / 'apps' / 'web'
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return None
    
    print("🎨 Starting Frontend Server (Port 3030)...")
    
    cmd = ['npm', 'run', 'dev']
    
    try:
        if platform_info['is_windows']:
            # On Windows, create new console window
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=True
            )
        else:
            # On Unix-like systems, run in background
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print(f"✅ Frontend Server started (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None


def cleanup_processes(processes):
    """Clean up running processes"""
    print("\\n🛑 Shutting down servers...")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Process {process.pid} terminated gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  Process {process.pid} killed forcefully")
            except Exception as e:
                print(f"❌ Error terminating process {process.pid}: {e}")


def display_info():
    """Display server information"""
    print("\\n" + "="*50)
    print("🌟 Seraaj v2 Development Servers Running!")
    print("="*50)
    print()
    print("📍 Server URLs:")
    print("   API Server:    http://localhost:8000")
    print("   API Docs:      http://localhost:8000/docs")
    print("   Frontend:      http://localhost:3030")
    print()
    print("🔐 Demo Login Credentials (Password: Demo123!):")
    print()
    print("   👥 Volunteers:")
    print("     • layla@example.com (Layla Al-Mansouri)")
    print("     • omar@example.com (Omar Hassan)")
    print("     • fatima@example.com (Fatima Al-Zahra)")
    print()
    print("   🏢 Organizations:")
    print("     • contact@hopeeducation.org (Hope Education Initiative)")
    print("     • info@cairohealthnetwork.org (Cairo Community Health Network)")
    print()
    print("💡 Press Ctrl+C to stop all servers")
    print("="*50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Start Seraaj v2 development servers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--api-only', action='store_true', 
                       help='Start only the API server')
    parser.add_argument('--frontend-only', action='store_true',
                       help='Start only the frontend server')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose output')
    
    args = parser.parse_args()
    
    print("Seraaj v2 Cross-Platform Server Launcher")
    print("=" * 45)
    
    # Get platform information
    platform_info = get_platform_info()
    print(f"Platform: {platform_info['system'].title()}")
    
    # Find project root
    project_root = find_project_root()
    print(f"Project Root: {project_root}")
    
    # Check dependencies
    if not check_dependencies(platform_info):
        print("\\nDependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    print()
    
    # Start servers
    processes = []
    
    try:
        if not args.frontend_only:
            api_process = start_api_server(project_root, platform_info, args.debug)
            if api_process:
                processes.append(api_process)
                time.sleep(3)  # Wait for API server to start
        
        if not args.api_only:
            frontend_process = start_frontend_server(project_root, platform_info, args.debug)
            if frontend_process:
                processes.append(frontend_process)
                time.sleep(2)  # Wait for frontend server to start
        
        if not processes:
            print("❌ No servers were started successfully.")
            sys.exit(1)
        
        # Display information
        display_info()
        
        # Wait for user interrupt
        try:
            while True:
                time.sleep(1)
                # Check if any process has died
                for process in processes[:]:  # Copy list to avoid modification during iteration
                    if process.poll() is not None:
                        print(f"\\n⚠️  Process {process.pid} has stopped unexpectedly")
                        processes.remove(process)
                
                if not processes:
                    print("\\n❌ All servers have stopped.")
                    break
                    
        except KeyboardInterrupt:
            print("\\n\\n🛑 Received shutdown signal...")
        
    finally:
        cleanup_processes(processes)
        print("\\n👋 Goodbye!")


if __name__ == '__main__':
    main()