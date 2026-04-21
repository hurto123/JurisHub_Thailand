import os
import json
import glob
import shutil

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_DIR = os.path.join(DATA_DIR, "database")
JS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "js"))

CONTENT_JS_PATH = os.path.join(JS_DIR, "content-data.js")

def update_viewer():
    print("🌐 Checking for newly generated JSON files to update Web Viewer...")
    
    if not os.path.exists(CONTENT_JS_PATH):
        print(f"⚠️ {CONTENT_JS_PATH} not found. Ensure you are running from ai_pipeline/")
        return

    json_files = glob.glob(os.path.join(DB_DIR, "*.json"))
    summary_files = glob.glob(os.path.join(DB_DIR, "summaries", "*.json"))
    
    all_files = json_files + summary_files
    
    if not all_files:
        print("💡 No JSON files found in database/. Skipping web update.")
        return

    # In a real dynamic site, you would just copy the JSONs to a public folder.
    # Since JurisHub uses a static .js mapping (const subjectsData = {}), 
    # we need to inject the newly formed JSONs into content-data.js 
    # Or, preferably, you modify viewer.html to fetch("database/law-civ-04.json")
    
    # As a robust static solution, let's copy the JSON files directly to the js/ folder 
    # so frontend could potentially fetch them.
    for fpath in all_files:
        dest_name = os.path.basename(fpath)
        dest_path = os.path.join(JS_DIR, dest_name)
        shutil.copy2(fpath, dest_path)
        print(f"✅ Copied {dest_name} to {JS_DIR}/ for frontend accessibility.")
        
    print("✅ Web Viewer paths updated! You may need to edit viewer.html to fetch() these directly.")

if __name__ == "__main__":
    update_viewer()
