import os
import json
import time
import requests
import glob
from tqdm import tqdm
import update_viewer # Import logic to update web live

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
TXT_INBOX = os.path.join(DATA_DIR, "01_raw_text")
OUT_DIR = os.path.join(DATA_DIR, "database", "summaries")
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:1.5b" 

os.makedirs(OUT_DIR, exist_ok=True)

def check_ollama_health():
    """Health Check for Ollama Process."""
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=5)
        if res.status_code == 200:
            print("✅ Ollama is running.")
            return True
    except requests.ConnectionError:
        pass
    print("❌ Error: Ollama is NOT running.")
    return False

def summarize_with_ollama(text_chunk):
    """Sends a chunk to DeepSeek to get a detailed long summary."""
    system_prompt = (
        "คุณคือผู้เชี่ยวชาญด้านกฎหมายไทย หน้าที่ของคุณคือสรุปเนื้อหากฎหมายต่อไปนี้อย่างละเอียด "
        "ครอบคลุมทุกประเด็นสำคัญ กรุณาอธิบายให้มีความยาวสอดคล้องกับเนื้อหา อย่างน้อย 1 หน้ากระดาษ A4 "
        "หากมีมาตรากฎหมาย ให้คงเลขมาตราไว้และเรียบเรียงให้อ่านเข้าใจง่ายขึ้น"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text_chunk,
        "system": system_prompt,
        "stream": True,
        "options": {
            "temperature": 0.4,
            "num_gpu": 1,         # Force GPU usage
            "num_thread": 4        # Threads for safety
        }
    }
    
    full_response = ""
    print(f"🤖 AI ({OLLAMA_MODEL}) กำลังเตรียมคำตอบ... (ถ้าเงียบนานเกิน 1 นาทีโปรดแจ้งผม)", flush=True)
    
    try:
        # กำหนด timeout สั้นๆ สำหรับการเชื่อมต่อ แต่ปล่อยยาวสำหรับการรอคำตอบ
        response = requests.post(OLLAMA_API, json=payload, stream=True, timeout=(5, 120))
        response.raise_for_status()
        
        print("✍️ เริ่มเขียนเนื้อหา: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    chunk_text = data["response"]
                    full_response += chunk_text
                    # พิมพ์ออกมาทันทีที่ได้รับข้อมูล
                    print(chunk_text, end="", flush=True)
                if data.get("done"):
                    break
        print("\n" + "-"*30)
    except requests.exceptions.Timeout:
        print("\n❌ Error: Ollama ตอบสนองช้าเกินไป (Timeout). อาจเป็นเพราะ GPU ทำงานหนักเกินไป")
    except Exception as e:
        print(f"\n❌ Ollama Request Failed: {e}")
        return ""
        
    return full_response

def process_file(file_path):
    print(f"\n📚 Processing: {os.path.basename(file_path)}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # Split into chunks of 2500 words
    words = text.split()
    chunks = [" ".join(words[i:i + 2500]) for i in range(0, len(words), 2500)]
    print(f"  -> Separated into {len(chunks)} chunks.")
    
    final_summary = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\n⏳ Summarizing Chunk {i}/{len(chunks)}...")
        summary = summarize_with_ollama(chunk)
        final_summary.append(summary)
        
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    result_json = {
        "source_file": os.path.basename(file_path),
        "total_chunks": len(chunks),
        "summary": "\n\n".join(final_summary)
    }
    
    out_path = os.path.join(OUT_DIR, f"{base_name}_summary.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved summary. Updating Web Viewer...")
    
    # LIVE UPDATE: Trigger viewer update immediately for this file
    update_viewer.update_viewer()

if __name__ == "__main__":
    if not check_ollama_health():
        exit(1)
        
    txt_files = glob.glob(os.path.join(TXT_INBOX, "*.txt"))
    for idx, filepath in enumerate(txt_files, 1):
        print(f"\n[{idx}/{len(txt_files)}] =====================================")
        process_file(filepath)
