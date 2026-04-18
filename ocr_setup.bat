@echo off
echo ==========================================
echo JurisHub OCR Environment Setup (Windows)
echo Target: RTX 3050 (4GB VRAM)
echo ==========================================

echo [1] Creating Conda Environment (jurishub-ocr) with Python 3.10...
call conda create -n jurishub-ocr python=3.10 -y

echo [2] Activating Environment...
call conda activate jurishub-ocr

echo [3] Installing PyTorch with CUDA 12.1 support...
call pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

echo [4] Installing Dependencies for GOT-OCR2.0...
call pip install transformers accelerate tiktoken verovio

echo [5] Installing pdf2image for PDF processing...
call pip install pdf2image Pillow

echo ==========================================
echo Setup Complete!
echo Please don't forget to install Poppler for Windows and add it to your PATH
echo for pdf2image to work correctly.
echo ==========================================
pause
