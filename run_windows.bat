@echo off
REM LottoAI Project Launcher for Windows
REM ดับเบิลคลิกไฟล์นี้เพื่อรันโปรเจค

setlocal enabledelayedexpansion

REM หาตำแหน่งโปรเจค
cd /d "%~dp0"

REM เช็ค Python ติดตั้งหรือไม่
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ไม่พบ! โปรดติดตั้ง Python ก่อน
    echo.
    echo ไปที่: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ ค้นหา Python สำเร็จ
echo.

REM เช็ค venv ติดตั้งหรือไม่
if not exist "venv\Scripts\activate.bat" (
    echo ⚙️ สร้าง Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ สร้าง venv ล้มเหลว
        pause
        exit /b 1
    )
    echo ✅ Virtual Environment สร้างสำเร็จ
)

echo.
echo 🚀 เปิด Virtual Environment...
call venv\Scripts\activate.bat

REM เช็ค requirements ติดตั้งหรือไม่
pip list | find /i "django" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📦 ติดตั้ง Dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ ติดตั้ง packages ล้มเหลว
        pause
        exit /b 1
    )
    echo ✅ Dependencies ติดตั้งสำเร็จ
)

REM เช็ค database ติดตั้งหรือไม่
if not exist "db.sqlite3" (
    echo.
    echo 🗄️ สร้างฐานข้อมูล...
    python manage.py migrate
    if errorlevel 1 (
        echo ❌ Migrate ล้มเหลว
        pause
        exit /b 1
    )
    echo ✅ ฐานข้อมูลสร้างสำเร็จ

    echo.
    echo 👤 สร้าง Admin Account...
    echo หมายเหตุ: กรอก Username, Email, Password
    python manage.py createsuperuser
)

REM รัน Development Server
echo.
echo 🌐 รัน Django Development Server...
echo.
echo ================================================================
echo ✅ LottoAI ขณะนี้รันอยู่!
echo.
echo URL: http://localhost:8000
echo Admin: http://localhost:8000/admin
echo.
echo หมายเหตุ: เปิดเบราว์เซอร์แล้วไปที่ URL ด้านบน
echo ปิด Server ได้โดยกด Ctrl+C ที่หน้านี้
echo ================================================================
echo.

python manage.py runserver

REM ถ้า Server ปิด
echo.
echo ℹ️ Server ปิดแล้ว
echo หากต้องการรันใหม่ ดับเบิลคลิก run_windows.bat อีกครั้ง
echo.
pause
