import os
import json
import glob
import re
from PIL import Image
import pytesseract

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_DIR = os.path.join(DATA_DIR, "database")

TXT_INBOX = os.path.join(DATA_DIR, "01_raw_text")
EXAM_RAW = os.path.join(DATA_DIR, "04_exam_raw")

os.makedirs(DB_DIR, exist_ok=True)

def parse_lesson_txt_to_json(file_path):
    """Parses structural .txt files into Lesson JSON Format."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    filename = os.path.basename(file_path)
    subject_id = filename.replace(".txt", "").replace("สรุป ", "").strip()

    # Create basic structure
    json_data = {
        "id": subject_id.lower().replace(" ", "-"),
        "title": subject_id,
        "chapters": [
            {
                "chapter_no": 1,
                "title": "สรุปเนื้อหา",
                "sections": [
                    {
                        "section_no": 1,
                        "content": content[:1000] + "..." # Truncated for JSON builder logic, summarizer will handle deep texts
                    }
                ]
            }
        ]
    }
    
    out_path = os.path.join(DB_DIR, f"{json_data['id']}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Processed Lesson JSON: {out_path}")


def process_exam_images():
    """Reads 04_exam_raw/, runs Tesseract OCR, outputs to JSON."""
    if not os.path.exists(EXAM_RAW):
        print(f"⚠️ {EXAM_RAW} not found.")
        return

    exam_images = glob.glob(os.path.join(EXAM_RAW, "*.png")) + glob.glob(os.path.join(EXAM_RAW, "*.jpg"))
    for img_path in exam_images:
        filename = os.path.basename(img_path)
        print(f"🔍 Running OCR on Exam Image: {filename} ...")
        
        try:
            # Requires Tesseract installed locally
            text = pytesseract.image_to_string(Image.open(img_path), lang='tha+eng')
            
            # Simple heuristic parsing (Can be enhanced)
            questions = []
            parts = re.split(r'ข้อที่\s*\d+|ข้อ\s*\d+', text)
            for idx, part in enumerate(parts[1:]):
                questions.append({
                    "question_no": idx + 1,
                    "question": part.strip(),
                    "answer": "รอธงคำตอบ"
                })

            exam_json = {
                "exam_file": filename,
                "questions": questions
            }

            base_name = os.path.splitext(filename)[0]
            out_path = os.path.join(DB_DIR, f"exam_{base_name}.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(exam_json, f, ensure_ascii=False, indent=2)
            print(f"✅ Processed Exam JSON: {out_path}")
            
        except Exception as e:
            print(f"❌ Failed to OCR {filename}: {e}")

if __name__ == "__main__":
    print("🚀 Starting JSON Builder...")
    
    # Process TXT files
    if os.path.exists(TXT_INBOX):
        txt_files = glob.glob(os.path.join(TXT_INBOX, "*.txt"))
        for f in txt_files:
            parse_lesson_txt_to_json(f)
            
    # Process Exams
    process_exam_images()
    print("✨ JSON Builder Finished.")
