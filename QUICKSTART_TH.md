# ⚡ เริ่มใช้งานอย่างรวดเร็ว (Quick Start)

**สำหรับผู้ที่เพิ่งได้โปรเจคและต้องการรันทันที!**

---

## 🚀 ขั้นตอน 3 ขั้น (5 นาที)

### **ขั้นที่ 1: ติดตั้ง Python (ครั้งเดียว)**

#### **Windows:**
```
1. ไปที่ https://www.python.org/downloads/
2. ดาวน์โหลด Python 3.10+
3. รัน installer → ✓ เช็ค "Add Python to PATH"
4. Finish
```

#### **Mac:**
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12
```

#### **Linux:**
```
sudo apt update && sudo apt install python3 python3-pip
```

---

### **ขั้นที่ 2: ติดตั้งโปรเจค (ครั้งเดียว)**

```bash
# 1. ไปโฟลเดอร์โปรเจค
cd /path/to/lottery-guide

# 2. ติดตั้ง (รันคำสั่งเดียวนี้)
python launcher.py
# หรือ
python3 launcher.py
```

**ถ้ามี GUI Window → ใช้ GUI**  
**ถ้าไม่มี GUI → ใช้ Console Menu**

---

### **ขั้นที่ 3: เปิด Browser**

```
ไปที่: http://localhost:8000
```

**ได้เสร็จ! 🎉**

---

## 🖱️ วิธี Easiest: ดับเบิลคลิก

### **Windows:**
```
เปิด File Explorer
ไปที่: C:\...\lottery-guide\
ดับเบิลคลิก: run_windows.bat
```

### **Mac/Linux:**
```
เปิด Finder / File Manager
ไปที่: ~/lottery-guide/ หรือ /path/to/...
ดับเบิลคลิก: run_mac_linux.sh
(หรือ Right-click → Open with → Terminal)
```

---

## 📋 ไฟล์ที่ต้องรู้

```
📁 lottery-guide/
├─ launcher.py ← คลิกเพื่อรัน (ง่ายสุด)
├─ run_windows.bat ← Windows ดับเบิลคลิก
├─ run_mac_linux.sh ← Mac/Linux ดับเบิลคลิก
│
├─ 📖 INSTALLATION_GUIDE_TH.md ← ติดตั้งละเอียด
├─ 📖 RUN_PROJECT_GUIDE_TH.md ← รันละเอียด
├─ 📖 QUICKSTART_TH.md ← ไฟล์นี้ (เร็วสุด)
│
└─ 🏠 manage.py ← หลัก Django
```

---

## 🎯 ใช้งานหลังรัน

### **หน้า Main:**
```
http://localhost:8000
├─ Dashboard
├─ ผลการออกรางวัล
├─ วิเคราะห์
├─ ประวัติการวิเคราะห์
├─ ตรวจสอบ
└─ ตั้งค่าสูตร
```

### **หน้า Admin:**
```
http://localhost:8000/admin
Username: admin (ที่คุณสร้าง)
Password: (ที่คุณตั้ง)
```

---

## ⚠️ ปัญหาทั่วไป

### "ไม่มี launcher.py"
```
→ ใช้ run_windows.bat (Windows)
→ ใช้ run_mac_linux.sh (Mac/Linux)
```

### "Python: command not found"
```
→ ไปติดตั้ง Python ก่อน
→ https://www.python.org/downloads/
```

### "Port 8000 in use"
```
→ ใช้พอร์ตอื่น:
python manage.py runserver 8080
```

### "Module not found"
```
→ ลบโฟลเดอร์ venv ทั้งหมด
→ รัน launcher.py ใหม่
```

---

## 💡 จากนี้ไป

```
ครั้งแรก:     launcher.py (ติดตั้ง + รัน)
ครั้งต่อไป:   launcher.py (แค่รัน)

หรือ:
ดับเบิลคลิก run_windows.bat / run_mac_linux.sh
```

---

## 📚 อ่านเพิ่มเติม

- **INSTALLATION_GUIDE_TH.md** → ติดตั้งละเอียด
- **RUN_PROJECT_GUIDE_TH.md** → รันละเอียด
- **ANALYSIS_GUIDE.md** → วิธีใช้งาน
- **GENERATE_6DIGIT_GUIDE.md** → สร้างเลข 6 หลัก

---

## ✅ ทำได้แล้ว!

```
ถ้าเห็น:
✅ Server รันที่ http://localhost:8000
✅ สามารถเข้า Dashboard ได้
✅ สามารถเข้า Admin ได้

= พร้อมใช้งานแล้ว! 🎉
```

---

**🚀 ถ้ายังมีปัญหา → อ่านไฟล์ Guide ที่ละเอียด**

**หรือ → ถามความช่วยเหลือในไฟล์คู่มือ**

---

**Happy Coding! 💻✨**
