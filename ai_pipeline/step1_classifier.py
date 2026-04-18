import os
import json
import requests
import argparse
import shutil
import glob

# -------------------------------------------------------------------------
# Step 1: AI Classifier (นักคัดแยกวิชา)
# อ่านไฟล์ Text ที่ได้มาจาก OCR/PDF แล้วส่งให้ Ollama ทายว่าเป็นวิชาอะไร
# -------------------------------------------------------------------------

DATA_DIR = "data"
DIR_IN = os.path.join(DATA_DIR, "01_raw_text")
DIR_OUT = os.path.join(DATA_DIR, "02_classified")

# สร้างโฟลเดอร์ให้พร้อม
for d in [DIR_IN, DIR_OUT]:
    os.makedirs(d, exist_ok=True)

# List วิชาที่มีเพื่อบอกให้ LLM ทายกรอบนี้
SUBJECT_LIST = """
- law-civ-02 (กฎหมายลักษณะนิติกรรมและสัญญา)
- law-civ-03 (กฎหมายลักษณะหนี้)
- law-civ-08 (กฎหมายลักษณะครอบครัว)
- law-crim-01 (กฎหมายอาญา ภาคทั่วไป)
- law-crim-02 (กฎหมายอาญา ภาคความผิด)
- law-pub-02 (กฎหมายรัฐธรรมนูญ)
- law-pub-03 (กฎหมายปกครอง)
- law-proc-01 (วิชาพิจารณาความแพ่ง)
- law-proc-02 (วิชาพิจารณาความอาญา)
"""

def classify_text(text: str, model_name: str) -> str:
    system_prompt = f"""
หน้าที่ของคุณคือ "นักจัดหมวดหมู่วิชากฎหมาย"
กรุณาอ่านเนื้อหา และตัดสินใจว่าเนื้อหานี้ควรจัดอยู่ในวิชาใด จากรายชื่อที่กำหนดให้:

{SUBJECT_LIST}

ตอบกลับมาเฉพาะ "รหัสวิชา" (เช่น law-civ-02) ห้ามตอบอย่างอื่นเด็ดขาด
หากหาไม่ได้ให้ตอบ "Unknown"
"""
    prompt = f"เนื้อหาบางส่วน:\n---\n{text[:1500]}\n---\n\nรหัสวิชาคือ:"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        response.raise_for_status()
        result = response.json().get('response', '').strip()
        return result
    except Exception as e:
        print(f"Error accessing Ollama: {e}")
        return "ERROR"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="gemma:2b", help="Ollama Model")
    args = parser.parse_args()

    files = glob.glob(os.path.join(DIR_IN, "*.txt"))
    if not files:
        print("💡 นำไฟล์ข้อความดิบที่อยากตรวจ (.txt) ไปวางไว้ใน data/01_raw_text นะครับ")
        return

    print("🤖 กำลังเริ่มกระบวนการจัดหมวดหมู่...")
    for file_path in files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"กำลังวิเคราะห์ไฟล์: {filename}")
        subject_id = classify_text(content, args.model)
        
        if "law-" in subject_id:
            # สร้างที่อยู่ใหม่ตามวิชา
            target_dir = os.path.join(DIR_OUT, subject_id)
            os.makedirs(target_dir, exist_ok=True)
            
            # ย้ายไฟล์
            shutil.move(file_path, os.path.join(target_dir, filename))
            print(f"✅ ย้ายเข้าหมวดหมู่: {target_dir}")
        else:
            print(f"❌ จัดหมวดหมู่ไม่ได้ (ผลจาก AI: {subject_id}) - ข้ามไฟล์นี้")

if __name__ == "__main__":
    main()
