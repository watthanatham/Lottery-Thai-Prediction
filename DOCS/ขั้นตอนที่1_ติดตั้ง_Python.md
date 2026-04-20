# 📥 ขั้นตอนที่ 1: ติดตั้ง Python

**เป้าหมาย:** ติดตั้ง Python 3.10+ เพื่อให้โปรเจค LottoAI รันได้

---

## 🪟 Windows

### **ขั้นตอน:**

1. **ไปที่เว็บไซต์ Python**
   - เปิด: https://www.python.org/downloads/
   - ดาวน์โหลด Python 3.10 หรือสูงกว่า

2. **รัน Installer**
   - ดับเบิลคลิก `python-3.x.x-amd64.exe`
   - ⚠️ **สำคัญ:** เช็ค ✓ "Add Python to PATH" ก่อน Click Install
   - รอจนเสร็จ → Click Finish

3. **ตรวจสอบ Installation**
   - เปิด Command Prompt (Windows Key + R → พิมพ์ `cmd` → Enter)
   - พิมพ์: `python --version`
   - ต้องเห็น: `Python 3.10.x` หรือสูงกว่า

**✅ เสร็จ!** ไปขั้นตอนที่ 2

---

## 🍎 Mac

### **ขั้นตอน:**

1. **ติดตั้ง Homebrew (ถ้ายังไม่มี)**
   - เปิด Terminal (Command + Space → พิมพ์ `terminal`)
   - คัดลอก + วางคำสั่งนี้:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   - รอสักครู่

2. **ติดตั้ง Python ผ่าน Homebrew**
   - พิมพ์:
   ```bash
   brew install python@3.12
   ```
   - รอจนเสร็จ

3. **ตรวจสอบ Installation**
   - พิมพ์: `python3 --version`
   - ต้องเห็น: `Python 3.12.x` หรือคล้ายๆ

**✅ เสร็จ!** ไปขั้นตอนที่ 2

---

## 🐧 Linux (Ubuntu/Debian)

### **ขั้นตอน:**

1. **เปิด Terminal**
   - Press Ctrl + Alt + T

2. **อัปเดต Package Manager**
   ```bash
   sudo apt update
   ```

3. **ติดตั้ง Python**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
   - ตอบ `y` เมื่อถาม

4. **ตรวจสอบ Installation**
   ```bash
   python3 --version
   ```
   - ต้องเห็น: `Python 3.10.x` ขึ้นไป

**✅ เสร็จ!** ไปขั้นตอนที่ 2

---

## ❓ ถ้า Python Installation ล้มเหลว?

### **❌ "python: command not found"**
- Windows: รีตัดตั้งและเช็คให้แน่ว่า "Add Python to PATH" ถูกเลือก
- Mac: ลอง `python3` แทน `python`
- Linux: รันคำสั่ง `sudo apt install python3` ใหม่

### **❌ "Version too old"**
- ต้อง Python 3.10+ ขึ้นไป
- ดาวน์โหลดเวอร์ชั่นใหม่จาก python.org

---

## 🎯 ขั้นตอนต่อไป

✅ Python ติดตั้งแล้ว? → ไป [ขั้นตอนที่ 2: ติดตั้งโปรเจค](ขั้นตอนที่2_ติดตั้ง_โปรเจค.md)

---

**💡 Tips:**
- Python ต้องติดตั้งเพียงครั้งเดียว บนคอมพิวเตอร์ของคุณ
- เวอร์ชั่นที่ทำงานได้: 3.10, 3.11, 3.12
