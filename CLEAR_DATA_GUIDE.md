# 🗑️ วิธีเคลียร์ข้อมูลประวัติการวิเคราะห์

**เมื่อ:** ต้องการลบ Analysis Sessions ทั้งหมด เพื่อเริ่มวิเคราะห์ใหม่  
**ข้อมูลที่จะลบ:** ✗ Analysis Sessions + Predictions  
**ข้อมูลที่เก็บไว้:** ✓ Lottery Draws (ข้อมูลการออกรางวัล)

---

## 🚀 วิธีที่ 1: ใช้ Terminal (อนุเสาะ)

### ขั้นตอน:

```bash
# 1. เปิด Terminal / Command Prompt
# 2. ไปที่โฟลเดอร์โปรเจค
cd "/Users/watt/Private Watt/Develop/Lottery Prediction/lottery_guide"

# 3. เปิด Virtual Environment
source venv/bin/activate

# 4. รันคำสั่งเคลียร์ข้อมูล
python manage.py clear_analysis
```

### ผลลัพธ์:
```
⚠️  จะลบข้อมูลดังต่อไปนี้:
  • Analysis Sessions (งวดวิเคราะห์): 5 งวด
  • Predictions (เลขที่ทำนาย): 25 เลข

❓ ต้องการดำเนินการลบข้อมูลจริงหรือ? (yes/no): yes

✓ ลบ 25 เลขที่ทำนาย
✓ ลบ 5 งวดวิเคราะห์

✅ เสร็จสมบูรณ์!
  ข้อมูลประวัติการวิเคราะห์ทั้งหมดได้ถูกลบแล้ว
  📝 ข้อมูลการออกรางวัล (Lottery Draws) ยังอยู่
  🚀 พร้อมวิเคราะห์ใหม่ได้แล้ว!
```

---

## ⚡ วิธีที่ 2: ใช้ Terminal + Confirm (ไม่ต้องตอบ)

ถ้าต้องการข้ามการยืนยัน:

```bash
python manage.py clear_analysis --confirm
```

**⚠️ หมายเหตุ:** ตัวเลือก `--confirm` จะลบข้อมูลทันทีโดยไม่ถามซ้ำ

---

## 📊 ข้อมูลที่จะลบ

| ข้อมูล | สถานะ | หมายเหตุ |
|--------|-------|---------|
| **Analysis Sessions** | ✗ ลบ | งวดวิเคราะห์ทั้งหมด |
| **Predictions** | ✗ ลบ | เลขทำนายทั้งหมด |
| **Lottery Draws** | ✓ เก็บ | ข้อมูลการออกรางวัลยังอยู่ |
| **Formula Configs** | ✓ เก็บ | ตั้งค่าสูตรยังอยู่ |

---

## ✅ ตรวจสอบหลังเคลียร์

หลังจากเคลียร์ข้อมูล ตรวจสอบดังนี้:

### 1️⃣ ในแอป:
```
🏠 Dashboard
  └─ ไม่มี "ประวัติการวิเคราะห์" ✓

📋 ประวัติการวิเคราะห์
  └─ ว่างเปล่า ✓

✅ ตรวจสอบ
  └─ ไม่มี "Analysis Sessions ที่ต้องตรวจสอบ" ✓
```

### 2️⃣ ในฐานข้อมูล (Django Admin):
```
/admin/analysis/analysissession/
  └─ ว่างเปล่า (0 sessions) ✓

/admin/analysis/predictionentry/
  └─ ว่างเปล่า (0 predictions) ✓

/admin/analysis/lottarydraw/
  └─ ยังมี (✓ สำคัญ!)
```

---

## 🎯 เริ่มวิเคราะห์ใหม่

หลังเคลียร์ข้อมูล:

```
1. 🏠 ไปหน้า Dashboard
2. 📊 ไปหน้า "วิเคราะห์"
3. ⚙️ ตั้งค่า (History, Reference Draw, Target Date)
4. 🚀 กด "วิเคราะห์ตอนนี้"
5. 📈 ดูผลลัพธ์ใหม่
```

