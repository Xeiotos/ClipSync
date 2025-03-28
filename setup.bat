@echo off

:: Create virtual environment
python -m venv .venv

:: Activate virtual environment and install requirements
call .venv\Scripts\activate.bat
pip install -r requirements.txt

echo Virtual environment created and dependencies installed!
echo To activate the virtual environment, run: .venv\Scripts\activate.bat 