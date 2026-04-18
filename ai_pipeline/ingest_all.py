import os
import json
import glob
import re

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

# Initialize databases. If they don't exist, we start with empty structures.
# (To preserve the exact mock data would require complex parsing, so we assume fresh start or pre-existing DB).
# We will create a fresh structure.
chapters_db = load_or_init_db(DB_CHAPTERS_FILE, {})
articles_db = load_or_init_db(DB_ARTICLES_FILE, [])

def process_chapters():
    print("📚 Processing new Chapters...")
    chapter_files = glob.glob(os.path.join(READY_DIR, "chapters", "*", "*.json"))
    
    for file_path in chapter_files:
        subject_id = os.path.basename(os.path.dirname(file_path))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
                
            # Formatting to our Chapter Schema
            if subject_id not in chapters_db:
                # Need subject metadata, we'll create a placeholder if it doesn't exist
                chapters_db[subject_id] = {
                    "subject": {
                        "id": subject_id,
                        "code": subject_id.upper(),
                        "name_th": f"วิชา {subject_id}",
                        "name_en": f"Subject {subject_id}",
                        "category": "กฎหมาย",
                        "source": "สร้างจากเนื้อหา AI"
                    },
                    "chapters": []
                }
                
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
                new_data = json.load(f)
                
            articles_list = new_data.get("articles", [])
            for art in articles_list:
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


if __name__ == "__main__":
    process_chapters()
    process_articles()
    
    # Save the master DBs
    save_db(DB_CHAPTERS_FILE, chapters_db)
    save_db(DB_ARTICLES_FILE, articles_db)
    print("💾 Master databases updated.")
    
    # Export to Web
    build_web_files()
    
    print("🎉 Ingestion Complete! Your website is now up to date.")
