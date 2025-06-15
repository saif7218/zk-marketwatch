import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ['python', 'pip', 'node', 'npm']
    missing = []
    
    for cmd in required:
        try:
            subprocess.run([cmd, '--version'], capture_output=True)
        except FileNotFoundError:
            missing.append(cmd)
    
    return missing

def setup_environment():
    """Set up virtual environment and install dependencies"""
    # Create virtual environment
    subprocess.run([sys.executable, '-m', 'venv', '.venv'])
    
    # Activate virtual environment
    if sys.platform == 'win32':
        python = '.venv\\Scripts\\python'
        pip = '.venv\\Scripts\\pip'
    else:
        python = '.venv/bin/python'
        pip = '.venv/bin/pip'
    
    # Install Python dependencies
    subprocess.run([pip, 'install', '-r', 'requirements.txt'])
    
    # Install Playwright browsers
    subprocess.run([python, '-m', 'playwright', 'install', 'chromium'])

def setup_directories():
    """Create necessary directories"""
    dirs = ['data', 'logs', 'reports']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)

def main():
    print("🚀 Setting up Apon Price Monitor")
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Please install missing dependencies and try again")
        return
    
    # Setup directories
    print("📁 Creating directories...")
    setup_directories()
    
    # Setup virtual environment
    print("🐍 Setting up Python environment...")
    setup_environment()
    
    print("✅ Setup complete!")
    print("\nTo start the application, run:")
    print("python launch.py")

if __name__ == "__main__":
    main()
