#!/bin/bash
# Directory Manager Web Application Launcher

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the application directory
cd "$DIR"

# Activate virtual environment
source venv/bin/activate

# Install Flask if not already installed
pip install flask

# Run the web application
python web_app.py
