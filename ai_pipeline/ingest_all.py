import os
import json
import glob
import re
import shutil

# -------------------------------------------------------------------------
# Step 4: Web Ingestor (ผู้นำเข้าข้อมูลสู่อินเทอร์เน็ต)
# ดึงข้อมูลจาก 03_ready_to_web เก็บเข้าฐานข้อมูลกลาง แล้วอัปเดตไฟล์เว็บ .js
# -------------------------------------------------------------------------

DATA_DIR = "data"
WEB_JS_DIR = "js"
DB_DIR = os.path.join(DATA_DIR, "database")
READY_DIR = os.path.join(DATA_DIR, "03_ready_to_web")
PROCESSED_DIR = os.path.join(READY_DIR, "processed")

# Ensure directories exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.join(PROCESSED_DIR, "chapters"), exist_ok=True)
os.makedirs(os.path.join(PROCESSED_DIR, "articles"), exist_ok=True)

# Database file paths
DB_CHAPTERS_FILE = os.path.join(DB_DIR, "chapters.json")
DB_ARTICLES_FILE = os.path.join(DB_DIR, "articles.json")
DB_EXAMS_FILE = os.path.join(DB_DIR, "exams.json")

def load_or_init_db(filepath, default_data):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Database file {filepath} is corrupted. Re-initializing...")
            return default_data
    return default_data

