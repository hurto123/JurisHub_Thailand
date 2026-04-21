import os
import json
import requests
import argparse
import glob

# -------------------------------------------------------------------------
# Step 2: The Rewriter (นักสรุปเนื้อหาเลี่ยงลิขสิทธิ์)
# อ่านไฟล์จาก 02_classified มาทำการ Paraphrase ให้ออกมาเป็นโครงสร้าง Web (chapter content)
# -------------------------------------------------------------------------

DATA_DIR = "data"
DIR_IN = os.path.join(DATA_DIR, "02_classified")
DIR_OUT = os.path.join(DATA_DIR, "03_ready_to_web", "chapters")

os.makedirs(DIR_OUT, exist_ok=True)

def rewrite_content(text: str, model_name: str) -> str:
    system_prompt = """
คุณคืออาจารย์นิติศาสตร์ผู้เชี่ยวชาญ อ่านเนื้อหาที่มีลิขสิทธิ์นี้ และทำการเรียบเรียงอธิบายใหม่ทั้งหมดด้วยภาษาที่เข้าใจง่าย ยกเว้น "ตัวบทมาตรา" ให้คงไว้เหมือนเดิม 100%
ต้องตอบกลับเป็น Valid JSON Format ตามนี้เท่านั้น:
{
  "title": "หัวข้อหลักของเนื้อหานี้ (เช่น ความหมายของประมาท)",
  "content": "เนื้อหาที่เรียบเรียงอธิบายใหม่ <br> ขั้นบรรทัดได้"
}
ห้ามตอบข้อความอื่นๆ ตอบเป็น JSON เท่านั้น
"""
    payload = {
        "model": model_name,
        "prompt": text,
        "system": system_prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.3}
    }
    
    response = requests.post('http://localhost:11434/api/generate', json=payload)
    output = response.json().get('response', '')
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="gemma:2b", help="Ollama Model")
    args = parser.parse_args()

    # ไปไล่อ่านจาก Subdirectory ของรายวิชาที่มี
    for root, dirs, files in os.walk(DIR_IN):
        for file in files:
            if file.endswith(".txt"):
                subject_id = os.path.basename(root) # ชื่อโฟลเดอร์คือ รหัสวิชา
                file_path = os.path.join(root, file)
                
                print(f"✍️ กำลังทำการเรียบเรียงเนื้อหาไฟล์ {file} (วิชา: {subject_id})...")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                result = rewrite_content(content, args.model)
                
                # Setup output path
                # Ex: 03_ready_to_web/chapters/law-civ-02/filename.json
                out_subj_dir = os.path.join(DIR_OUT, subject_id)
                os.makedirs(out_subj_dir, exist_ok=True)
                
                out_file_path = os.path.join(out_subj_dir, file.replace(".txt", ".json"))
                
                with open(out_file_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ บันทึกเนื้อหาเรียบเรียงใหม่ที่ {out_file_path}")

if __name__ == "__main__":
    main()
