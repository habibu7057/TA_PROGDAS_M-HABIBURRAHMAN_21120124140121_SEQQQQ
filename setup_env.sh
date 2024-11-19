#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the name of the virtual environment folder
VENV_DIR="venv_lnx"

# Check if a requirements.txt file exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Create a virtual environment if it doesn't already exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install the requirements from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo
echo "Setup complete. To activate the virtual environment, run:"
echo "    source $VENV_DIR/bin/activate"
echo "And to run the project, run:"
echo "    python3 main.py"
echo
