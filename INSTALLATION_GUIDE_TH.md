# 📖 คู่มือการติดตั้งโปรเจค LottoAI

**สำหรับผู้ใช้ที่ต้องการติดตั้งและรันโปรเจครครั้งแรก**

---

## 📋 สิ่งที่ต้องเตรียมก่อน (Prerequisites)

### **1️⃣ ติดตั้ง Python**

#### **Windows:**
```
1. ไปที่ https://www.python.org/downloads/
2. คลิก "Download Python 3.10" หรือใหม่กว่า
3. เปิดไฟล์ installer
4. ✓ เช็ค "Add Python to PATH" 
5. คลิก "Install Now"
6. รอจนเสร็จ (อาจใช้เวลา 2-3 นาที)
```

#### **Mac:**
```
1. ติดตั้ง Homebrew ก่อน:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. ติดตั้ง Python:
   brew install python@3.12
```

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### **2️⃣ ติดตั้ง Git (Optional แต่แนะนำ)**

#### **Windows:**
- ดาวน์โหลดจาก https://git-scm.com/download/win
- รันไฟล์ installer → Next Next... → Finish

#### **Mac:**
```bash
brew install git
```

#### **Linux:**
```bash
sudo apt install git
```

### **3️⃣ ติดตั้ง Visual Studio Code (Optional)**
- ดาวน์โหลดจาก https://code.visualstudio.com/
- ใช้สำหรับแก้ไขไฟล์ (ถ้า/ถ้าต้อง)

---

## 🚀 ขั้นตอนการติดตั้งโปรเจค

### **ขั้นตอนที่ 1: ดาวน์โหลดโปรเจค**

#### **วิธี A: ใช้ Git (แนะนำ)**
```bash
# เปิด Terminal / Command Prompt
git clone https://github.com/your-username/lottery-guide.git
cd lottery-guide
```

#### **วิธี B: ดาวน์โหลดไฟล์ ZIP**
```
1. ไปที่ GitHub page
2. คลิก "Code" → "Download ZIP"
3. แตกไฟล์ ZIP
4. เปิด Folder
```

---

### **ขั้นตอนที่ 2: สร้าง Virtual Environment**

**Virtual Environment** = การแยกโปรเจคนี้ให้มี Python packages เป็นของตัวเองแต่เฉพาะ

#### **Windows (Command Prompt):**
```bash
# ไปที่โฟลเดอร์โปรเจค
cd "C:\Users\YourName\Desktop\lottery-guide"

# สร้าง venv
python -m venv venv

# เปิด venv
venv\Scripts\activate
```

**ถ้าสำเร็จ** จะเห็น `(venv)` ที่ด้านหน้า Command Prompt:
```
(venv) C:\Users\YourName\...\lottery-guide>
```

#### **Mac / Linux (Terminal):**
```bash
# ไปที่โฟลเดอร์โปรเจค
cd /path/to/lottery-guide

# สร้าง venv
python3 -m venv venv

# เปิด venv
source venv/bin/activate
```

**ถ้าสำเร็จ** จะเห็น `(venv)` ที่ด้านหน้า Terminal:
```
(venv) path/to/lottery-guide $
```

---

### **ขั้นตอนที่ 3: ติดตั้ง Dependencies**

**Dependencies** = ไลบรารี่ต่างๆ ที่โปรเจคต้องใช้

```bash
# ตรวจสอบ venv เปิดอยู่ (ต้องเห็น (venv) ที่ด้านหน้า)

# ติดตั้ง packages จาก requirements.txt
pip install -r requirements.txt

# รอสักครู่ (อาจใช้เวลา 1-2 นาที)
```

**ได้ผลลัพธ์เช่นนี้ = ติดตั้งสำเร็จ:**
```
Successfully installed django-4.2.0 djangorestframework-3.14.0 ... (มีรายการหลายอย่าง)
```

---

### **ขั้นตอนที่ 4: ติดตั้งฐานข้อมูล**

**Migration** = สร้างตาราฐานข้อมูล

```bash
# ตรวจสอบ venv ยังเปิดอยู่

# รัน migrations
python manage.py migrate

# ได้ผลลัพธ์เช่นนี้ = สำเร็จ:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, django_htmx, sessions, analysis
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ... (มีอีกหลายอย่าง)
```

---

### **ขั้นตอนที่ 5: สร้าง Superuser (Admin Account)**

**Superuser** = บัญชี Admin ที่ใช้จัดการโปรเจค

```bash
# ตรวจสอบ venv ยังเปิดอยู่

# สร้าง superuser
python manage.py createsuperuser

# ตอบคำถามตามที่ปรากฏ:
# Username: admin
# Email address: your-email@example.com
# Password: (พิมพ์รหัสผ่าน - จะไม่แสดง)
# Password (again): (พิมพ์ซ้ำ)
```

