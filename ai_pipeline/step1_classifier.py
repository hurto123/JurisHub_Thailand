import os
import json
import requests
import argparse
import shutil
import glob
import re

# -------------------------------------------------------------------------
# Step 1: AI Classifier (นักคัดแยกวิชา)
# อ่านไฟล์ Text ที่ได้มาจาก OCR/PDF แล้วส่งให้ Ollama ทายว่าเป็นวิชาอะไร
# -------------------------------------------------------------------------

def sanitize_name(name: str) -> str:
    # ล้างเครื่องหมายที่ Windows ห้ามใช้ในชื่อโฟลเดอร์ ( \ / : * ? " < > | )
    return re.sub(r'[\\/:*?"<>|]', '-', name).strip()

DATA_DIR = "data"
DIR_IN = os.path.join(DATA_DIR, "01_raw_text")
DIR_OUT = os.path.join(DATA_DIR, "02_classified")

# สร้างโฟลเดอร์ให้พร้อม
DIR_OUT_CONTENT = os.path.join(DATA_DIR, "02_classified")
DIR_OUT_EXAM = os.path.join(DATA_DIR, "04_exam_raw")
DIR_OUT_ARTICLES = os.path.join(DATA_DIR, "01_articles_raw")

for d in [DIR_IN, DIR_OUT_CONTENT, DIR_OUT_EXAM, DIR_OUT_ARTICLES]:
    os.makedirs(d, exist_ok=True)

