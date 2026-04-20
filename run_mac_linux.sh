#!/bin/bash

# LottoAI Project Launcher for Mac/Linux
# ทำให้ executable: chmod +x run_mac_linux.sh
# รัน: ./run_mac_linux.sh หรือ ดับเบิลคลิก

# สี ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ตั้งค่า path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   LottoAI Project Launcher${NC}"
echo -e "${BLUE}================================${NC}"
echo

# เช็ค Python ติดตั้งหรือไม่
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 ไม่พบ!${NC}"
    echo "โปรดติดตั้ง Python 3.10+ ก่อน"
    echo "Mac: brew install python@3.12"
    echo "Linux: sudo apt install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ พบ Python ${PYTHON_VERSION}${NC}"
echo

# เช็ค venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  สร้าง Virtual Environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ สร้าง venv ล้มเหลว${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual Environment สร้างสำเร็จ${NC}"
fi

echo
echo -e "${YELLOW}🚀 เปิด Virtual Environment...${NC}"
source venv/bin/activate

# เช็ค requirements
if ! pip list | grep -i "django" > /dev/null 2>&1; then
    echo
    echo -e "${YELLOW}📦 ติดตั้ง Dependencies...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ติดตั้ง packages ล้มเหลว${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Dependencies ติดตั้งสำเร็จ${NC}"
fi

# เช็ค database
if [ ! -f "db.sqlite3" ]; then
    echo
    echo -e "${YELLOW}🗄️  สร้างฐานข้อมูล...${NC}"
    python manage.py migrate
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Migrate ล้มเหลว${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ ฐานข้อมูลสร้างสำเร็จ${NC}"

    echo
    echo -e "${YELLOW}👤 สร้าง Admin Account...${NC}"
    echo "กรอก Username, Email, Password:"
    python manage.py createsuperuser
fi

# รัน Server
echo
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ LottoAI ขณะนี้รันอยู่!${NC}"
echo -e "${BLUE}================================${NC}"
echo
echo -e "${YELLOW}🌐 URL:${NC}"
echo "  Main: http://localhost:8000"
echo "  Admin: http://localhost:8000/admin"
echo
echo -e "${YELLOW}📝 หมายเหตุ:${NC}"
echo "  • เปิดเบราว์เซอร์แล้วไปที่ URL ด้านบน"
echo "  • ปิด Server: กด Ctrl+C"
echo "  • รันใหม่: ./run_mac_linux.sh"
echo
echo -e "${BLUE}================================${NC}"
echo

python manage.py runserver

# ถ้า Server ปิด
echo
echo -e "${YELLOW}ℹ️  Server ปิดแล้ว${NC}"
echo "หากต้องการรันใหม่ รัน: ./run_mac_linux.sh"
echo
