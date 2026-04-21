import argparse
import time
import torch
from transformers import AutoModel, AutoTokenizer
import json
import os

from post_process import clean_thai_text, parse_legal_layer

def load_got_ocr_model():
    """
    Loads the GOT-OCR2_0 model optimized for limited VRAM (RTX 3050 4GB).
    Uses float16 to reduce memory footprint.
    """
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained('stepfun-ai/GOT-OCR2_0', trust_remote_code=True)
    
    print("Loading model to CUDA in FP16 (Takes time)...")
    # Using device_map='cuda' and torch_dtype=torch.float16 is critical for 4GB VRAM
    model = AutoModel.from_pretrained(
        'stepfun-ai/GOT-OCR2_0', 
        trust_remote_code=True, 
        low_cpu_mem_usage=True, 
        torch_dtype=torch.float16,
        device_map='cuda'
    )
    model = model.eval()
    return tokenizer, model

def run_ocr_inference(image_path: str, tokenizer, model) -> str:
    """
    Runs OCR on the given image path.
    """
    print(f"Running OCR on: {image_path}")
    start_time = time.time()
    
    # GOT-OCR natively supports plain OCR type
    res = model.chat(tokenizer, image_path, ocr_type='ocr')
    
    end_time = time.time()
    print(f"Inference complete in {end_time - start_time:.2f} seconds.")
    
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test GOT-OCR2.0 on a sample legal document image.")
    parser.add_argument("--image", type=str, help="Path to the test image file.", default="test_sample.png")
    parser.add_argument("--format", type=str, choices=['raw', 'json'], default='json', help="Output format.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Could not find image at '{args.image}'")
        print("Please place a test image in the directory or specify path with --image.")
        print("Note: To convert PDF to image, you can use pdf2image library separately.")
        exit(1)
        
    try:
        tokenizer, model = load_got_ocr_model()
        
        # 1. Raw Text Extraction
        raw_text = run_ocr_inference(args.image, tokenizer, model)
        
        # 2. Text clean up (Post-processing)
        cleaned_text = clean_thai_text(raw_text)
        
        # 3. Output
        if args.format == 'raw':
            print("\n--- OCR OUTPUT ---")
            print(cleaned_text)
            print("------------------")
        else:
            # Parse into JSON structure layer
            parsed_json = parse_legal_layer(cleaned_text)
            print("\n--- PARSED JSON OUTPUT ---")
            print(json.dumps(parsed_json, ensure_ascii=False, indent=2))
            
    except torch.cuda.OutOfMemoryError:
        print("\n[ERROR] CUDA Out Of Memory!")
        print("Your 4GB VRAM might be heavily fragmented by other running apps.")
        print("Please close background apps using GPU (browsers, discord) and try again.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
