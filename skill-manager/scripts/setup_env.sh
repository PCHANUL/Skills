#!/bin/bash

# setup_env.sh
# Installs necessary dependencies for the skill-manager.

echo "Setting up environment for skill-manager..."

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install Python 3."
    exit 1
fi

# Install PyYAML
echo "Installing PyYAML..."
pip3 install pyyaml

if [ $? -eq 0 ]; then
    echo "Environment setup complete."
else
    echo "Error: Failed to install dependencies."
    exit 1
fi
