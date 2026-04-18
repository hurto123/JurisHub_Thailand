# JurisHub_Thailand

# 🏛️ JurisHub Thailand - Centralized Law Study Platform

**JurisHub Thailand** คือหลักฐานทางวิชาการและแพลตฟอร์มเพื่อนักศึกษานิติศาสตร์ ซึ่งรวบรวมวิชากฎหมาย สรุปบทเรียน และคลังข้อสอบเก่าจากมหาวิทยาลัยชั้นนำของไทย (เช่น มธ., จุฬาฯ, รามคำแหง) มาไว้ในที่เดียว โดยเน้นความสวยงาม การใช้งานที่ง่าย (UX/UI) และความถูกต้องของข้อมูล

---

## ✨ Key Features (ฟีเจอร์เด่น)

### 1. Subject Catalog & Search
- ค้นหาวิชาที่ต้องการได้อย่างรวดเร็วผ่านระบบ Smart Search (รหัสวิชา หรือ ชื่อวิชา)
- ระบบตัวกรอง (Filter) ชั้นสูงตามหมวดหมู่ (แพ่ง, อาญา, มหาชน, ฯลฯ) และตามมหาวิทยาลัยที่เปิดสอน
- Modal แสดงรายละเอียดวิชาพร้อมคำอธิบายเบื้องต้นก่อนเข้าสู่บทเรียน

### 2. Smart Subject Viewer
- หน้าต่างอ่านเนื้อหาที่แบ่งเป็น Layer อย่างชัดเจน (ตัวบทกฎหมาย, คำอธิบาย, หมายเหตุ)
- สารบัญ (Sidebar Menu) ที่ช่วยให้นำทางระหว่างบทเรียนได้สะดวก
- แถบแสดงความคืบหน้า (Progress Bar) เพื่อติดตามการเรียนรู้

### 3. Exam Archive with Blur-Toggle
- คลังข้อสอบเก่าที่รวบรวมคำถามจริงจากสนามสอบ
- **ฟีเจอร์เด่น:** ระบบซ่อนคำตอบ (Blur-Toggle) เพื่อให้นักศึกษาได้ลองฝึกทำข้อสอบจริงก่อนดูเฉลย

### 4. AI-Powered OCR Infrastructure
- แพลตฟอร์มรองรับการขยายเนื้อหาด้วย AI Pipeline
- ใช้สคริปต์ **GOT-OCR2.0** ในการสกัดข้อความจากหนังสือเรียนและตัวบทกฎหมาย
- ระบบ Post-processing อัตโนมัติเพื่อแก้ไขปัญหาภาษาไทย (สระลอย, เลขไทย) และจัดรูปแบบ JSON

---

## 🛠️ Tech Stack (เทคโนโลยีที่ใช้)

### Frontend (User Interface)
- **Languages:** HTML5, CSS3, JavaScript (Vanilla ES6+)
- **CSS Framework:** [Tailwind CSS](https://tailwindcss.com/) (Via CDN for MVP)
- **Typography:** Prompt & Sarabun (Google Fonts)
- **Design:** Modern Glassmorphism & Midnight Blue Palette

### Backend & AI Pipeline
- **Python 3.10+**
- **Inference Model:** [GOT-OCR2.0](https://github.com/stepfun-ai/GOT-OCR2.0) (Optimized for 4GB VRAM)
- **Data Structure:** JSON-based Layered Content

---

## 📂 Project Structure (โครงสร้างไฟล์)

```text
LAW_WAT/
├── index.html          # หน้าแรก (Hero & Stats)
├── catalog.html        # หน้าคลังวิชาและ Filter
├── viewer.html         # หน้าอ่านเนื้อหาบทเรียน
├── exam.html           # หน้าคลังข้อสอบเก่า
├── about.html          # หน้าเกี่ยวกับเราและนโยบาย DMCA
│
├── css/
│   └── styles.css      # Design System และ Custom Utilities
│
├── js/
│   ├── app.js          # Logic หน้าแรก
│   ├── catalog.js      # Logic การค้นหาและกรองวิชา
│   ├── viewer.js       # Logic การเรนเดอร์บทเรียน
│   ├── exam.js         # Logic การซ่อน/แสดงคำตอบข้อสอบ
│   ├── data.js         # Mock Data รายชื่อวิชา
│   └── content-data.js # Mock Data เนื้อหาบทเรียนและข้อสอบ
│
├── ai_pipeline/         # ระบบประมวลผล AI
│   ├── test_ocr.py      # สคริปต์รัน OCR Inference
│   └── post_process.py  # สคริปต์แก้สระลอยและแยกโครงสร้างข้อมูล
│
└── ocr_setup.bat       # สคริปต์ติดตั้ง Environment สำหรับ Windows
```

---

## 🚀 Getting Started (วิธีการใช้งาน)

### สำหรับผู้ใช้ทั่วไป (Frontend Only)
1. ดาวน์โหลดหรือ Clone โฟลเดอร์ `LAW_WAT`
2. เปิดไฟล์ `index.html` ผ่านเว็บเบราว์เซอร์ (แนะนำให้ใช้ Extension เช่น *Live Server* ใน VS Code)

### สำหรับนักพัฒนา (AI OCR Setup)
1. ตรวจสอบว่าเครื่องมี **Anaconda/Miniconda** และการ์ดจอ NVIDIA (แนะนำ RTX 3050+)
2. รันไฟล์ `ocr_setup.bat` เพื่อติดตั้ง Environment อัตโนมัติ
3. เข้าโหมด Conda: `conda activate jurishub-ocr`
4. ทดสอบรัน OCR: `python ai_pipeline/test_ocr.py --image <path_to_image>`

---

## ⚖️ Copyright & DMCA (ลิขสิทธิ์)
เนื้อหาใน JurisHub Thailand มุ่งเน้นเพื่อประโยชน์ทางการศึกษา:
- **ตัวบทกฎหมาย:** เป็นข้อมูลสาธารณะ (Public Domain)
- **เนื้อหาสรุป:** เรียบเรียงใหม่ภายใต้หลักการ Fair Use พร้อมอ้างอิงแหล่งที่มา
- **DMCA:** หากพบเนื้อหาละเมิดลิขสิทธิ์ แจ้งลบได้ที่ `dmca@jurishub.in.th`

---
**JurisHub Thailand** - *"Empowering Law Students Through Technology"*
