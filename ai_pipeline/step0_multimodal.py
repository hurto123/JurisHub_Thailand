import os
import shutil
import argparse
import glob
import time
import json
import hashlib
import contextlib

# --- MONKEY PATCH FOR CPU ONLY ---
import torch
import torch.nn as nn

# Disable CUDA globally for this script to avoid hardcoded .cuda() calls in external models
def noop_cuda(self, *args, **kwargs):
    return self

torch.cuda.is_available = lambda: False
torch.Tensor.cuda = noop_cuda
nn.Module.cuda = noop_cuda
# ---------------------------------

# Optional: Try to import PDF processing libraries
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# -------------------------------------------------------------------------
# Step 0: Multimodal Pre-processor (Image/PDF -> Text)
# -------------------------------------------------------------------------

DATA_DIR = "data"
DIR_IN = os.path.join(DATA_DIR, "00_inbox")
DIR_OUT = os.path.join(DATA_DIR, "01_raw_text")

# Create folders
os.makedirs(DIR_IN, exist_ok=True)
os.makedirs(DIR_OUT, exist_ok=True)

REGISTRY_FILE = os.path.join(DATA_DIR, "processed_registry.json")

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_registry(registry_set):
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(registry_set), f)

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# GOT-OCR Loading Function (Same as test_ocr.py)
def load_got_ocr_model():
    import torch
    from transformers import AutoModel, AutoTokenizer
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    print(f"🤖 Loading GOT-OCR2.0 model on {device.upper()}...")
    tokenizer = AutoTokenizer.from_pretrained('stepfun-ai/GOT-OCR2_0', trust_remote_code=True)
    model = AutoModel.from_pretrained(
        'stepfun-ai/GOT-OCR2_0', 
        trust_remote_code=True, 
        low_cpu_mem_usage=True, 
        torch_dtype=dtype,
        device_map=device
    )
    return tokenizer, model.eval()

def ocr_image(image_path, tokenizer, model):
    print(f"  - OCRing: {os.path.basename(image_path)}")
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    with torch.no_grad():
        try:
            return model.chat(tokenizer, image_path, ocr_type='ocr')
        except Exception as e:
            if "CUDA" in str(e).lower():
                print(f"  ⚠️ Warning: Model tried to use CUDA. Falling back to CPU...")
                model.to("cpu")
                return model.chat(tokenizer, image_path, ocr_type='ocr')
            raise e

def process_file(file_path, tokenizer, model):
    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    output_text = ""

    if ext == ".txt":
        print(f"📄 Copying text file: {filename}")
        shutil.copy(file_path, os.path.join(DIR_OUT, filename))
        return True

    elif ext in [".png", ".jpg", ".jpeg"]:
        if not model:
            tokenizer, model = load_got_ocr_model()
        print(f"📸 Processing image: {filename}")
        output_text = ocr_image(file_path, tokenizer, model)
        
    elif ext == ".pdf":
        print(f"📖 Processing PDF: {filename}")
        
        # 1. Try digital text extraction first
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    text_content = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                    
                    if text_content.strip():
                        print(f"  ✅ Extracted digital text from PDF.")
                        output_text = text_content
            except Exception as e:
                print(f"  ⚠️ Digital extraction failed: {e}")

        # 2. If no text found or failed, use OCR
        if not output_text.strip():
            print(f"  🔍 No digital text found, starting OCR for PDF...")
            if not fitz and not convert_from_path:
                print("  ❌ Neither PyMuPDF nor pdf2image found. Cannot OCR PDF. Please run: pip install PyMuPDF")
            else:
                try:
                    if not model:
                        tokenizer, model = load_got_ocr_model()
                    
                    # Store temp images in root/temp_ocr/
                    temp_dir = "temp_ocr"
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    pdf_texts = []
                    if fitz:
                        doc = fitz.open(file_path)
                        total_pages = len(doc)
                        for i in range(total_pages):
                            print(f"    📄 Processing Page {i+1}/{total_pages}...")
                            page = doc.load_page(i)
                            pix = page.get_pixmap(dpi=150)
                            temp_img_path = os.path.join(temp_dir, f"page_{i}.png")
                            pix.save(temp_img_path)
                            page_text = ocr_image(temp_img_path, tokenizer, model)
                            pdf_texts.append(page_text)
                            os.remove(temp_img_path)
                    else:
                        images = convert_from_path(file_path)
                        total_pages = len(images)
                        for i, image in enumerate(images):
                            print(f"    📄 Processing Page {i+1}/{total_pages}...")
                            temp_img_path = os.path.join(temp_dir, f"page_{i}.png")
                            image.save(temp_img_path, "PNG")
                            page_text = ocr_image(temp_img_path, tokenizer, model)
                            pdf_texts.append(page_text)
                            os.remove(temp_img_path) # Clean up
                    
                    output_text = "\n\n".join(pdf_texts)
                except Exception as e:
                    print(f"  ❌ OCR PDF failed: {e}")

    # Save output if we have content
    if output_text.strip():
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        with open(os.path.join(DIR_OUT, txt_filename), 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"✅ Success: {txt_filename} saved to {DIR_OUT}")
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force_ocr", action="store_true", help="Force OCR on PDFs even if text-based")
    args = parser.parse_args()

    files = glob.glob(os.path.join(DIR_IN, "*.*"))
    if not files or (len(files) == 1 and files[0].endswith(".placeholder")):
        print("💡 Inbox is empty. Put .pdf, .png, .jpg files in data/00_inbox first.")
        return

    tokenizer = None
    model = None

    print(f"🚀 Starting Multimodal Pre-processor...")
    registry = load_registry()

    for f in files:
        if f.endswith(".placeholder"): continue
        
        file_hash = get_file_hash(f)
        if file_hash in registry:
            print(f"⏭️ Skipping {os.path.basename(f)} (Already processed previously).")
            # Move to done anyway to clear inbox
            done_dir = os.path.join(DATA_DIR, "00_done")
            os.makedirs(done_dir, exist_ok=True)
            shutil.move(f, os.path.join(done_dir, os.path.basename(f)))
            continue

        try:
            success = process_file(f, tokenizer, model)
            if success:
                registry.add(file_hash)
                save_registry(registry)
                
            # Move processed file to a 'done' folder
            done_dir = os.path.join(DATA_DIR, "00_done")
            os.makedirs(done_dir, exist_ok=True)
            shutil.move(f, os.path.join(done_dir, os.path.basename(f)))
        except Exception as e:
            print(f"💥 Failed to process {f}: {e}")

    print("🏁 Step 0 Complete. All conversions finished.")

if __name__ == "__main__":
    main()
