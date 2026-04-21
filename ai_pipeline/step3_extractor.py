import os
import json
import requests
import argparse

# -------------------------------------------------------------------------
# Step 3: The Article Extractor (นักสกัดและสรุปมาตรา)
# อ่านเนื้อหาจาก 02_classified ตามหาตัวบทและสั่งรวบรัดใจความ เพื่อส่งไปคลังมาตรา
# -------------------------------------------------------------------------

DATA_DIR = "data"
DIR_IN_CONTENT = os.path.join(DATA_DIR, "02_classified")
DIR_IN_ARTICLES = os.path.join(DATA_DIR, "01_articles_raw")
DIR_OUT = os.path.join(DATA_DIR, "03_ready_to_web", "articles")

os.makedirs(DIR_OUT, exist_ok=True)
os.makedirs(DIR_IN_ARTICLES, exist_ok=True)

def extract_and_summarize_articles(text: str, subject_id: str, model_name: str) -> str:
    system_prompt = f"""
คุณจะได้รับข้อความเกี่ยวกับกฎหมาย หน้าที่ของคุณคือมองหาว่ามีการพูดถึง "มาตรา" อะไรหรือไม่
ถ้ามี ให้ดึงตัวบทมาตราดั้งเดิมออกมา และ "สรุปเฉพาะมาตรานั้นแบบสั้นๆ ด้วยภาษาที่เข้าใจง่ายที่สุด (ภาษาชาวบ้าน) เสมือนกำลังอธิบายให้คนทั่วไปฟัง ไม่เกิน 2-3 บรรทัด"
ถ้าไม่มีมาตราเลยในเนื้อหา ให้ตอบแค่ {{ "articles": [] }}

ต้องตอบกลับเป็น Valid JSON Format เท่านั้น รูปแบบ:
{{
  "articles": [
    {{
      "code_type": "ถ้าแยกได้ให้ใส่ เช่น ป.พ.พ. หรือ ป.อ. (ถ้าไม่รู้ให้เดาจากรหัสวิชา {subject_id} เช่น ถ้าวิชา law-civ ให้ตอบ ป.พ.พ., ถ้า law-crim ให้ตอบ ป.อ.)",
      "article_no": "เลขมาตรา เช่น มาตรา 149",
      "original_text": "ตัวบทแบบเป๊ะๆ ดั้งเดิม",
      "summary_by_ai": "สรุปใจความของมาตรานี้ด้วยภาษาชาวบ้าน เข้าใจง่ายที่สุด 1-2 บรรทัด",
      "related_subject_id": "{subject_id}"
    }}
  ]
}}
ห้ามตอบข้อความอื่นๆ ตอบเป็น JSON เท่านั้น
"""
    payload = {
        "model": model_name,
        "prompt": text,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2}
    }
    
    response = requests.post('http://localhost:11434/api/generate', json=payload)
    return response.json().get('response', '')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="gemma:2b", help="Ollama Model")
    args = parser.parse_args()

    # Scan both folders: Content (embedded) and Articles Raw (standalone)
    input_dirs = [DIR_IN_CONTENT, DIR_IN_ARTICLES]
    
    for input_dir in input_dirs:
        if not os.path.exists(input_dir): continue
        print(f"📂 Scanning directory: {input_dir}")
        
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".txt"):
                    subject_id = os.path.basename(root)
                    file_path = os.path.join(root, file)
                    
                    print(f"🔍 สแกนหามาตราในไฟล์ {file} (วิชา: {subject_id})...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    result = extract_and_summarize_articles(content, subject_id, args.model)
                    
                    out_subj_dir = os.path.join(DIR_OUT, subject_id)
                    os.makedirs(out_subj_dir, exist_ok=True)
                    
                    # Prevent filename collisions between different input folders
                    prefix = "raw_" if input_dir == DIR_IN_ARTICLES else ""
                    out_file_path = os.path.join(out_subj_dir, prefix + file.replace(".txt", "_articles.json"))
                    
                    with open(out_file_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"✅ บันทึกข้อมูลคลังมาตราสกัดใหม่ที่ {out_file_path}")

if __name__ == "__main__":
    main()