**จำรหัสผ่านไว้!** จะใช้เพื่อเข้า Admin Panel

---

## ✅ ตรวจสอบการติดตั้ง

หลังติดตั้งเสร็จแล้ว ตรวจสอบดังนี้:

```bash
# 1. ตรวจสอบ venv
(venv) lottery-guide $  ← ต้องเห็น (venv)

# 2. ตรวจสอบ Python version
python --version
# ต้องได้ Python 3.10+ ขึ้นไป

# 3. ตรวจสอบ Django
python -c "import django; print(django.get_version())"
# ต้องเห็นเลขเวอร์ชัน เช่น 4.2.0
```

---

## 🚨 ถ้ามีปัญหา

### ❌ "Module not found: django"
```
สาเหตุ: venv ไม่เปิด หรือ requirements ไม่ติดตั้ง

วิธีแก้:
1. ตรวจสอบ (venv) อยู่ที่ด้านหน้า
2. ลองติดตั้ง requirements อีกครั้ง:
   pip install -r requirements.txt
```

### ❌ "Python: command not found" (Mac/Linux)
```
สาเหตุ: Python ไม่ติดตั้ง หรือ PATH ไม่ตั้งค่า

วิธีแก้:
1. ตรวจสอบการติดตั้ง Python:
   python3 --version
2. ใช้ python3 แทน python:
   python3 -m venv venv
   python3 manage.py runserver
```

### ❌ "Permission denied" (Mac/Linux)
```
สาเหตุ: ไม่มีสิทธิ์เขียนไฟล์

วิธีแก้:
chmod -R 755 /path/to/lottery-guide
```

### ❌ "Port 8000 already in use"
```
สาเหตุ: โปรเจคอื่นใช้พอร์ต 8000 อยู่

วิธีแก้:
python manage.py runserver 8080
# ใช้พอร์ต 8080 แทน
```

---

## 📝 สรุปขั้นตอน

| ขั้นตอน | คำสั่ง | เวลา |
|--------|--------|------|
| 1. ติดตั้ง Python | (ดาวน์โหลด) | 5 นาที |
| 2. ดาวน์โหลดโปรเจค | git clone หรือ ZIP | 2 นาที |
| 3. สร้าง venv | python -m venv venv | 30 วินาที |
| 4. เปิด venv | source/activate | 5 วินาที |
| 5. ติดตั้ง packages | pip install -r requirements.txt | 2 นาที |
| 6. Migrate database | python manage.py migrate | 1 นาที |
| 7. สร้าง admin | python manage.py createsuperuser | 1 นาที |
| **รวม** | | **~12 นาที** |

---

## 🎯 ต่อไป

ติดตั้งเสร็จแล้ว! ต่อไปต้อง:

👉 ไปอ่าน **RUN_PROJECT_GUIDE_TH.md** เพื่อรันโปรเจค

หรือ

👉 ใช้ **Project Launcher** (GUI) ที่ง่ายกว่า

---

## 💡 Tips

### ✅ บันทึก Password Superuser
```
Username: admin
Password: (ที่คุณตั้ง)
Email: your-email@example.com

เก็บไว้สำหรับเข้า Admin Panel
```

### ✅ venv ต้องเปิดทุกครั้ง
```
ทุกครั้งที่เปิด Terminal/Command Prompt ใหม่
ต้องรัน:
  source venv/bin/activate (Mac/Linux)
  venv\Scripts\activate (Windows)
```

### ✅ อัปเดต pip
```bash
# ถ้า pip ล้าสมัย
python -m pip install --upgrade pip
```

---

## 📞 ต้องการความช่วยเหลือ?

```
❓ "ไม่รู้ว่าติดตั้งที่ไหน"
└─ ไปที่ C:\Users\YourName\Desktop (Windows)
└─ ไปที่ ~/Desktop (Mac/Linux)
└─ แล้วสร้างโฟลเดอร์ lottery-guide

❓ "ติดตั้งแล้วแต่ยังไม่รู้วิธีรัน"
└─ อ่าน RUN_PROJECT_GUIDE_TH.md

❓ "Python ติดตั้งไม่ได้"
└─ ตรวจสอบระบบปฏิบัติการ (Windows/Mac/Linux)
└─ ลองติดตั้งใหม่จาก python.org

❓ "ขอความช่วยเหลือจาก AI"
└─ ถามหรือแชร์ error message ที่ได้
```

---

**✅ พร้อมทำไปขั้นต่อไป! 🎯**

---

**ไฟล์ต่อไป:** `RUN_PROJECT_GUIDE_TH.md` สำหรับวิธีรันโปรเจค
