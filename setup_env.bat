@echo off
setlocal enabledelayedexpansion

:: Define the name of the virtual environment folder
set VENV_DIR=venv_win

:: Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Error: requirements.txt not found!
    exit /b 1
)

:: Determine the correct Python command
set PYTHON_CMD=
for %%P in (python py python3) do (
    %%P --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=%%P
        goto :found
    )
)
:found
if "%PYTHON_CMD%"=="" (
    echo Error: No Python interpreter found in PATH.
    exit /b 1
)

:: Create a virtual environment if it doesn't already exist
if not exist "%VENV_DIR%" (
    echo Creating a virtual environment...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
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
echo Setup complete. To activate the virtual environment, run:
echo     "%VENV_DIR%\Scripts\activate.bat"
echo And to run the project, run:
echo     "%PYTHON_CMD% main.py"
echo Don't forget to deactivate the virtual environment when you're done:
echo     "deactivate"
endlocal