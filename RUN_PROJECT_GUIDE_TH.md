# 🚀 คู่มือการรันโปรเจค LottoAI

**สำหรับผู้ที่ติดตั้งเสร็จแล้ว ต้องการรันโปรเจค**

---

## 📋 สิ่งที่ต้องเตรียม

✅ Python ติดตั้งแล้ว  
✅ โปรเจคติดตั้งแล้ว  
✅ Database migrate แล้ว  
✅ Superuser สร้างแล้ว  

*ถ้ายังไม่ได้ → อ่าน `INSTALLATION_GUIDE_TH.md` ก่อน*

---

## 🎯 วิธีรัน: 2 แบบ

### **แบบที่ 1: ใช้ GUI Launcher (ง่ายสุด!) ⭐ แนะนำ**

ดูส่วน "GUI Launcher" ด้านล่าง → ดับเบิลคลิก → เสร็จ!

---

### **แบบที่ 2: ใช้ Command Line (Manual)**

#### **Step 1: เปิด Terminal / Command Prompt**

**Windows:**
```
1. กด Windows + R
2. พิมพ์ "cmd"
3. กด Enter
```

**Mac:**
```
1. กด Command + Space
2. พิมพ์ "Terminal"
3. กด Enter
```

**Linux:**
```
เปิด Terminal จาก Applications
```

---

#### **Step 2: ไปที่โฟลเดอร์โปรเจค**

```bash
# Windows:
cd "C:\Users\YourName\Desktop\lottery-guide"

# Mac/Linux:
cd ~/Desktop/lottery-guide
# หรือ
cd /path/to/lottery-guide
```

---

#### **Step 3: เปิด Virtual Environment**

```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

**ถ้าสำเร็จ** จะเห็น `(venv)` ที่ด้านหน้า:
```
(venv) C:\Users\...\lottery-guide>
```

---

#### **Step 4: รัน Development Server**

```bash
python manage.py runserver
```

**รอสักครู่ (10-15 วินาที)** จนเห็น:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

#### **Step 5: เปิดเว็บไซต์**

```
ไปที่เบราว์เซอร์ แล้วพิมพ์:
http://127.0.0.1:8000
หรือ
http://localhost:8000
```

**ถ้าสำเร็จ** จะเห็น:
- 🏠 LottoAI Dashboard
- ดีไซน์สวยงาม
- พร้อมใช้งาน!

---

## 🖥️ GUI Launcher (ง่ายสุด!)

### **วิธี: ดับเบิลคลิก = รัน**

**Windows:**
```
1. เปิด Folder: C:\...\lottery-guide\
2. มองหาไฟล์: run_windows.bat
3. ดับเบิลคลิก
4. Command Prompt เปิด → Server รัน
5. เบราว์เซอร์เปิดอัตโนมัติ
```

**Mac/Linux:**
```
1. เปิด Folder: ~/lottery-guide/ หรือ /path/to/...
2. มองหาไฟล์: run_mac.sh หรือ run_linux.sh
3. ดับเบิลคลิก (หรือ Right-click → Open)
4. Terminal เปิด → Server รัน
5. เบราว์เซอร์เปิดอัตโนมัติ
```

**ถ้า Launcher ไม่มี → สร้างได้เอง (ดูส่วน "สร้าง Launcher")**

---

## 🖥️ วิธีปิด Server

### **วิธี 1: Keyboard Shortcut**
```
ที่ Terminal/Command Prompt ที่ Server กำลังรัน:
1. กด Ctrl + C (ค้างไว้ 1-2 วินาที)
2. Server จะปิด
```

**Output:**
```
^C
KeyboardInterrupt
```

### **วิธี 2: ปิด Terminal**
```
ปิด Terminal/Command Prompt window
Server จะปิดอัตโนมัติ
```

### **วิธี 3: GUI Launcher ปิด Server**
```
(หากมี "Stop Server" button ใน Launcher)
คลิกปุ่ม → Server ปิด
```

---

## 📝 ข้อมูลการเข้าใช้งาน

### **หน้า Admin:**
```
URL: http://localhost:8000/admin/
Username: admin (ที่คุณสร้าง)
Password: (รหัสที่คุณตั้ง)
```

### **หน้า Main:**
```
URL: http://localhost:8000/
- Dashboard
- ผลการออกรางวัล
- วิเคราะห์
- ประวัติการวิเคราะห์
- ตรวจสอบ
- ตั้งค่าสูตร
```

---

## 🚨 ปัญหาทั่วไป

### ❌ "Port 8000 already in use"
```
สาเหตุ: โปรเจคอื่นใช้พอร์ต 8000

วิธีแก้:
python manage.py runserver 8080
# หรือพอร์ต 8888, 3000, เป็นต้น
```

### ❌ "Module not found"
```
สาเหตุ: venv ไม่เปิด หรือ packages ไม่ติดตั้ง

