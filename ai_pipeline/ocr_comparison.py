"""
OCR Comparison Module - โมดูลเปรียบเทียบ OCR 2 แบบ
================================================================
แบบที่ 1: EasyOCR - โมเดล OCR โอเพนซอร์สที่รองรับภาษาไทยดี
แบบที่ 2: Deepseek OCR - ใช้ Deepseek Vision API สำหรับ OCR ขั้นสูง

วิธีใช้:
    python ocr_comparison.py --input <path> --method [easyocr|deepseek|both]
"""

import os
import re
import sys
import json
import time
import base64
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Deepseek API Configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# EasyOCR Configuration
EASYOCR_LANGS = ['th', 'en']  # ภาษาไทย + อังกฤษ

# Output Directories
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ocr_comparison")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@dataclass
class OCResult:
    """Data class สำหรับเก็บผลลัพธ์ OCR"""
    method: str
    text: str
    confidence: float
    processing_time: float
    word_count: int
    error: Optional[str] = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def encode_image_to_base64(image_path: str) -> str:
    """แปลงรูปภาพเป็น base64 string"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def clean_thai_ocr_text(text: str) -> str:
    """ทำความสะอาดข้อความ OCR ภาษาไทย"""
    if not text:
        return ""

    # แก้ไขสระลอยที่พบบ่อยใน OCR ภาษาไทย
    fixes = {
        'เ เ': 'แ',
        ' ำ': 'ำ',
        ' า': 'ำ',
        ' ึ': 'ึ',
        ' ื': 'ื',
        ' ั': 'ั',
        ' ิ': 'ิ',
        ' ี': 'ี',
        ' ุ': 'ุ',
        ' ู': 'ู',
        ' ์': '์',
        ' ่': '่',
        ' ้': '้',
        ' ๊': '๊',
        ' ๋': '๋',
        'อ านาจ': 'อำนาจ',
        'ค าสั่ง': 'คำสั่ง',
        'ส านัก': 'สำนัก',
        'กฎ หมาย': 'กฎหมาย',
        'วิ ธี': 'วิธี',
    }

    cleaned = text
    for wrong, right in fixes.items():
        cleaned = cleaned.replace(wrong, right)

    # ลบช่องว่างซ้ำ
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()


def calculate_confidence_metrics(text: str, method: str) -> float:
    """คำนวณความมั่นใจโดยประมาณจากคุณภาพข้อความ"""
    if not text:
        return 0.0

    score = 100.0

    # ตรวจสอบสระลอย (common OCR error)
    floating_vowels = text.count('่ ') + text.count('้ ') + text.count('์ ')
    score -= floating_vowels * 2

    # ตรวจสอบตัวอักษรที่แยกกัน
    separated = text.count('ก ') + text.count('ข ') + text.count('ค ')
    score -= separated * 1.5

    # ตรวจสอบสัญลักษณ์แปลก
    weird_chars = sum(1 for c in text if ord(c) > 0xE000)
    score -= weird_chars * 5

    # คะแนนความยาวที่เหมาะสม
    if len(text) < 50:
        score -= 20

    return max(0.0, min(100.0, score))


# =============================================================================
# EASY OCR IMPLEMENTATION
# =============================================================================

class EasyOCRProcessor:
    """
    EasyOCR Implementation
    ข้อดี: ฟรี, เร็ว, ไม่ต้องใช้อินเทอร์เน็ต, รองรับภาษาไทยดี
    ข้อเสีย: อาจมีข้อผิดพลาดกับเอกสารซับซ้อน, ต้องติดตั้งโมเดลก่อนใช้งาน
    """

    def __init__(self):
        self.reader = None
        self._initialized = False

    def initialize(self):
        """โหลดโมเดล EasyOCR"""
        if self._initialized:
            return True

        try:
            import easyocr
            print("🔄 กำลังโหลด EasyOCR (ครั้งแรกอาจใช้เวลา)...")
            self.reader = easyocr.Reader(
                EASYOCR_LANGS,
                gpu=False,  # ใช้ CPU เพื่อความเสถียร
                verbose=False
            )
            self._initialized = True
            print("[OK] EasyOCR พร้อมใช้งาน")
            return True
        except ImportError:
            print("[FAIL] กรุณาติดตั้ง EasyOCR: pip install easyocr")
            return False
        except Exception as e:
            print(f"[FAIL] EasyOCR Error: {e}")
            return False

    def process_image(self, image_path: str) -> OCResult:
        """ประมวลผลรูปภาพด้วย EasyOCR"""
        start_time = time.time()

        if not self.initialize():
            return OCResult(
                method="easyocr",
                text="",
                confidence=0.0,
                processing_time=0.0,
                word_count=0,
                error="Failed to initialize EasyOCR"
            )

        try:
            # อ่านข้อความจากรูปภาพ
            results = self.reader.readtext(image_path, detail=1)

            # รวมข้อความทั้งหมด
            text_parts = []
            total_confidence = 0.0

            for (bbox, text, conf) in results:
                text_parts.append(text)
                total_confidence += conf

            raw_text = ' '.join(text_parts)
            cleaned_text = clean_thai_ocr_text(raw_text)

            processing_time = time.time() - start_time
            avg_confidence = (total_confidence / len(results) * 100) if results else 0
            word_count = len(cleaned_text.split())

            return OCResult(
                method="easyocr",
                text=cleaned_text,
                confidence=avg_confidence,
                processing_time=processing_time,
                word_count=word_count
            )

        except Exception as e:
            return OCResult(
                method="easyocr",
                text="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                word_count=0,
                error=str(e)
            )

    def process_pdf(self, pdf_path: str) -> OCResult:
        """ประมวลผล PDF โดยแปลงเป็นรูปภาพก่อน"""
        try:
            import fitz  # PyMuPDF
            from PIL import Image

            start_time = time.time()
            all_texts = []
            total_confidence = 0.0
            page_count = 0

            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # แปลงหน้าเป็นรูปภาพ
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better OCR
                img_data = pix.tobytes("png")

                # บันทึกเป็นไฟล์ชั่วคราว
                temp_path = os.path.join(OUTPUT_DIR, f"temp_page_{page_num}.png")
                with open(temp_path, 'wb') as f:
                    f.write(img_data)

                # OCR หน้านี้
                result = self.process_image(temp_path)

                if result.text:
                    all_texts.append(f"--- หน้า {page_num + 1} ---\n{result.text}")
                    total_confidence += result.confidence
                    page_count += 1

                # ลบไฟล์ชั่วคราว
                os.remove(temp_path)

            doc.close()

            full_text = '\n\n'.join(all_texts)
            processing_time = time.time() - start_time
            avg_confidence = total_confidence / page_count if page_count > 0 else 0

            return OCResult(
                method="easyocr_pdf",
                text=full_text,
                confidence=avg_confidence,
                processing_time=processing_time,
                word_count=len(full_text.split())
            )

        except Exception as e:
            return OCResult(
                method="easyocr_pdf",
                text="",
                confidence=0.0,
                processing_time=0.0,
                word_count=0,
                error=str(e)
            )


# =============================================================================
# DEEPSEEK OCR IMPLEMENTATION
# =============================================================================

class DeepseekOCRProcessor:
    """
    Deepseek Vision API OCR
    ข้อดี: แม่นยำสูง, เข้าใจบริบทเอกสารกฎหมาย, รองรับเอกสารซับซ้อน
    ข้อเสีย: ต้องใช้ API Key, มีค่าใช้จ่าย, ต้องต่ออินเทอร์เน็ต
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL

    def _call_api(self, image_base64: str, is_pdf_page: bool = False) -> str:
        """เรียก Deepseek Vision API"""
        import requests

        if not self.api_key:
            raise ValueError("Deepseek API Key not found. Set DEEPSEEK_API_KEY environment variable.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Prompt สำหรับ OCR เอกสารกฎหมาย
        system_prompt = """คุณคือผู้เชี่ยวชาญ OCR เอกสารกฎหมายไทย

หน้าที่:
1. อ่านข้อความทั้งหมดจากภาพให้ครบถ้วน
2. รักษาโครงสร้างเอกสาร (หัวข้อ, มาตรา, ย่อหน้า)
3. แก้ไขสระลอยและตัวอักษรที่ผิดธรรมดาเองโดยอัตโนมัติ
4. ใช้ภาษากฎหมายที่ถูกต้อง
5. ตอบกลับเฉพาะข้อความที่อ่านได้เท่านั้น ไม่ต้องอธิบายเพิ่มเติม"""

        # Deepseek API ใช้รูปแบบ OpenAI-compatible
        # หมายเหตุ: Deepseek อาจไม่รองรับ vision โดยตรง อาจต้องใช้ multi-modal model อื่น
        payload = {
            "model": "deepseek-chat",  # สำหรับ text OCR หรือ deepseek-vision ถ้ามี
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "อ่านข้อความทั้งหมดจากเอกสารนี้ เก็บรักษาโครงสร้างหัวข้อและมาตราไว้ให้ครบถ้วน"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']

    def process_image(self, image_path: str) -> OCResult:
        """ประมวลผลรูปภาพด้วย Deepseek Vision"""
        start_time = time.time()

        try:
            base64_image = encode_image_to_base64(image_path)
            text = self._call_api(base64_image)
            cleaned_text = clean_thai_ocr_text(text)

            processing_time = time.time() - start_time
            confidence = calculate_confidence_metrics(cleaned_text, "deepseek")

            return OCResult(
                method="deepseek",
                text=cleaned_text,
                confidence=confidence,
                processing_time=processing_time,
                word_count=len(cleaned_text.split())
            )

        except Exception as e:
            return OCResult(
                method="deepseek",
                text="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                word_count=0,
                error=str(e)
            )

    def process_pdf(self, pdf_path: str) -> OCResult:
        """ประมวลผล PDF ด้วย Deepseek Vision"""
        try:
            import fitz

            start_time = time.time()
            all_texts = []
            total_confidence = 0.0
            page_count = 0

            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

                # แปลงเป็น base64 โดยตรง
                img_data = pix.tobytes("png")
                base64_image = base64.b64encode(img_data).decode('utf-8')

                text = self._call_api(base64_image, is_pdf_page=True)
                cleaned_text = clean_thai_ocr_text(text)

                if cleaned_text:
                    all_texts.append(f"--- หน้า {page_num + 1} ---\n{cleaned_text}")
                    total_confidence += calculate_confidence_metrics(cleaned_text, "deepseek")
                    page_count += 1

            doc.close()

            full_text = '\n\n'.join(all_texts)
            processing_time = time.time() - start_time
            avg_confidence = total_confidence / page_count if page_count > 0 else 0

            return OCResult(
                method="deepseek_pdf",
                text=full_text,
                confidence=avg_confidence,
                processing_time=processing_time,
                word_count=len(full_text.split())
            )

        except Exception as e:
            return OCResult(
                method="deepseek_pdf",
                text="",
                confidence=0.0,
                processing_time=0.0,
                word_count=0,
                error=str(e)
            )


# =============================================================================
# COMPARISON & REPORTING
# =============================================================================

def compare_ocr_methods(input_path: str, save_results: bool = True) -> Dict[str, OCResult]:
    """
    เปรียบเทียบผลลัพธ์ OCR ทั้ง 2 แบบ

    Args:
        input_path: พาธไปยังไฟล์รูปภาพหรือ PDF
        save_results: บันทึกผลลัพธ์ลงไฟล์หรือไม่

    Returns:
        Dictionary ของผลลัพธ์ OCR
    """
    results = {}

    print("=" * 60)
    print("🔍 OCR COMPARISON MODE")
    print("=" * 60)
    print(f"📄 ไฟล์: {os.path.basename(input_path)}")
    print()

    # EasyOCR
    print("[TEXT] กำลังประมวลผลด้วย EasyOCR...")
    easyocr_processor = EasyOCRProcessor()

    if input_path.lower().endswith('.pdf'):
        results['easyocr'] = easyocr_processor.process_pdf(input_path)
    else:
        results['easyocr'] = easyocr_processor.process_image(input_path)

    print(f"   [OK] เสร็จสิ้นใน {results['easyocr'].processing_time:.2f} วินาที")
    print(f"   📊 Confidence: {results['easyocr'].confidence:.1f}%")
    print(f"   [TEXT] Words: {results['easyocr'].word_count}")
    if results['easyocr'].error:
        print(f"   [WARN] Error: {results['easyocr'].error}")
    print()

    # Deepseek OCR (ถ้ามี API Key)
    if DEEPSEEK_API_KEY:
        print("[AI] กำลังประมวลผลด้วย Deepseek Vision...")
        deepseek_processor = DeepseekOCRProcessor()

        if input_path.lower().endswith('.pdf'):
            results['deepseek'] = deepseek_processor.process_pdf(input_path)
        else:
            results['deepseek'] = deepseek_processor.process_image(input_path)

        print(f"   [OK] เสร็จสิ้นใน {results['deepseek'].processing_time:.2f} วินาที")
        print(f"   📊 Confidence: {results['deepseek'].confidence:.1f}%")
        print(f"   [TEXT] Words: {results['deepseek'].word_count}")
        if results['deepseek'].error:
            print(f"   [WARN] Error: {results['deepseek'].error}")
    else:
        print("[WARN] ข้าม Deepseek OCR (ไม่พบ API Key)")
        print("   ตั้งค่า: set DEEPSEEK_API_KEY=your_key_here")

    print()

    # บันทึกผลลัพธ์
    if save_results:
        timestamp = int(time.time())
        base_name = Path(input_path).stem

        # บันทึกแต่ละแบบแยกไฟล์
        for method, result in results.items():
            output_file = os.path.join(OUTPUT_DIR, f"{base_name}_{method}_{timestamp}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Method: {result.method}\n")
                f.write(f"Confidence: {result.confidence:.1f}%\n")
                f.write(f"Processing Time: {result.processing_time:.2f}s\n")
                f.write(f"Word Count: {result.word_count}\n")
                if result.error:
                    f.write(f"Error: {result.error}\n")
                f.write("=" * 60 + "\n\n")
                f.write(result.text)
            print(f"💾 บันทึกผลลัพธ์ {method}: {output_file}")

        # บันทึก JSON comparison
        json_file = os.path.join(OUTPUT_DIR, f"{base_name}_comparison_{timestamp}.json")
        json_data = {
            "input_file": input_path,
            "timestamp": timestamp,
            "results": {
                k: {
                    "method": v.method,
                    "confidence": v.confidence,
                    "processing_time": v.processing_time,
                    "word_count": v.word_count,
                    "error": v.error,
                    "text_preview": v.text[:500] if v.text else ""
                }
                for k, v in results.items()
            }
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"💾 บันทึก JSON comparison: {json_file}")

    return results


def print_comparison_summary(results: Dict[str, OCResult]):
    """แสดงสรุปการเปรียบเทียบ"""
    print()
    print("=" * 60)
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)

    if len(results) < 2:
        print("ไม่สามารถเปรียบเทียบได้ (มีผลลัพธ์น้อยกว่า 2 แบบ)")
        return

    methods = list(results.keys())
    r1, r2 = results[methods[0]], results[methods[1]]

    # Speed comparison
    speed_diff = abs(r1.processing_time - r2.processing_time)
    faster = methods[0] if r1.processing_time < r2.processing_time else methods[1]
    print(f"\n⚡ ความเร็ว:")
    print(f"   {methods[0]}: {r1.processing_time:.2f}s")
    print(f"   {methods[1]}: {r2.processing_time:.2f}s")
    print(f"   🏆 เร็วกว่า: {faster} (ต่างกัน {speed_diff:.2f}s)")

    # Confidence comparison
    conf_diff = abs(r1.confidence - r2.confidence)
    better = methods[0] if r1.confidence > r2.confidence else methods[1]
    print(f"\n🎯 ความมั่นใจ:")
    print(f"   {methods[0]}: {r1.confidence:.1f}%")
    print(f"   {methods[1]}: {r2.confidence:.1f}%")
    print(f"   🏆 ดีกว่า: {better} (ต่างกัน {conf_diff:.1f}%)")

    # Word count comparison
    word_diff = abs(r1.word_count - r2.word_count)
    print(f"\n[TEXT] จำนวนคำ:")
    print(f"   {methods[0]}: {r1.word_count} คำ")
    print(f"   {methods[1]}: {r2.word_count} คำ")
    print(f"   📊 ต่างกัน: {word_diff} คำ")

    print("\n" + "=" * 60)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="OCR Comparison Tool - EasyOCR vs Deepseek Vision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ตัวอย่างการใช้งาน:
  python ocr_comparison.py --input document.pdf --method both
  python ocr_comparison.py --input image.png --method easyocr
  python ocr_comparison.py --input scan.pdf --method deepseek

ตั้งค่า Deepseek API Key:
  Windows: set DEEPSEEK_API_KEY=your_key_here
  Linux/Mac: export DEEPSEEK_API_KEY=your_key_here
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='พาธไปยังไฟล์รูปภาพหรือ PDF'
    )

    parser.add_argument(
        '--method', '-m',
        choices=['easyocr', 'deepseek', 'both'],
        default='both',
        help='เลือกวิธี OCR (default: both)'
    )

    parser.add_argument(
        '--output', '-o',
        help='โฟลเดอร์สำหรับบันทึกผลลัพธ์ (default: data/ocr_comparison/)'
    )

    args = parser.parse_args()

    # ตรวจสอบไฟล์
    if not os.path.exists(args.input):
        print(f"[FAIL] Error: ไม่พบไฟล์ {args.input}")
        sys.exit(1)

    # รัน OCR ตาม method ที่เลือก
    if args.method == 'both':
        results = compare_ocr_methods(args.input)
        print_comparison_summary(results)
    elif args.method == 'easyocr':
        processor = EasyOCRProcessor()
        if args.input.lower().endswith('.pdf'):
            result = processor.process_pdf(args.input)
        else:
            result = processor.process_image(args.input)

        print(f"\n{'='*60}")
        print(f"📄 Result from EasyOCR:")
        print(f"{'='*60}")
        print(result.text[:1000])
        if len(result.text) > 1000:
            print(f"\n... (ตัดข้อความ, ทั้งหมด {len(result.text)} ตัวอักษร)")
    elif args.method == 'deepseek':
        if not DEEPSEEK_API_KEY:
            print("[FAIL] Error: ไม่พบ Deepseek API Key")
            print("ตั้งค่าด้วย: set DEEPSEEK_API_KEY=your_key_here")
            sys.exit(1)

        processor = DeepseekOCRProcessor()
        if args.input.lower().endswith('.pdf'):
            result = processor.process_pdf(args.input)
        else:
            result = processor.process_image(args.input)

        print(f"\n{'='*60}")
        print(f"📄 Result from Deepseek OCR:")
        print(f"{'='*60}")
        print(result.text[:1000])
        if len(result.text) > 1000:
            print(f"\n... (ตัดข้อความ, ทั้งหมด {len(result.text)} ตัวอักษร)")


if __name__ == "__main__":
    main()
