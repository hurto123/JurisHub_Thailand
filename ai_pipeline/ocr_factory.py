"""
OCR Factory - ระบบเลือกใช้ OCR ตามความเหมาะสม
================================================================
รองรับ:
- EasyOCR (ฟรี, เร็ว, ใช้ CPU)
- Deepseek Vision (แม่นยำ, ใช้ API)
- Tesseract (สำรอง, มีอยู่แล้ว)
- GOT-OCR2.0 (โมเดล AI ที่มีอยู่เดิม)

วิธีใช้ใน Pipeline:
    from ocr_factory import OCFactory

    factory = OCFactory()
    result = factory.process_file("document.pdf", method="easyocr")
"""

import os
import sys
import time
import json
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))


class OCRMethod(Enum):
    """Enum สำหรับเลือกวิธี OCR"""
    EASYOCR = "easyocr"
    DEEPSEEK = "deepseek"
    TESSERACT = "tesseract"
    GOT_OCR = "got_ocr"
    AUTO = "auto"  # เลือกอัตโนมัติตามสภาพแวดล้อม


@dataclass
class OCResult:
    """ผลลัพธ์ OCR"""
    text: str
    method: str
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None


class OCFactory:
    """
    Factory class สำหรับ OCR
    เลือกใช้ method ที่เหมาะสมตามไฟล์และสภาพแวดล้อม
    """

    # Class-level cache สำหรับ models ที่โหลดแล้ว
    _model_cache: Dict[str, Any] = {}
    _easyocr_processor = None

    def __init__(self):
        self._processors: Dict[str, Callable] = {}
        self._initialized: Dict[str, bool] = {}
        self._available_methods: list = []

        # ตรวจสอบ methods ที่ใช้ได้
        self._detect_available_methods()

    def _get_cached_easyocr(self):
        """Get or create EasyOCR processor (singleton)"""
        if OCFactory._easyocr_processor is None:
            from ocr_comparison import EasyOCRProcessor
            OCFactory._easyocr_processor = EasyOCRProcessor()
        return OCFactory._easyocr_processor

    def _detect_available_methods(self):
        """ตรวจสอบว่ามี methods ไหนใช้ได้บ้าง"""
        print("[CHECK] ตรวจสอบ OCR Methods ที่ใช้ได้...")

        # Check EasyOCR
        try:
            import easyocr
            self._available_methods.append("easyocr")
            print("   [OK] EasyOCR พร้อมใช้งาน")
        except ImportError:
            print("   [FAIL] EasyOCR (ติดตั้ง: pip install easyocr)")

        # Check Deepseek
        if os.environ.get("DEEPSEEK_API_KEY"):
            self._available_methods.append("deepseek")
            print("   [OK] Deepseek Vision พร้อมใช้งาน")
        else:
            print("   [FAIL] Deepseek (ตั้งค่า DEEPSEEK_API_KEY)")

        # Check Tesseract
        try:
            import pytesseract
            # ตรวจสอบว่า tesseract ติดตั้งแล้ว
            version = pytesseract.get_tesseract_version()
            self._available_methods.append("tesseract")
            print(f"   [OK] Tesseract {version} พร้อมใช้งาน")
        except:
            print("   [FAIL] Tesseract (ติดตั้ง Tesseract-OCR และเพิ่มลง PATH)")

        # Check GOT-OCR
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
            self._available_methods.append("got_ocr")
            print("   [OK] GOT-OCR2.0 พร้อมใช้งาน")
        except ImportError:
            print("   [FAIL] GOT-OCR2.0 (ติดตั้ง: pip install transformers torch)")

        print()

    def get_recommended_method(self, file_path: str) -> str:
        """
        แนะนำ method ที่เหมาะสมที่สุดสำหรับไฟล์

        - ไฟล์สแกนคุณภาพต่ำ: Deepseek > EasyOCR > Tesseract
        - ไฟล์สแกนคุณภาพดี: EasyOCR (เร็วกว่า)
        - ไฟล์ขนาดใหญ่: EasyOCR (ไม่ต้องใช้อินเทอร์เน็ต)
        - PDF หลายหน้า: EasyOCR (ฟรี)
        """
        if not self._available_methods:
            raise RuntimeError("ไม่มี OCR Method ที่ใช้ได้!")

        ext = os.path.splitext(file_path)[1].lower()

        # Priority:
        # 1. EasyOCR (ถ้ามี) - ดีที่สุดสำหรับเอกสารไทย ฟรี
        if "easyocr" in self._available_methods:
            return "easyocr"

        # 2. Deepseek (ถ้ามี API) - แม่นยำสูง
        if "deepseek" in self._available_methods:
            return "deepseek"

        # 3. Tesseract - สำรอง
        if "tesseract" in self._available_methods:
            return "tesseract"

        # 4. GOT-OCR - ใช้ GPU
        if "got_ocr" in self._available_methods:
            return "got_ocr"

        return self._available_methods[0]

    def process_file(
        self,
        file_path: str,
        method: str = "auto",
        **kwargs
    ) -> OCResult:
        """
        ประมวลผลไฟล์ด้วย OCR method ที่เลือก

        Args:
            file_path: พาธไปยังไฟล์
            method: "easyocr", "deepseek", "tesseract", "got_ocr", "auto"
            **kwargs: options เฉพาะ method

        Returns:
            OCResult object
        """
        if not os.path.exists(file_path):
            return OCResult(
                text="",
                method=method,
                confidence=0.0,
                processing_time=0.0,
                metadata={},
                error=f"File not found: {file_path}"
            )

        # Auto-select method
        if method == "auto":
            method = self.get_recommended_method(file_path)
            print(f"🤖 Auto-selected method: {method}")

        # Route to appropriate processor
        if method == "easyocr":
            return self._process_with_easyocr(file_path, **kwargs)
        elif method == "deepseek":
            return self._process_with_deepseek(file_path, **kwargs)
        elif method == "tesseract":
            return self._process_with_tesseract(file_path, **kwargs)
        elif method == "got_ocr":
            return self._process_with_got_ocr(file_path, **kwargs)
        else:
            return OCResult(
                text="",
                method=method,
                confidence=0.0,
                processing_time=0.0,
                metadata={},
                error=f"Unknown method: {method}"
            )

    def _process_with_easyocr(self, file_path: str, **kwargs) -> OCResult:
        """ประมวลผลด้วย EasyOCR"""
        import time
        start_time = time.time()

        try:
            # Use cached processor
            processor = self._get_cached_easyocr()
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.pdf':
                result = processor.process_pdf(file_path)
            else:
                result = processor.process_image(file_path)

            return OCResult(
                text=result.text,
                method="easyocr",
                confidence=result.confidence,
                processing_time=time.time() - start_time,
                metadata={"pages": kwargs.get("pages", 1)},
                error=result.error
            )

        except Exception as e:
            return OCResult(
                text="",
                method="easyocr",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )

    def _process_with_deepseek(self, file_path: str, **kwargs) -> OCResult:
        """ประมวลผลด้วย Deepseek Vision"""
        import time
        start_time = time.time()

        try:
            from ocr_comparison import DeepseekOCRProcessor

            processor = DeepseekOCRProcessor()
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.pdf':
                result = processor.process_pdf(file_path)
            else:
                result = processor.process_image(file_path)

            return OCResult(
                text=result.text,
                method="deepseek",
                confidence=result.confidence,
                processing_time=time.time() - start_time,
                metadata={},
                error=result.error
            )

        except Exception as e:
            return OCResult(
                text="",
                method="deepseek",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )

    def _process_with_tesseract(self, file_path: str, **kwargs) -> OCResult:
        """ประมวลผลด้วย Tesseract"""
        start_time = time.time()

        try:
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF

            # Setup Tesseract path on Windows
            if sys.platform == 'win32':
                tesseract_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    os.path.join(os.environ.get("USERPROFILE", ""),
                               r"AppData\Local\Tesseract-OCR\tesseract.exe")
                ]
                for path in tesseract_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break

            ext = os.path.splitext(file_path)[1].lower()
            all_text = []

            if ext == '.pdf':
                # Convert PDF to images and OCR
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = pytesseract.image_to_string(img, lang='tha+eng')
                    all_text.append(f"--- หน้า {page_num + 1} ---\n{text}")
                doc.close()
            else:
                # Direct image OCR
                img = Image.open(file_path)
                all_text.append(pytesseract.image_to_string(img, lang='tha+eng'))

            full_text = '\n\n'.join(all_text)
            processing_time = time.time() - start_time

            # คำนวณความมั่นใจโดยประมาณ
            confidence = 70.0  # Tesseract baseline
            if '่ ' in full_text or '้ ' in full_text:
                confidence -= 10  # มีสระลอย

            return OCResult(
                text=full_text,
                method="tesseract",
                confidence=max(0, confidence),
                processing_time=processing_time,
                metadata={"lang": "tha+eng"}
            )

        except Exception as e:
            return OCResult(
                text="",
                method="tesseract",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )

    def _get_cached_got_ocr(self):
        """Get or create GOT-OCR model (singleton)"""
        if 'got_ocr' not in OCFactory._model_cache:
            import torch
            from transformers import AutoModel, AutoTokenizer

            print("[LOAD] กำลังโหลด GOT-OCR2.0 model (ครั้งแรก)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32

            tokenizer = AutoTokenizer.from_pretrained(
                'stepfun-ai/GOT-OCR2_0',
                trust_remote_code=True
            )
            model = AutoModel.from_pretrained(
                'stepfun-ai/GOT-OCR2_0',
                trust_remote_code=True,
                torch_dtype=dtype,
                device_map=device
            )
            model.eval()

            OCFactory._model_cache['got_ocr'] = (tokenizer, model, device)
            print(f"[OK] GOT-OCR2.0 พร้อมใช้งาน ({device})")

        return OCFactory._model_cache['got_ocr']

    def _process_with_got_ocr(self, file_path: str, **kwargs) -> OCResult:
        """ประมวลผลด้วย GOT-OCR2.0 (โมเดลเดิม)"""
        import time
        import torch
        import fitz

        start_time = time.time()

        try:
            # Use cached model
            tokenizer, model, device = self._get_cached_got_ocr()

            ext = os.path.splitext(file_path)[1].lower()
            all_text = []

            if ext == '.pdf':
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=150)
                    temp_path = f"temp_got_{page_num}.png"
                    pix.save(temp_path)

                    with torch.no_grad():
                        text = model.chat(tokenizer, temp_path, ocr_type='ocr')
                    all_text.append(f"--- หน้า {page_num + 1} ---\n{text}")
                    os.remove(temp_path)
                doc.close()
            else:
                with torch.no_grad():
                    all_text.append(model.chat(tokenizer, file_path, ocr_type='ocr'))

            full_text = '\n\n'.join(all_text)

            return OCResult(
                text=full_text,
                method="got_ocr",
                confidence=85.0,  # GOT-OCR มักให้ผลดี
                processing_time=time.time() - start_time,
                metadata={"device": device}
            )

        except Exception as e:
            return OCResult(
                text="",
                method="got_ocr",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )


