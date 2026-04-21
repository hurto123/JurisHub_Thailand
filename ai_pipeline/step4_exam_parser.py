import os
import json
import requests
import argparse

# -------------------------------------------------------------------------
# Step 4: The Exam Parser (ตัวดึงข้อสอบและธงคำตอบ)
# อ่านเนื้อหาจากรายวิชา เพื่อสกัดโจทย์และธงคำตอบออกมาเป็น JSON สำหรับเว็บ
# -------------------------------------------------------------------------

DATA_DIR = "data"
DIR_IN = os.path.join(DATA_DIR, "04_exam_raw")
DIR_OUT = os.path.join(DATA_DIR, "05_exam_ready")

os.makedirs(DIR_IN, exist_ok=True)
os.makedirs(DIR_OUT, exist_ok=True)

def parse_exam_content(text: str, subject_id: str, model_name: str) -> str:
    system_prompt = f"""
คุณจะได้รับข้อความเกี่ยวกับข้อสอบเก่าของวิชากฎหมาย (รหัสวิชา {subject_id})
หน้าที่ของคุณคือ "แยกแยะข้อสอบและธงคำตอบ" (คำเฉลย) ออกมาให้เป็นรูปแบบ JSON ที่กำหนด

ถ้าในเอกสารมีข้อสอบ ให้คุณแยกแต่ละข้อออกจากกัน โดยเก็บ "โจทย์" และหา "ธงคำตอบ" (ถ้ามี) จับคู่กัน
ถ้าไม่มีข้อสอบเลย ให้ตอบโครงสร้าง JSON ว่างๆ

ต้องตอบกลับเป็น Valid JSON Format เท่านั้น รูปแบบที่ต้องใช้:
{{
  "subject_id": "{subject_id}",
  "exam_type": "ถ้าเป็นข้อสอบกลางภาค ให้พิมว่า midterm ถ้าปลายภาคให้พิมพ์ว่า final ถ้าระบุไม่ได้ให้เดาจากบริบท",
  "year": "ปีการศึกษา ถ้ามี เช่น 2565",
  "semester": "ภาคการศึกษา เช่น 1 หรือ 2",
  "questions": [
    {{
      "number": 1,
      "points": คะแนนเต็มของข้อนี้ (เป็นตัวเลข เช่น 20, ถ้าไม่ระบุให้เดาว่าเป็น 20),
      "text": "โจทย์ข้อสอบทั้งหมดแบบเป๊ะๆ",
      "answer": "ธงคำตอบ (เฉลย) แบบเป๊ะๆ หรือจัดบรรทัดให้อ่านง่าย ถ้าไม่มีให้เขียนว่า ไม่มีธงคำตอบ"
    }}
  ]
}}
ห้ามตอบข้อความอื่นๆ ก่อนและหลัง ห้ามครอบด้วย ```json ตอบเป็นดิบๆ JSON เท่านั้น
"""
    payload = {
        "model": model_name,
        "prompt": text,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1}
    }
    
    response = requests.post('http://localhost:11434/api/generate', json=payload)
    return response.json().get('response', '')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="gemma:2b", help="Ollama Model")
    args = parser.parse_args()

    for root, dirs, files in os.walk(DIR_IN):
        for file in files:
            if file.endswith(".txt"):
                subject_id = os.path.basename(root)
                file_path = os.path.join(root, file)
                
                print(f"📝 กำลังวิเคราะห์และสกัดข้อสอบจากไฟล์ {file} (วิชา: {subject_id})...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                result = parse_exam_content(content, subject_id, args.model)
                
                out_subj_dir = os.path.join(DIR_OUT, subject_id)
                os.makedirs(out_subj_dir, exist_ok=True)
                
                out_file_path = os.path.join(out_subj_dir, file.replace(".txt", "_exam.json"))
                
                with open(out_file_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ บันทึกโครงสร้างข้อสอบที่สกัดได้ไว้ที่ {out_file_path}")

if __name__ == "__main__":
    main()
