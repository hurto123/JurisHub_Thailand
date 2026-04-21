# 📝 ระบบ OCR สำหรับ JurisHub Thailand

เอกสารนี้อธิบายระบบ OCR หลายแบบที่พัฒนาขึ้นมาเพื่อรองรับการแปลงเอกสารกฎหมายภาษาไทยเป็นข้อความดิจิทัล

---

## 📋 สารบัญ

1. [OCR Methods ที่รองรับ](#ocr-methods-ที่รองรับ)
2. [การติดตั้ง](#การติดตั้ง)
3. [การใช้งาน](#การใช้งาน)
4. [การเปรียบเทียบ](#การเปรียบเทียบ)
5. [การแก้ไขปัญหา](#การแก้ไขปัญหา)

---

## 🔧 OCR Methods ที่รองรับ

### 1. EasyOCR (แนะนำ ⭐)

**ข้อดี:**
- ✅ ฟรี 100% (Open Source)
- ✅ เร็ว (ใช้ CPU ได้ดี)
- ✅ รองรับภาษาไทยดีมาก
- ✅ ไม่ต้องใช้อินเทอร์เน็ต
- ✅ จัดการสระลอยได้ดี

**ข้อเสีย:**
- ⚠️ ต้องดาวน์โหลดโมเดลครั้งแรก (~100MB)
- ⚠️ อาจมีข้อผิดพลาดกับเอกสารคุณภาพต่ำมาก

**เหมาะสำหรับ:**
- เอกสารสแกนทั่วไป
- การประมวลผลปริมาณมาก
- ระบบที่ไม่มี GPU

---

### 2. Deepseek Vision (Premium)

**ข้อดี:**
- ✅ แม่นยำสูงสุด
- ✅ เข้าใจบริบทเอกสารกฎหมาย
- ✅ รองรับเอกสารซับซ้อน
- ✅ แก้ไขสระลอยอัตโนมัติ

**ข้อเสีย:**
- ❌ มีค่าใช้จ่าย (ตามการใช้งาน API)
- ❌ ต้องใช้อินเทอร์เน็ต
- ❌ ช้ากว่า (ขึ้นกับเครือข่าย)

**เหมาะสำหรับ:**
- เอกสารคุณภาพต่ำ/เสียหาย
- เอกสารสำคัญที่ต้องการความแม่นยำสูง
- ไฟล์ที่ OCR แบบอื่นๆ ทำไม่สำเร็จ

---

### 3. Tesseract OCR (สำรอง)

**ข้อดี:**
- ✅ ฟรี
- ✅ มีอยู่แล้วในบางระบบ
- ✅ เร็ว

**ข้อเสีย:**
- ❌ ภาษาไทยไม่ค่อยดี
- ❌ มีสระลอยบ่อย

**เหมาะสำหรับ:**
- เอกสารภาษาอังกฤษ
- ระบบที่ไม่สามารถติดตั้ง EasyOCR ได้

---

### 4. GOT-OCR2.0 (Legacy)

**ข้อดี:**
- ✅ แม่นยำกับเอกสารทั่วไป
- ✅ รองรับโครงสร้างเอกสาร

**ข้อเสีย:**
- ❌ ต้องใช้ GPU
- ❌ ใช้ VRAM มาก
- ❌ ช้า

**เหมาะสำหรับ:**
- ระบบที่มี GPU รุ่นใหม่
- เอกสารที่ต้องการโครงสร้างซับซ้อน

---

## 📦 การติดตั้ง

### 1. ติดตั้ง Dependencies

```bash
cd ai_pipeline
pip install -r requirements.txt
```

### 2. ดาวน์โหลดโมเดล EasyOCR (ครั้งแรก)

```python
import easyocr
reader = easyocr.Reader(['th', 'en'])
# โมเดลจะดาวน์โหลดอัตโนมัติ (~100MB)
```

### 3. ตั้งค่า Deepseek API (Optional)

**Windows:**
```cmd
set DEEPSEEK_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY=your_api_key_here
```

---

## 🚀 การใช้งาน

### วิธีที่ 1: ใช้ OCR Factory (ง่ายที่สุด)

```python
from ocr_factory import OCFactory

factory = OCFactory()

# Auto-select method
result = factory.process_file("document.pdf", method="auto")

# หรือเลือก method เอง
result = factory.process_file("document.pdf", method="easyocr")

print(result.text)
print(f"Confidence: {result.confidence}%")
```

### วิธีที่ 2: ประมวลผล Inbox (แนะนำ)

```bash
# ประมวลผลทั้ง inbox ด้วย EasyOCR
python step0_multimodal_v2.py --inbox --method easyocr

# หรือใช้ Deepseek
python step0_multimodal_v2.py --inbox --method deepseek

# ประมวลผลซ้ำทั้งหมด
python step0_multimodal_v2.py --inbox --method easyocr --no-skip
```

### วิธีที่ 3: เปรียบเทียบ OCR

```bash
# เปรียบเทียบทั้งสองแบบ
python ocr_comparison.py --input document.pdf --method both

# ใช้เฉพาะ EasyOCR
python ocr_comparison.py --input scan.jpg --method easyocr

# ใช้เฉพาะ Deepseek
python ocr_comparison.py --input scan.jpg --method deepseek
```

### วิธีที่ 4: Batch Processing

```python
from ocr_factory import batch_process

results = batch_process(
    input_dir="data/00_inbox",
    output_dir="data/01_raw_text",
    method="easyocr"
)
```

---

## 📊 การเปรียบเทียบ

### ความเร็ว

| Method | 1 หน้า | 10 หน้า | 100 หน้า |
|---------|--------|---------|----------|
| EasyOCR | 2s | 15s | 2 นาที |
| Deepseek | 5s | 50s | 8 นาที |
| Tesseract | 1s | 8s | 1 นาที |
| GOT-OCR | 10s | 90s | 15 นาที |

### ความแม่นยำ (ภาษาไทย)

| Method | ความแม่นยำ | สระลอย | จัดการเอกสารซับซ้อน |
|---------|-----------|--------|-------------------|
| EasyOCR | 85% | น้อย | ปานกลาง |
| Deepseek | 95% | แก้ให้ | ดีมาก |
| Tesseract | 70% | มาก | พื้นฐาน |
| GOT-OCR | 80% | ปานกลาง | ดี |

### ค่าใช้จ่าย

| Method | ค่าใช้จ่าย | ต้องใช้อินเทอร์เน็ต |
|---------|-----------|-------------------|
| EasyOCR | ฟรี | ไม่ |
| Deepseek | ~$0.01/หน้า | ใช่ |
| Tesseract | ฟรี | ไม่ |
| GOT-OCR | ฟรี | ไม่ |

---

## 🔧 การแก้ไขปัญหา

### ปัญหา: EasyOCR โหลดช้าในครั้งแรก

**แก้ไข:** นี่เป็นปกติ โมเดลจะถูกดาวน์โหลดครั้งแรก (~100MB) ครั้งต่อไปจะเร็ว

### ปัญหา: "ModuleNotFoundError: No module named 'easyocr'"

**แก้ไข:**
```bash
pip install easyocr
```

### ปัญหา: "Deepseek API Key not found"

**แก้ไข:**
```bash
# Windows
set DEEPSEEK_API_KEY=your_key

# หรือสร้างไฟล์ .env
DEEPSEEK_API_KEY=your_key
```

### ปัญหา: สระลอยในข้อความ OCR

**แก้ไข:**
- ใช้ `clean_thai_ocr_text()` จาก `ocr_comparison.py`
- หรือใช้ `step1_5_ocr_corrector_api.py` หลัง OCR

### ปัญหา: CUDA Out of Memory

**แก้ไข:**
- ใช้ EasyOCR แทน GOT-OCR (ใช้ CPU)
- ลดจำนวนหน้าที่ประมวลผลพร้อมกัน

---

## 💡 คำแนะนำ

### สำหรับผู้เริ่มต้น

1. เริ่มต้นด้วย **EasyOCR** (method="easyocr")
2. ทดสอบกับไฟล์ตัวอย่างก่อน
3. ตรวจสอบผลลัพธ์และปรับตามความเหมาะสม

### สำหรับ Production

1. ใช้ **EasyOCR** เป็นหลัก (ประหยัดค่าใช้จ่าย)
2. ใช้ **Deepseek** เฉพาะไฟล์ที่ OCR ไม่สำเร็จ
3. ตั้งค่า `--no-skip` เพื่อประมวลผลซ้ำเมื่อจำเป็น

### สำหรับเอกสารสำคัญ

1. ใช้ **Deepseek** เพื่อความแม่นยำสูงสุด
2. ตรวจสอบผลลัพธ์ทุกครั้ง
3. บันทึกเวอร์ชันดิบไว้เปรียบเทียบ

---

## 📝 Changelog

### v2.0 (ล่าสุด)
- ✨ เพิ่ม EasyOCR support
- ✨ เพิ่ม Deepseek Vision support
- ✨ สร้าง OCR Factory สำหรับเลือก method อัตโนมัติ
- ✨ สร้าง OCR Comparison tool
- ✨ ปรับปรุง step0_multimodal_v2

### v1.0
- 📝 Tesseract OCR (เดิม)
- 📝 GOT-OCR2.0 (เดิม)

---

**หากมีคำถามหรือพบปัญหา กรุณาติดต่อทีมพัฒนา**