def save_db(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def extract_js_data_to_json(js_path, var_name):
    """
    Attempts to extract JSON-like data from an existing .js file to migrate mock data.
    """
    if not os.path.exists(js_path): return None
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to find the assignment of the variable
    match = re.search(rf'const\s+{var_name}\s*=\s*([\[{{].*?[\]\}}]);?\s*$', content, re.DOTALL | re.MULTILINE)
    
    if match:
        json_str = match.group(1)
        # Attempt to clean up JS-specific quirks (like unquoted keys) if necessary, 
        # but standard json.loads might fail if the JS is not strict JSON.
        # For our specific mock data, we might need a workaround.
        pass # Too risky for a general regex, we'll initialize with empty if DB doesn't exist,
             # OR we pre-fill the DB manually in Python.

def get_subject_metadata(subject_id):
    """Parses js/data.js to extract subject details."""
    data_js_path = os.path.join(WEB_JS_DIR, "data.js")
    default_meta = {
        "id": subject_id,
        "code": subject_id.upper(),
        "name_th": f"วิชา {subject_id}",
        "name_en": f"Subject {subject_id}",
        "category": "กฎหมาย",
        "source": "สร้างจากเนื้อหา AI"
    }
    if not os.path.exists(data_js_path): return default_meta
    
    with open(data_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find subjectsData array
    match = re.search(r'const\s+subjectsData\s*=\s*(\[.*?\]);', content, re.DOTALL)
    if not match: return default_meta
    
    array_str = match.group(1)
    
    # Because it is JS, we can just regex the specific item
    # Quick regex to extract details for the subject id
    item_match = re.search(rf'{{\s*id:\s*"{subject_id}".*?code:\s*"([^"]+)".*?name_th:\s*"([^"]+)".*?name_en:\s*"([^"]+)".*?category:\s*"([^"]+)"', array_str, re.DOTALL | re.IGNORECASE)
    
    if item_match:
        return {
            "id": subject_id,
            "code": item_match.group(1),
            "name_th": item_match.group(2),
            "name_en": item_match.group(3),
            "category": item_match.group(4),
            "source": ""
        }
    return default_meta

def clean_json_str(raw_str):
    """Extracts valid JSON from LLM output by finding the first { or [ and last } or ]."""
    raw_str = raw_str.strip()
    # Find first { or [
    start_obj = raw_str.find('{')
    start_arr = raw_str.find('[')
    
    if start_obj == -1 and start_arr == -1:
        raise ValueError("No JSON object or array found in text")
    
    start_idx = start_obj if (start_arr == -1 or (start_obj != -1 and start_obj < start_arr)) else start_arr
    end_char = '}' if start_idx == start_obj else ']'
    
    end_idx = raw_str.rfind(end_char)
    if end_idx == -1:
        raise ValueError("Unterminated JSON object or array")
        
    json_str = raw_str[start_idx:end_idx+1]
    return json.loads(json_str)

# Initialize databases. If they don't exist, we start with empty structures.
# (To preserve the exact mock data would require complex parsing, so we assume fresh start or pre-existing DB).
# We will create a fresh structure.
chapters_db = load_or_init_db(DB_CHAPTERS_FILE, {})
articles_db = load_or_init_db(DB_ARTICLES_FILE, [])
exams_db = load_or_init_db(DB_EXAMS_FILE, [])

def process_chapters():
    print("📚 Processing new Chapters...")
    chapter_files = glob.glob(os.path.join(READY_DIR, "chapters", "*", "*.json"))
    
    for file_path in chapter_files:
        subject_id = os.path.basename(os.path.dirname(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                new_data = clean_json_str(raw_content)
                
            # Formatting to our Chapter Schema
            if subject_id not in chapters_db:
                chapters_db[subject_id] = {
                    "subject": get_subject_metadata(subject_id),
                    "chapters": []
                }
                
            # Duplicate check based on title
            new_title = new_data.get("title", "")
            exists = any(ch["title_th"] == new_title for ch in chapters_db[subject_id]["chapters"])
            
            if exists:
                print(f"  ⏭️ Skipped Duplicate Chapter '{new_title}' in {subject_id}")
            else:
                chapter_count = len(chapters_db[subject_id]["chapters"])
                new_ch_no = chapter_count + 1
                
                # Map raw AI output to our Viewer Schema
                new_chapter = {
                    "id": f"ch-{new_ch_no}",
                    "chapter_no": new_ch_no,
                    "title_th": new_data.get("title", f"บทที่ {new_ch_no}"),
                    "content": {
                        "header": f"บทที่ {new_ch_no}: {new_data.get('title', '')}",
                        "sections": [
                            {
                                "title": "เนื้อหาสรุป",
                                "body": new_data.get("content", "ไม่มีเนื้อหา")
                            }
                        ],
                        "legal_articles": [],
                        "explanation": "",
                        "case_references": []
                    }
                }
                
                chapters_db[subject_id]["chapters"].append(new_chapter)
                print(f"  ✅ Added Chapter {new_ch_no} to {subject_id}")

            
            # Move to processed
            dest_dir = os.path.join(PROCESSED_DIR, "chapters", subject_id)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
            
        except Exception as e:
            print(f"  ❌ Failed to process {file_path}: {e}")

def process_articles():
    print("⚖️ Processing new Articles...")
    article_files = glob.glob(os.path.join(READY_DIR, "articles", "*", "*.json"))
    
    for file_path in article_files:
        subject_id = os.path.basename(os.path.dirname(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                new_data = clean_json_str(raw_content)
                
            articles_list = new_data.get("articles", [])
            for art in articles_list:
                article_no = art.get("article_no", "")
                
                # Check for duplicates
                exists = any(a["article_no"] == article_no and a["related_subject_id"] == subject_id for a in articles_db)
                if exists:
                    print(f"  ⏭️ Skipped Duplicate Article '{article_no}' in {subject_id}")
                    continue
                    
                # Add unique ID
                art["id"] = f"art-{subject_id}-{len(articles_db)+1}"
                art["related_subject_id"] = subject_id
                if "tags" not in art:
                    art["tags"] = ["AI_Extracted"]
                    
                articles_db.append(art)
                print(f"  ✅ Added Article {art.get('article_no')} from {subject_id}")
            
            # Move to processed
            dest_dir = os.path.join(PROCESSED_DIR, "articles", subject_id)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
            
        except Exception as e:
            print(f"  ❌ Failed to process {file_path}: {e}")

def process_exams():
    print("📋 Processing new Exams...")
    READY_EXAM_DIR = os.path.join(DATA_DIR, "05_exam_ready")
    os.makedirs(READY_EXAM_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROCESSED_DIR, "exams"), exist_ok=True)
    
    exam_files = glob.glob(os.path.join(READY_EXAM_DIR, "*", "*_exam.json"))
    
    for file_path in exam_files:
        subject_id = os.path.basename(os.path.dirname(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                new_data = clean_json_str(raw_content)
                
            # If the exam has no questions, ignore
            if not new_data.get("questions"):
                print(f"  ⏭️ Skipped Empty Exam for {subject_id}")
                dest_dir = os.path.join(PROCESSED_DIR, "exams", subject_id)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
                continue

            # Fill in subject names if missing
            meta = get_subject_metadata(subject_id)
            if "subject_name" not in new_data:
                new_data["subject_name"] = meta["name_th"]
            if "subject_code" not in new_data:
                new_data["subject_code"] = meta["code"]
            if "university" not in new_data or not new_data.get("university"):
                new_data["university"] = "ไม่ระบุมหาวิทยาลัย"
                
            # Basic validation
            for q in new_data.get("questions", []):
                if "points" not in q or not str(q["points"]).isdigit():
                    q["points"] = 10
            
            # Simple duplicate check by year and semester for the same subject
            exists = any(
                e.get("subject_id") == subject_id and 
                e.get("year") == new_data.get("year") and 
                e.get("semester") == new_data.get("semester") and
                e.get("exam_type") == new_data.get("exam_type")
                for e in exams_db
            )
            
            if exists:
                print(f"  ⏭️ Skipped Duplicate Exam {new_data.get('year')}/{new_data.get('semester')} in {subject_id}")
            else:
                exams_db.append(new_data)
                print(f"  ✅ Added Exam {new_data.get('year')}/{new_data.get('semester')} to {subject_id}")
            
            # Move to processed
            dest_dir = os.path.join(PROCESSED_DIR, "exams", subject_id)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
            
        except Exception as e:
            print(f"  ❌ Failed to process exam {file_path}: {e}")

def build_web_files():
    print("🌐 Building Web Data Files...")
    
    # Write content-data.js
    content_js_path = os.path.join(WEB_JS_DIR, "content-data.js")
    with open(content_js_path, 'w', encoding='utf-8') as f:
        f.write("/**\n * Auto-generated by JurisHub Ingestor Pipeline\n */\n")
        f.write("const chaptersData = ")
        f.write(json.dumps(chapters_db, ensure_ascii=False, indent=2))
        f.write(";\n")
    print(f"  ✅ Built {content_js_path}")
        
    # Write articles-data.js
    articles_js_path = os.path.join(WEB_JS_DIR, "articles-data.js")
    with open(articles_js_path, 'w', encoding='utf-8') as f:
        f.write("/**\n * Auto-generated by JurisHub Ingestor Pipeline\n */\n")
        f.write("const articlesData = ")
        f.write(json.dumps(articles_db, ensure_ascii=False, indent=2))
        f.write(";\n\n")
        
        # Adding codeTypes static config
        f.write("""const codeTypes = [
    { id: "all", name: "ทั้งหมด" },
    { id: "ป.พ.พ.", name: "ประมวลกฎหมายแพ่งและพาณิชย์" },
    { id: "ป.อ.", name: "ประมวลกฎหมายอาญา" },
    { id: "ป.วิ.พ.", name: "ประมวลกฎหมายวิธีพิจารณาความแพ่ง" },
    { id: "ป.วิ.อ.", name: "ประมวลกฎหมายวิธีพิจารณาความอาญา" },
    { id: "รัฐธรรมนูญฯ", name: "รัฐธรรมนูญแห่งราชอาณาจักรไทย" },
    { id: "พ.ร.บ.", name: "พระราชบัญญัติอื่นๆ" }
];""")
    print(f"  ✅ Built {articles_js_path}")

    # Write exams-data.js
    exams_js_path = os.path.join(WEB_JS_DIR, "exams-data.js")
    with open(exams_js_path, 'w', encoding='utf-8') as f:
        f.write("/**\n * Auto-generated by JurisHub Ingestor Pipeline\n */\n")
        f.write("const examsData = ")
        f.write(json.dumps(exams_db, ensure_ascii=False, indent=2))
        f.write(";\n")
    print(f"  ✅ Built {exams_js_path}")


if __name__ == "__main__":
    process_chapters()
    process_articles()
    process_exams()
    
    # Save the master DBs
    save_db(DB_CHAPTERS_FILE, chapters_db)
    save_db(DB_ARTICLES_FILE, articles_db)
    save_db(DB_EXAMS_FILE, exams_db)
    print("💾 Master databases updated.")
    
    # Export to Web
    build_web_files()
    
    print("🎉 Ingestion Complete! Your website is now up to date.")
