@echo off
setlocal enabledelayedexpansion

:: Define the name of the virtual environment folder
set VENV_DIR=venv_win

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Error: requirements.txt not found!
    exit /b 1
)

:: Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    exit /b 1
)

:: Create a virtual environment if it doesn't already exist
if not exist "%VENV_DIR%" (
    echo Creating a virtual environment...
    python -m venv "%VENV_DIR%"
) else (
    echo Virtual environment already exists.
)

:: Activate the virtual environment
echo Activating the virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

:: Deactivate the virtual environment after setup
echo
echo "Setup complete. To activate the virtual environment, run:"
echo "    %VENV_DIR%\Scripts\activate.bat"
echo "And to run the project, run:"
echo "    python3 main.py"
echo
endlocal