---

## ⚠️ สิ่งที่ต้องระวัง

### ❌ ข้อมูลที่จะหายไป:
```
• งวดวิเคราะห์ทั้งหมด (Analysis Sessions)
• เลขทำนายทั้งหมด (Predictions)
• ประวัติการตรวจสอบ (Verified Results)
• Dashboard data
• Analysis History
```

### ✅ ข้อมูลที่จะเก็บ:
```
• ข้อมูลการออกรางวัล (Lottery Draws)
• ตั้งค่าสูตร (Formula Configs)
• ความเป็นส่วนตัว (ไม่มี user data)
```

---

## 🔄 กู้คืนข้อมูล

**ไม่สามารถกู้คืนได้หลังเคลียร์!**

ดังนั้น:
- ✅ **ก่อนเคลียร์:** ดาวน์โหลด/บันทึกข้อมูลถ้าต้องการ
- ⚠️ **หลังเคลียร์:** ข้อมูลหายไปตลอด

---

## 💡 เคล็ดลับ

### 1️⃣ สำรองข้อมูลก่อน (ถ้ากังวล)
```bash
# ส่งออก Lottery Draws เป็น CSV
python manage.py dumpdata analysis.LotteryDraw > draws_backup.json
```

### 2️⃣ เคลียร์บ่อย ๆ?
```bash
# ทำให้เป็นแบบอัตโนมัติ (ถ้าต้องการ)
# สร้าง cronjob หรือ scheduled task
```

### 3️⃣ ลบแบบบางส่วน (ถ้าต้องการ)
```bash
# ใช้ Django Admin ไปที่ /admin/analysis/
# เลือก Sessions ที่ต้องการลบ
# กดปุ่ม "Delete"
```

---

## 🚨 Emergency: ลบเอง (Advanced)

ถ้า command ไม่ทำงาน ลองใช้ Django Shell:

```bash
# 1. เปิด Django Shell
python manage.py shell

# 2. วาง code นี้:
from apps.analysis.models import AnalysisSession, PredictionEntry

# 3. ลบ Predictions ก่อน
PredictionEntry.objects.all().delete()
print("Predictions deleted!")

# 4. ลบ Sessions
AnalysisSession.objects.all().delete()
print("Analysis Sessions deleted!")

# 5. ปิด shell
exit()
```

---

## ✨ สรุป

| ขั้นตอน | วิธี | เวลา |
|--------|------|------|
| 1️⃣ เปิด Terminal | `terminal` | 30 วินาที |
| 2️⃣ ไปโฟลเดอร์โปรเจค | `cd ...` | 10 วินาที |
| 3️⃣ เปิด venv | `source venv/bin/activate` | 5 วินาที |
| 4️⃣ รัน clear_analysis | `python manage.py clear_analysis` | 2 วินาที |
| 5️⃣ ยืนยัน | ตอบ `yes` | 1 วินาที |
| **รวม** | | **~50 วินาที** |

---

**✅ เสร็จแล้ว! พร้อมวิเคราะห์ใหม่ได้แล้ว! 🎯**

---

## 📞 ต้องการช่วยเหลือ?

```
❓ "Command ไม่ทำงาน"
└─ ตรวจสอบ: source venv/bin/activate แล้วหรือ

❓ "ต้องการลบเฉพาะบางส่วน"
└─ ไปที่ /admin/analysis/ เลือกเอง

❓ "ต้องการเก็บข้อมูล"
└─ รัน dumpdata ก่อนเคลียร์

❓ "หลังเคลียร์แล้วมีปัญหา"
└─ ข้อมูล Lottery Draws ยังอยู่
└─ Formula Configs ยังอยู่
└─ วิเคราะห์ใหม่ได้เลย
```

---

**Happy fresh start! 🚀**
