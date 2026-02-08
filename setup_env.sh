#!/bin/bash

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate and Install
echo "Activating venv and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Playwright Browsers
echo "Installing Playwright browsers..."
playwright install

echo "------------------------------------------------"
echo "Setup Complete! To run the app:"
echo "source venv/bin/activate"
echo "streamlit run dashboard.py"
echo "------------------------------------------------"