วิธีแก้:
1. ตรวจสอบ (venv) อยู่ที่หน้า
2. ติดตั้ง packages:
   pip install -r requirements.txt
```

### ❌ "No such table"
```
สาเหตุ: Database ไม่ migrate

วิธีแก้:
python manage.py migrate
```

### ❌ "Superuser required"
```
สาเหตุ: ยังไม่สร้าง admin account

วิธีแก้:
python manage.py createsuperuser
```

### ❌ "ModuleNotFoundError: No module named 'venv'"
```
สาเหตุ: venv ไม่สร้าง

วิธีแก้:
python -m venv venv
source venv/bin/activate (Mac/Linux)
venv\Scripts\activate (Windows)
```

---

## 📖 ใช้งานหลังรัน

### **ขั้นตอน 1: เข้า Main Page**
```
ไปที่ http://localhost:8000
จะเห็น Dashboard
```

### **ขั้นตอน 2: เพิ่มผลการออกรางวัล**
```
Dashboard → "เพิ่มการออกรางวัล"
กรอก:
- วันที่ออกรางวัล
- รางวัลที่ 1 (6 หลัก)
- อื่นๆ (ตามต้องการ)
บันทึก
```

### **ขั้นตอน 3: วิเคราะห์**
```
Dashboard → "วิเคราะห์"
ตั้งค่า:
- ประเภทหวย (2D/3F/3B)
- จำนวน History
- Reference Draw
- Target Date (optional)
กด "วิเคราะห์ตอนนี้"
```

### **ขั้นตอน 4: ดูผลลัพธ์**
```
คลิกผลลัพธ์ → Analysis Detail
├─ Option A (ความถี่)
├─ Option B (คะแนน)
└─ Formula Breakdown
```

### **ขั้นตอน 5: สร้างเลข 6 หลัก**
```
Hover ที่เลข → "🎲 สร้าง 6 หลัก"
ได้เลข 6 หลัก 1000 ตัว
Copy/Download/Print
```

---

## 🔄 ทำวนซ้ำ

```
วิเคราะห์ → ได้ผล → เล่นหวย
    ↓
รอวันออกรางวัล
    ↓
ไปหน้า "ตรวจสอบ"
    ↓
เลือก Analysis Session
    ↓
เลือกวันการออกรางวัลจริง
    ↓
ดูผล (Hit/Miss)
    ↓
ปรับปรุงการวิเคราะห์
    ↓
วิเคราะห์ใหม่
```

---

## 💡 เคล็ดลับ

### ✅ Server ค้างอยู่?
```
1. กด Ctrl+C ที่ Terminal
2. หรือปิด Terminal
3. หรือเปิด Task Manager → ฆ่า Python
```

### ✅ ลืมเปิด venv?
```
จะได้ error: "Module not found"
วิธีแก้: เปิด venv ก่อน
```

### ✅ ต้องการเปลี่ยนพอร์ต?
```
python manage.py runserver 8080
python manage.py runserver 0.0.0.0:3000
```

### ✅ ต้องการให้เพื่อน access?
```
ต้องเปิด Server ด้วย:
python manage.py runserver 0.0.0.0:8000

แล้วให้เพื่อนเข้าที่:
http://[Your-IP]:8000
# หา IP: ipconfig (Windows) หรือ ifconfig (Mac/Linux)
```

---

## 📚 ไฟล์เอกสารอื่น

```
📖 INSTALLATION_GUIDE_TH.md
   └─ วิธีติดตั้งโปรเจค

📖 RUN_PROJECT_GUIDE_TH.md (ไฟล์นี้)
   └─ วิธีรันโปรเจค

📖 ANALYSIS_GUIDE.md
   └─ วิธีใช้งาน Analysis Feature

📖 QUICK_REFERENCE.md
   └─ Quick reference (พิมพ์ได้)

📖 GENERATE_6DIGIT_GUIDE.md
   └─ วิธีใช้ Generate 6-Digit
```

---

## 🎯 ต่อไป

เมื่อ Server รันแล้ว → ไปใช้งานได้ เลย!

👉 อ่าน **ANALYSIS_GUIDE.md** เพื่อเรียนรู้วิธีใช้งาน Analysis

---

## 📞 ต้องการความช่วยเหลือ?

```
❓ "Server ไม่รัน"
└─ ลองตรวจสอบ venv และ migrations

❓ "Error หลังรัน"
└─ อ่านข้อความ error ให้ดี
└─ ลองตรวจสอบ Port

❓ "ต้องการปิด Server"
└─ กด Ctrl+C หรือปิด Terminal

❓ "ต้องการรันใหม่"
└─ ปิด Server → เปิด Terminal ใหม่ → อ้างอิงขั้นตอนด้านบน
```

---

**✅ Server พร้อมรัน! 🚀**

**⏭️ ต่อไป:** `ANALYSIS_GUIDE.md` สำหรับใช้งาน