# List วิชาที่มีเพื่อบอกให้ LLM ทายกรอบนี้
SUBJECT_LIST = """
[1. หมวดพื้นฐานและทฤษฎีกฎหมาย (Fundamentals & Theory)]
- law-fun-01 (ความรู้พื้นฐานเกี่ยวกับกฎหมายและระบบกฎหมาย - Introduction to Law)
- law-fun-02 (ประวัติศาสตร์กฎหมายไทยและต่างประเทศ - Legal History)
- law-fun-03 (นิติปรัชญา - Philosophy of Law)
- law-fun-04 (การใช้และการตีความกฎหมาย - Legal Interpretation)
- law-fun-05 (นิติตรรกศาสตร์และการให้เหตุผลทางกฎหมาย - Legal Logic and Reasoning)
- law-fun-06 (วิชาชีพนักกฎหมายและจรรยาบรรณ - Legal Profession and Ethics)
- law-fun-07 (ภาษากฎหมาย - Legal Language)
- law-fun-08 (สังคมวิทยากฎหมาย - Sociology of Law)
- law-fun-09 (นิติเศรษฐศาสตร์ - Economic Analysis of Law)

[2. หมวดกฎหมายแพ่งและพาณิชย์ (Civil and Commercial Law)]
- law-civ-01 (กฎหมายลักษณะบุคคล - Persons)
- law-civ-02 (กฎหมายลักษณะนิติกรรมและสัญญา - Juristic Acts and Contracts)
- law-civ-03 (กฎหมายลักษณะหนี้ - Obligations)
- law-civ-04 (กฎหมายลักษณะละเมิด จัดการงานนอกสั่ง และลาภมิควรได้ - Delicts)
- law-civ-05 (กฎหมายลักษณะทรัพย์สินและที่ดิน - Property and Land Law)
- law-civ-06 (กฎหมายลักษณะเอกเทศสัญญา 1 ซื้อขาย แลกเปลี่ยน ให้ เช่าทรัพย์ เช่าซื้อ)
- law-civ-07 (กฎหมายลักษณะเอกเทศสัญญา 2 ยืม ฝากทรัพย์ เก็บของในคลังสินค้า ตัวแทน นายหน้า)
- law-civ-08 (กฎหมายลักษณะเอกเทศสัญญา 3 ประกันภัย รับขน ค้ำประกัน จำนอง จำนำ)
- law-civ-09 (กฎหมายลักษณะตั๋วเงินและบัญชีเดินสะพัด - Negotiable Instruments)
- law-civ-10 (กฎหมายลักษณะหุ้นส่วนและบริษัท - Business Organizations / Partnerships and Companies)
- law-civ-11 (กฎหมายลักษณะครอบครัว - Family Law)
- law-civ-12 (กฎหมายลักษณะมรดก - Succession Law)
- law-civ-13 (หลักเกณฑ์การทำสัญญาและเอกสารทางกฎหมาย - Legal Document Preparation)

[3. หมวดกฎหมายอาญาและนิติวิทยาศาสตร์ (Criminal Law & Forensic Science)]
- law-crim-01 (กฎหมายอาญา ภาคทั่วไป - Criminal Law: General Principles)
- law-crim-02 (กฎหมายอาญา ภาคความผิด - Criminal Law: Specific Offenses)
- law-crim-03 (กฎหมายอาญา ภาคลหุโทษ - Petty Offenses)
- law-crim-04 (กฎหมายเกี่ยวกับกระบวนการยุติธรรมเด็กและเยาวชน - Juvenile Justice Law)
- law-crim-05 (อาชญาวิทยาและทัณฑวิทยา - Criminology and Penology)
- law-crim-06 (นิติวิทยาศาสตร์และนิติเวชศาสตร์ - Forensic Science and Medicine)
- law-crim-07 (กฎหมายเกี่ยวกับยาเสพติด - Narcotics Law)

[4. หมวดกฎหมายมหาชนและการปกครอง (Public Law)]
- law-pub-01 (หลักกฎหมายมหาชนเบื้องต้น - Principles of Public Law)
- law-pub-02 (กฎหมายรัฐธรรมนูญและสถาบันการเมือง - Constitutional Law)
- law-pub-03 (กฎหมายปกครอง - Administrative Law)
- law-pub-04 (วิธีพิจารณาคดีปกครอง - Administrative Procedure)
- law-pub-05 (กฎหมายการคลังและภาษีอากร - Public Finance and Taxation)
- law-pub-06 (กฎหมายเกี่ยวกับการเลือกตั้ง - Election Law)
- law-pub-07 (กฎหมายปกครองส่วนท้องถิ่น - Local Administrative Law)
- law-pub-08 (กฎหมายการผังเมืองและอาคาร - Urban Planning Law)

[5. หมวดกฎหมายวิธีพิจารณาความและพยาน (Procedural Law)]
- law-proc-01 (พระธรรมนูญศาลยุติธรรม - Law on the Organization of Courts)
- law-proc-02 (กฎหมายวิธีพิจารณาความแพ่ง - Civil Procedure Law)
- law-proc-03 (กฎหมายวิธีพิจารณาความอาญา - Criminal Procedure Law)
- law-proc-04 (กฎหมายลักษณะพยานหลักฐาน - Law of Evidence)
- law-proc-05 (กฎหมายล้มละลายและการฟื้นฟูกิจการ - Bankruptcy and Rehabilitation)
- law-proc-06 (การว่าความและศาลจำลอง - Advocacy and Moot Court)
- law-proc-07 (การระงับข้อพิพาททางเลือก - Alternative Dispute Resolution - ADR)
- law-proc-08 (การบังคับคดีแพ่งและอาญา - Legal Execution)

[6. หมวดกฎหมายระหว่างประเทศ (International Law)]
- law-int-01 (กฎหมายระหว่างประเทศแผนกคดีเมือง - Public International Law)
- law-int-02 (กฎหมายระหว่างประเทศแผนกคดีบุคคลและคดีอาญา - Private International Law)
- law-int-03 (กฎหมายองค์การระหว่างประเทศ - International Organizations)
- law-int-04 (กฎหมายว่าด้วยทะเล - Law of the Sea)
- law-int-05 (กฎหมายอาเซียน - ASEAN Law)
- law-int-06 (กฎหมายการค้าระหว่างประเทศ - International Trade Law)
- law-int-07 (กฎหมายสิทธิมนุษยชน - Human Rights Law)

[7. หมวดกฎหมายเฉพาะทางและสมัยใหม่ (Specialized & Modern Law)]
- law-spec-01 (กฎหมายแรงงานและการประกันสังคม - Labour and Social Security Law)
- law-spec-02 (กฎหมายทรัพย์สินทางปัญญา - Intellectual Property Law)
- law-spec-03 (กฎหมายเศรษฐกิจและการค้าระหว่างประเทศ - Economic Law)
- law-spec-04 (กฎหมายการธนาคารและสถาบันการเงิน - Banking and Financial Institutions Law)
- law-spec-05 (กฎหมายคุ้มครองผู้บริโภค - Consumer Protection Law)
- law-spec-06 (กฎหมายสิ่งแวดล้อม - Environmental Law)
- law-spec-07 (กฎหมายเทคโนโลยีสารสนเทศ / กฎหมายไซเบอร์ - IT / Cyber Law)
- law-spec-08 (กฎหมายคุ้มครองข้อมูลส่วนบุคคล - Privacy / PDPA Law)
- law-spec-09 (กฎหมายพลังงาน - Energy Law)
- law-spec-10 (กฎหมายการแพทย์และสาธารณสุข - Medical Law)
- law-spec-11 (กฎหมายบันเทิงและกีฬา - Entertainment and Sports Law)
- law-spec-12 (กฎหมายเกี่ยวกับการขนส่ง - Transport Law)
- law-spec-13 (กฎหมายเกี่ยวกับอสังหาริมทรัพย์ - Real Estate Law)
- law-spec-14 (กฎหมายว่าด้วยการลงทุน - Investment Law)
- law-spec-15 (กฎหมายเกษตรและอุตสาหกรรมเกษตร - Agrarian Law)
- law-spec-16 (กฎหมายทหาร - Military Law)
"""

