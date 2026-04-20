# การนำเข้าข้อมูลลอตเตอรี่ (Importing Lottery Data)

## ขั้นตอนการนำเข้าข้อมูล

### วิธีที่ 1: ใช้ script (แนะนำ)

1. **เตรียมไฟล์ CSV** 
   - วางไฟล์ CSV ไว้ในโฟลเดอร์โครงการหลัก (ชื่นเดียวกับ manage.py)

2. **เปิด Terminal/Command Prompt** 
   - นำทางไปที่โฟลเดอร์โครงการ

3. **เรียกใช้ script import** 
   ```bash
   # เปิดใช้งาน virtual environment
   source venv/bin/activate    # บน macOS/Linux
   # หรือ
   venv\Scripts\activate        # บน Windows
   
   # รันการนำเข้า
   python import_csv_data.py lottery_analysis_10years.csv
   ```

4. **ตรวจสอบผลลัพธ์**
   - Script จะแสดงจำนวนบันทึกที่นำเข้าสำเร็จ
   - กำหนดจำนวนแถวที่ข้ามและข้อผิดพลาด

### วิธีที่ 2: ใช้ Django Management Command

ถ้าโฟลเดอร์ management/commands ได้สร้างขึ้นแล้ว:

```bash
source venv/bin/activate
python manage.py import_lottery_data lottery_analysis_10years.csv
```

## ไฟล์ CSV ที่ต้องการ

ไฟล์ CSV ต้องมีคอลัมน์ต่อไปนี้:
- วันที่ออกรางวัล (รูปแบบ: DD/MM/YYYY)
- ปีพุทธศักราช
- เลขรางวัลที่ 1 (6 หลัก)
- เลขหน้า 3 ตัว 1
- เลขหน้า 3 ตัว 2
- เลขท้าย 3 ตัว 1
- เลขท้าย 3 ตัว 2
- เลขท้าย 2 ตัว

## การแปลง พ.ศ. เป็น ค.ศ.

Script จะแปลงวันที่จากปีพุทธศักราช (Buddhist Year) เป็นปีค.ศ. (Gregorian Year) โดยอัตโนมัติ:
- ค.ศ. = พ.ศ. - 543

ตัวอย่าง:
- พ.ศ. 2565 → ค.ศ. 2022
- พ.ศ. 2566 → ค.ศ. 2023

## การแก้ไขปัญหา

### ปัญหา: "disk I/O error"
- ลบไฟล์ db.sqlite3 และรันการ migrate อีกครั้ง
- ลองปิด application ทั้งหมดและลองใหม่

### ปัญหา: "File not found"
- ตรวจสอบว่าไฟล์ CSV อยู่ในโฟลเดอร์โครงการที่ถูกต้อง
- ใช้เส้นทางเต็ม (full path) หากต้องการ

### ปัญหา: "Bad CSV format"
- ตรวจสอบการเข้ารหัส (encoding) - ต้องเป็น UTF-8
- ตรวจสอบชื่อคอลัมน์ว่าตรงกับตัวอักษรและช่องว่างอย่างแม่นยำ

## หมายเหตุ

- Records ที่มีอยู่แล้ว (ตามวันที่) จะถูกข้ามโดยอัตโนมัติ
- Script จะสร้าง draw_label โดยอัตโนมัติ (เช่น "17 Jan 2022")
- near_first_1 และ near_first_2 จะถูกสร้างอัตโนมัติจาก first_prize