def batch_process(
    input_dir: str,
    output_dir: str,
    method: str = "auto",
    extensions: tuple = ('.pdf', '.png', '.jpg', '.jpeg')
) -> Dict[str, OCResult]:
    """
    ประมวลผลไฟล์หลายไฟล์พร้อมกัน

    Args:
        input_dir: โฟลเดอร์ที่มีไฟล์
        output_dir: โฟลเดอร์สำหรับบันทึกผล
        method: OCR method ที่ต้องการใช้
        extensions: นามสกุลไฟล์ที่รองรับ

    Returns:
        Dictionary mapping filename -> OCResult
    """
    import glob

    factory = OCFactory()
    results = {}

    os.makedirs(output_dir, exist_ok=True)

    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(input_dir, f"*{ext}")))

    print(f"🚀 Batch Processing {len(files)} files with {method}...")
    print("=" * 60)

    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        print(f"\n[{i}/{len(files)}] Processing: {filename}")

        result = factory.process_file(file_path, method=method)
        results[filename] = result

        # Save result
        output_name = os.path.splitext(filename)[0] + ".txt"
        output_path = os.path.join(output_dir, output_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR Result: {filename}\n")
            f.write(f"# Method: {result.method}\n")
            f.write(f"# Confidence: {result.confidence:.1f}%\n")
            f.write(f"# Time: {result.processing_time:.2f}s\n")
            if result.error:
                f.write(f"# Error: {result.error}\n")
            f.write("=" * 60 + "\n\n")
            f.write(result.text)

        status = "[OK]" if not result.error else "[FAIL]"
        print(f"   {status} {result.method} | {result.confidence:.0f}% | {result.processing_time:.1f}s")

    # Summary
    print("\n" + "=" * 60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results.values() if not r.error)
    total_time = sum(r.processing_time for r in results.values())

    print(f"Total files: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average time: {total_time/len(results):.1f}s" if results else "N/A")

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OCR Factory - Multi-method OCR processing")
    parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    parser.add_argument('--output', '-o', help='Output directory (for batch mode)')
    parser.add_argument('--method', '-m', default='auto',
                       choices=['auto', 'easyocr', 'deepseek', 'tesseract', 'got_ocr'],
                       help='OCR method to use')
    parser.add_argument('--batch', '-b', action='store_true', help='Batch process directory')

    args = parser.parse_args()

    if args.batch:
        if not os.path.isdir(args.input):
            print(f"[FAIL] Error: {args.input} is not a directory")
            sys.exit(1)
        batch_process(args.input, args.output or "ocr_output", args.method)
    else:
        if not os.path.isfile(args.input):
            print(f"[FAIL] Error: {args.input} is not a file")
            sys.exit(1)

        factory = OCFactory()
        result = factory.process_file(args.input, method=args.method)

        print("\n" + "=" * 60)
        print(f"📄 OCR Result - {result.method}")
        print("=" * 60)
        print(f"Confidence: {result.confidence:.1f}%")
        print(f"Time: {result.processing_time:.2f}s")
        if result.error:
            print(f"Error: {result.error}")
        print("=" * 60)
        print(result.text[:2000])
        if len(result.text) > 2000:
            print(f"\n... ({len(result.text)} characters total)")
