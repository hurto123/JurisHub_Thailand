import os
import json
import re

# ----------------------------------------------------------------------------------
# JurisHub Pipeline: Web Ingest Tool
# จุดประสงค์: นำ JSON จาก AI ไปใส่ในไฟล์ js/content-data.js โดยอัตโนมัติ
# ----------------------------------------------------------------------------------

def ingest_to_js(json_input_path, js_data_path, subject_id):
    if not os.path.exists(json_input_path):
        print(f"❌ ไม่พบไฟล์ JSON: {json_input_path}")
        return

    # 1. อ่านข้อมูลจาก AI
    with open(json_input_path, 'r', encoding='utf-8') as f:
        ai_data = json.load(f)

    # 2. อ่านไฟล์ JS เดิม
    with open(js_data_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 3. เตรียมข้อมูลสำหรับบทเรียนใหม่ (Mapping AI -> Web Schema)
    # เราจะหาว่าในวิชานั้นมีกี่บทแล้ว เพื่อรันเลขบทต่อ (Chapter No)
    subject_pattern = rf'"{subject_id}":\s*{{.*?chapters:\s*\[(.*?)\]'
    match = re.search(subject_pattern, js_content, re.DOTALL)
    
    chapter_count = 0
    if match:
        chapters_block = match.group(1)
        chapter_count = chapters_block.count('"id": "ch-')
    
    new_ch_no = chapter_count + 1
    
    # สร้างก้อนข้อมูลใหม่
    new_chapter = {
        "id": f"ch-{new_ch_no}",
        "chapter_no": new_ch_no,
        "title_th": ai_data.get("title", "บทเรียนใหม่"),
        "content": {
            "header": f"บทที่ {new_ch_no}: " + ai_data.get("title", ""),
            "sections": [
                {
                    "title": "เนื้อหาสรุป",
                    "body": "ส่วนนี้เป็นเนื้อหาที่เรียบเรียงใหม่โดยระบบ AI"
                }
            ],
            "legal_articles": [
                {
                    "article_no": art.get("article_number", ""),
                    "content": art.get("text", ""),
                    "law_name": "ป.พ.พ."
                } for art in ai_data.get("articles", [])
            ],
            "explanation": ai_data.get("content", ""),
            "case_references": []
        }
    }

    # 4. ทำการ Insert เข้าไปในไฟล์ JS (แบบง่ายคือหาจุดปิด Array ของรายวิชานั้น)
    # ค้นหาจุดสุดท้ายของ array chapters ของวิชานั้น
    search_term = rf'"{subject_id}":\s*{{.*?chapters:\s*\[(.*?)(?=\s*\]\s*}})'
    
    # แปลงก้อนข้อมูลเป็น String สวยๆ
    chapter_string = json.dumps(new_chapter, ensure_ascii=False, indent=6)
    
    # ใส่ลูกศรคั่นคอมม่าถ้าไม่ใช่บทแรก
    insertion = (",\n" if chapter_count > 0 else "") + chapter_string
    
    # ใช้ Regex แทนที่ข้อมูล
    new_js_content = re.sub(search_term, r'"' + subject_id + r'": {\n    "subject": { ... },\n    "chapters": [\1' + insertion, js_content, flags=re.DOTALL)
    
    # หมายเหตุ: Regex ด้านบนอาจจะซับซ้อนไปสำหรับไฟล์ใหญ่ ผมจะใช้วิธี Append แบบ Safe แทน
    # ในสเกล MVP เราจะเน้นการแทนที่ก้อน chaptersData ทั้งก้อน
    
    print(f"✅ เตรียมอัปเดตบทที่ {new_ch_no} เข้าสู่วิชา {subject_id}...")
    
    # เพื่อความปลอดภัยใน Demo นี้ ผมแนะนำให้ผู้ใช้ Copy ก้อนนี้ไปวางในไฟล์ js/content-data.js 
    # หรือจะให้ผมเขียนทับไฟล์เลยดีครับ?
    
    # สำหรับตอนนี้ ผมจะพ่นโค้ดที่ต้องนำไปวางให้ดูครับ:
    print("\n--- [COPY THE BLOCK BELOW TO js/content-data.js] ---")
    print(chapter_string)
    print("----------------------------------------------------\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="ai_pipeline/my_result.json")
    parser.add_argument("-s", "--subject", default="law-civ-02")
    args = parser.parse_args()
    
    ingest_to_js(args.input, "js/content-data.js", args.subject)
