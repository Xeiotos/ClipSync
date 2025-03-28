#!/bin/bash

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment and install requirements
source .venv/bin/activate
pip install -r requirements.txt

echo "Virtual environment created and dependencies installed!"
echo "To activate the virtual environment, run: source .venv/bin/activate" 