# (Docstring for clarity)
# classify_doc now returns structured JSON
def classify_doc(text: str, model_name: str) -> dict:
    system_prompt = f"""
หน้าที่ของคุณคือ "นักจัดหมวดหมู่เอกสารกฎหมาย"
กรุณาอ่านเนื้อหา และตัดสินใจ 2 เรื่อง:
1. "รหัสวิชา": เลือกจากรายชื่อที่กำหนดให้
2. "ประเภทเอกสาร" (doc_type): เลือกจาก 3 ประเภทนี้เท่านั้น:
   - "content": เนื้อหาบทเรียน, คำอธิบาย, หนังสือ, บทความสรุป
   - "exam": ข้อสอบเก่า, คำถาม-คำตอบ, ธงคำตอบ, โจทย์ทดสอบ
   - "articles": รายชื่อมาตราเพียวๆ, ตัวบทกฎหมายล้วนๆ

ตอบกลับเป็น JSON Format เท่านั้น:
{{
  "subject_id": "รหัสวิชา",
  "doc_type": "content|exam|articles"
}}

รายชื่อวิชา:
{SUBJECT_LIST}

หากหาไม่ได้ให้ตอบ "Unknown" ในฟิลด์นั้นๆ
"""
    prompt = f"เนื้อหาบางส่วน:\n---\n{text[:2000]}\n---\n\nวิเคราะห์และตอบเป็น JSON:"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1}
    }
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        response.raise_for_status()
        result = response.json().get('response', '{}')
        return json.loads(result)
    except Exception as e:
        print(f"Error accessing Ollama: {e}")
        return {"subject_id": "ERROR", "doc_type": "ERROR"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="gemma:2b", help="Ollama Model")
    args = parser.parse_args()

    files = glob.glob(os.path.join(DIR_IN, "*.txt"))
    if not files:
        print("💡 นำไฟล์ข้อความดิบที่อยากตรวจ (.txt) ไปวางไว้ใน data/01_raw_text นะครับ")
        return

    print("🤖 กำลังเริ่มกระบวนการจัดหมวดหมู่และคัดแยกประเภทเอกสาร...")
    for file_path in files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"กำลังวิเคราะห์ไฟล์: {filename}")
        classification = classify_doc(content, args.model)
        
        subject_id = sanitize_name(classification.get("subject_id", "Unknown"))
        doc_type = classification.get("doc_type", "content")
        
        if "law-" in subject_id or "LAW-" in subject_id.upper():
            # เลือกโฟลเดอร์ปลายทางตามประเภทเอกสาร
            if doc_type == "exam":
                target_root = DIR_OUT_EXAM
            elif doc_type == "articles":
                target_root = DIR_OUT_ARTICLES
            else:
                target_root = DIR_OUT_CONTENT
            
            target_dir = os.path.join(target_root, subject_id)
            os.makedirs(target_dir, exist_ok=True)
            
            # ย้ายไฟล์
            shutil.move(file_path, os.path.join(target_dir, filename))
            print(f"✅ ย้ายเข้าหมวดหมู่: {subject_id} | ประเภท: {doc_type} -> {target_dir}")
        else:
            print(f"❌ จัดหมวดหมู่ไม่ได้ (AI: {subject_id}) - ข้ามไฟล์นี้")

if __name__ == "__main__":
    main()

