@echo off
REM EDVAN DBF Commander Launcher for Windows
REM This batch file launches the EDVAN DBF Commander application

echo ================================================
echo   EDVAN DBF Commander - Starting Application
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import customtkinter, pandas, dbfpy3, openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some required packages are missing!
    echo Installing required packages...
    echo.
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install required packages
        echo Please manually run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies check: OK
echo.

REM Check Stata support
echo Checking Stata support...
python -c "import pyreadstat; print('Stata .dta support: AVAILABLE')" 2>nul
if %errorlevel% neq 0 (
    echo Stata .dta support: NOT AVAILABLE
    echo Note: Run 'python install_stata_support.py' to enable Stata file support
)
echo.

REM Create sample DBF files if they don't exist
if not exist "sample_employees.dbf" (
    echo Creating sample DBF files for testing...
    python create_sample_dbf.py
    echo.
)

REM Launch the application
echo Launching EDVAN DBF Commander...
echo.
python edvan_dbf_commander.py

REM Pause if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)

echo.
echo EDVAN DBF Commander has been closed.
pause
