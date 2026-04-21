import os
import glob
import pdfplumber
import pytesseract
from PIL import Image
import sys

# Setup Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INBOX_DIR = os.path.join(BASE_DIR, "data", "00_inbox")
OUT_DIR = os.path.join(BASE_DIR, "data", "01_raw_text")

# --- Auto-detect Tesseract on Windows ---
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Users\hurto\AppData\Local\Tesseract-OCR\tesseract.exe",
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData\Local\Tesseract-OCR\tesseract.exe")
]

for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break
# ----------------------------------------

os.makedirs(OUT_DIR, exist_ok=True)

def process_pdf(pdf_path):
    print(f"📖 กำลังอ่าน PDF: {os.path.basename(pdf_path)}")
    text_content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
                else:
                    # ถ้าหน้านั้นไม่มี Text (เป็นหน้าสแกน) ให้ใช้ Tesseract
                    print(f"  - หน้า {i+1}: ไม่พบตัวหนังสือแบบ Digital กำลังใช้ OCR สแกนภาพ...")
                    img = page.to_image().original
                    text_content += pytesseract.image_to_string(img, lang='tha+eng') + "\n"
        return text_content
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดกับ PDF: {e}")
        return None

def process_image(img_path):
    print(f"📸 กำลังสแกนรูปภาพ: {os.path.basename(img_path)}")
    try:
        text = pytesseract.image_to_string(Image.open(img_path), lang='tha+eng')
        return text
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดกับรูปภาพ: {e}")
        return None

def main():
    files = glob.glob(os.path.join(INBOX_DIR, "*.*"))
    if not files:
        print(f"💡 ไม่พบไฟล์ใน {INBOX_DIR} กรุณานำไฟล์ไปวางก่อนครับ")
        return

    for fpath in files:
        filename = os.path.basename(fpath)
        out_name = os.path.splitext(filename)[0] + ".txt"
        out_path = os.path.join(OUT_DIR, out_name)

        # Skip if already processed
        if os.path.exists(out_path):
            print(f"⏩ ข้ามไฟล์เดิม: {out_name}")
            continue

        ext = os.path.splitext(fpath)[1].lower()
        content = None

        if ext == ".pdf":
            content = process_pdf(fpath)
        elif ext in [".png", ".jpg", ".jpeg"]:
            content = process_image(fpath)
        else:
            print(f"⏩ ข้ามไฟล์ที่ไม่รองรับ: {filename}")
            continue

        if content:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ สำเร็จ! บันทึกไฟล์ไปที่: {out_name}")

            # ย้ายไฟล์ที่เสร็จแล้วไปเก็บ (เพื่อไม่ให้สแกนซ้ำ)
            # done_dir = os.path.join(BASE_DIR, "data", "00_done")
            # os.makedirs(done_dir, exist_ok=True)
            # os.rename(fpath, os.path.join(done_dir, filename))

if __name__ == "__main__":
    print("🚀 เริ่มระบบสแกนเอกสาร (Non-AI Mode)...")
    main()
    print("✨ ขบวนการสแกนเสร็จสิ้น")
