"""
Step 0: Multimodal Pre-processor v2 (Multiple OCR Support)
================================================================
รองรับ OCR หลายแบบ:
- easyocr: เร็ว, ฟรี, ใช้ CPU (แนะนำ)
- deepseek: แม่นยำสูง, ต้องมี API Key
- tesseract: สำรอง, มีอยู่แล้ว
- got_ocr: โมเดล AI (เดิม)

การใช้งาน:
    python step0_multimodal_v2.py --input <path> --method easyocr
    python step0_multimodal_v2.py --inbox  # ประมวลผลทั้ง inbox
"""

import os
import shutil
import argparse
import glob
import time
import json
import hashlib

# Import OCR Factory
from ocr_factory import OCFactory, batch_process

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DIR_IN = os.path.join(DATA_DIR, "00_inbox")
DIR_OUT = os.path.join(DATA_DIR, "01_raw_text")
DIR_DONE = os.path.join(DATA_DIR, "00_done")

# Create folders
os.makedirs(DIR_IN, exist_ok=True)
os.makedirs(DIR_OUT, exist_ok=True)
os.makedirs(DIR_DONE, exist_ok=True)

REGISTRY_FILE = os.path.join(DATA_DIR, "processed_registry.json")


def load_registry():
    """โหลด registry ไฟล์ที่ประมวลผลแล้ว"""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()


def save_registry(registry_set):
    """บันทึก registry"""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(registry_set), f)


def get_file_hash(filepath):
    """คำนวณ hash ของไฟล์"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def process_file(file_path: str, method: str = "auto", factory: OCFactory = None) -> bool:
    """
    ประมวลผลไฟล์เดี่ยว

    Args:
        file_path: พาธไฟล์
        method: OCR method (easyocr, deepseek, tesseract, got_ocr, auto)
        factory: OCFactory instance (optional, จะสร้างใหม่ถ้าไม่มี)

    Returns:
        bool: สำเร็จหรือไม่
    """
    if factory is None:
        factory = OCFactory()

    ext = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)

    # Skip text files (copy directly)
    if ext == ".txt":
        print(f"📄 Copying text file: {filename}")
        shutil.copy(file_path, os.path.join(DIR_OUT, filename))
        return True

    # Skip unsupported files
    if ext not in ['.pdf', '.png', '.jpg', '.jpeg']:
        print(f"⏭️ ข้ามไฟล์ที่ไม่รองรับ: {filename}")
        return False

    print(f"📄 Processing: {filename}")
    print(f"   Method: {method}")

    # Run OCR
    result = factory.process_file(file_path, method=method)

    if result.error:
        print(f"   ❌ Error: {result.error}")
        return False

    if not result.text.strip():
        print(f"   ⚠️ ไม่พบข้อความในไฟล์")
        return False

    # Save output
    txt_filename = os.path.splitext(filename)[0] + ".txt"
    output_path = os.path.join(DIR_OUT, txt_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        # เขียน metadata เป็นคอมเมนต์
        f.write(f"# OCR Method: {result.method}\n")
        f.write(f"# Confidence: {result.confidence:.1f}%\n")
        f.write(f"# Processing Time: {result.processing_time:.2f}s\n")
        f.write(f"# Source: {filename}\n")
        f.write("#" + "="*58 + "\n\n")
        f.write(result.text)

    print(f"   ✅ Success! ({len(result.text)} chars, {result.processing_time:.1f}s)")
    return True


def process_inbox(method: str = "auto", skip_existing: bool = True) -> None:
    """
    ประมวลผลไฟล์ทั้งหมดใน inbox

    Args:
        method: OCR method
        skip_existing: ข้ามไฟล์ที่เคยประมวลผลแล้ว
    """
    files = glob.glob(os.path.join(DIR_IN, "*.*"))
    files = [f for f in files if not f.endswith('.placeholder')]

    if not files:
        print(f"💡 Inbox ว่างเปล่า ({DIR_IN})")
        print("   วางไฟล์ .pdf, .png, .jpg ในโฟลเดอร์ inbox ก่อนเริ่ม")
        return

    factory = OCFactory()
    registry = load_registry() if skip_existing else set()

    print("=" * 60)
    print("🚀 Starting Multimodal Pre-processor v2")
    print(f"   Method: {method}")
    print(f"   Files: {len(files)}")
    print("=" * 60)
    print()

    success_count = 0
    error_count = 0
    skip_count = 0

    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        print(f"[{i}/{len(files)}] {filename}")

        # Check registry
        if skip_existing:
            file_hash = get_file_hash(file_path)
            if file_hash in registry:
                print("   ⏭️ ข้าม (เคยประมวลผลแล้ว)")
                skip_count += 1

                # Move to done anyway
                shutil.move(file_path, os.path.join(DIR_DONE, filename))
                continue

        # Process
        try:
            success = process_file(file_path, method=method, factory=factory)

            if success:
                success_count += 1
                if skip_existing:
                    registry.add(get_file_hash(file_path))
                    save_registry(registry)

                # Move to done
                shutil.move(file_path, os.path.join(DIR_DONE, filename))
            else:
                error_count += 1

        except Exception as e:
            print(f"   💥 Exception: {e}")
            error_count += 1

        print()

    # Summary
    print("=" * 60)
    print("📊 PROCESSING COMPLETE")
    print("=" * 60)
    print(f"   สำเร็จ: {success_count}")
    print(f"   ล้มเหลว: {error_count}")
    print(f"   ข้าม: {skip_count}")
    print()
    print(f"📁 ผลลัพธ์อยู่ที่: {DIR_OUT}")
    print(f"📁 ไฟล์ต้นฉับย้ายไป: {DIR_DONE}")


def main():
    parser = argparse.ArgumentParser(
        description="Step 0: Multimodal Pre-processor v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ตัวอย่าง:
  # ประมวลผลทั้ง inbox ด้วย EasyOCR (แนะนำ)
  python step0_multimodal_v2.py --inbox --method easyocr

  # ประมวลผลไฟล์เดี่ยว
  python step0_multimodal_v2.py --input document.pdf --method auto

  # ใช้ Deepseek (ต้องตั้งค่า API Key)
  python step0_multimodal_v2.py --inbox --method deepseek

  # ประมวลผลซ้ำทั้งหมด (ไม่ข้ามไฟล์ที่เคยทำ)
  python step0_multimodal_v2.py --inbox --method easyocr --no-skip
        """
    )

    parser.add_argument('--input', '-i', help='ไฟล์เดี่ยวที่ต้องการประมวลผล')
    parser.add_argument('--inbox', action='store_true', help='ประมวลผลทั้ง inbox')
    parser.add_argument('--method', '-m', default='auto',
                       choices=['auto', 'easyocr', 'deepseek', 'tesseract', 'got_ocr'],
                       help='วิธี OCR (default: auto)')
    parser.add_argument('--no-skip', action='store_true',
                       help='ประมวลผลซ้ำแม้เคยทำแล้ว')

    args = parser.parse_args()

    if args.input:
        # Single file mode
        if not os.path.exists(args.input):
            print(f"❌ Error: ไม่พบไฟล์ {args.input}")
            return

        success = process_file(args.input, method=args.method)
        sys.exit(0 if success else 1)

    elif args.inbox:
        # Inbox mode
        process_inbox(method=args.method, skip_existing=not args.no_skip)

    else:
        parser.print_help()
        print("\n❌ Error: ต้องระบุ --input หรือ --inbox")


if __name__ == "__main__":
    import sys
    main()
