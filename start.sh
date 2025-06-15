#!/bin/bash
echo "Starting Apon AI - Grocery Price Monitor"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Create and activate virtual environment
echo -e "\nSetting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install Python dependencies
echo -e "\nInstalling Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing Python dependencies"
    exit 1
fi

# Install Node.js dependencies
echo -e "\nInstalling Node.js dependencies..."
cd apps/web
npm install
if [ $? -ne 0 ]; then
    echo "Error installing Node.js dependencies"
    exit 1
fi
cd ../..

echo -e "\nInstallation complete! Starting the application..."
echo

# Make the script executable
chmod +x run.py

# Start the application
python run.py

echo -e "\nApplication started! You can access it at: http://localhost:3000"
