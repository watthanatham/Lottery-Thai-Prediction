@echo off
REM LottoAI Project Launcher for Windows
REM Run: run_windows.bat or Double-click

setlocal enabledelayedexpansion

cls
echo ================================
echo    LottoAI Project Launcher
echo ================================
echo.

REM Go to project directory
cd /d "%~dp0.."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python ไม่พบ!
    echo โปรดติดตั้ง Python 3.10+ ก่อน
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python พบ

REM Create venv if not exists
if not exist venv (
    echo.
    echo ⚙️  สร้าง Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ สร้าง venv ล้มเหลว
        pause
        exit /b 1
    )
    echo ✅ venv สร้างสำเร็จ
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo 📦 ตรวจสอบ Dependencies...
pip list | findstr /i django >nul 2>&1
if errorlevel 1 (
    echo ติดตั้ง Django...
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo ❌ ติดตั้ง packages ล้มเหลว
        pause
        exit /b 1
    )
)
echo ✅ Dependencies สำเร็จ

REM Create database if not exists
if not exist db.sqlite3 (
    echo.
    echo 🗄️  สร้างฐานข้อมูล...
    python manage.py migrate >nul 2>&1
    if errorlevel 1 (
        echo ❌ Migrate ล้มเหลว
        pause
        exit /b 1
    )
    echo ✅ Database สร้างสำเร็จ

    echo.
    echo 👤 สร้าง Admin Account...
    python manage.py createsuperuser
)

REM Start server
echo.
echo ================================
echo ✅ LottoAI ขณะนี้รันอยู่!
echo ================================
echo.
echo 🌐 URL:
echo   Main: http://localhost:8000
echo   Admin: http://localhost:8000/admin
echo.
echo 📝 หมายเหตุ:
echo   • เปิดเบราว์เซอร์แล้วไปที่ URL ด้านบน
echo   • ปิด Server: กด Ctrl+C
echo   • รันใหม่: run_windows.bat
echo.
echo ================================
echo.

python manage.py runserver

echo.
echo ℹ️  Server ปิดแล้ว
echo หากต้องการรันใหม่ รัน: run_windows.bat
echo.
pause
