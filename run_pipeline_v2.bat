@echo off
chcp 65001 >nul
echo ==============================================================
echo JurisHub Thailand AI Factory (Pipeline v2 with Multi-OCR)
echo ==============================================================
echo.

rem --- CONFIGURATION ---
set OCR_METHOD=easyocr
set ROUTER_MODEL=gemma:2b
set REASONER_MODEL=deepseek-r1:8b
rem ---------------------

echo [Config] OCR Method: %OCR_METHOD%
echo [Config] Router Model: %ROUTER_MODEL%
echo [Config] Reasoner Model: %REASONER_MODEL%
echo.

echo ==============================================================
echo [Step 0] Pre-processing with OCR (%OCR_METHOD%)
echo ==============================================================
python ai_pipeline\step0_multimodal_v2.py --inbox --method %OCR_METHOD%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Step 0 failed!
    pause
    exit /b 1
)

echo.
echo ==============================================================
echo [Step 0.5] Checking Ollama Service...
echo ==============================================================
curl -s http://localhost:11434/api/tags >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not running. Please open Ollama app first!
    pause
    exit /b 1
)
echo ✅ Ollama is running
echo.

echo ==============================================================
echo [STEP 1] Classifier (Using: %ROUTER_MODEL%)
echo ==============================================================
python ai_pipeline\step1_classifier.py -m %ROUTER_MODEL%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Step 1 completed with warnings
)
echo.

echo ==============================================================
echo [STEP 1.5] OCR Corrector (ThaiLLM API)
echo ==============================================================
echo ⏭️ ขั้นตอนนี้จำเป็นต้องใช้ ThaiLLM API
set /p RUN_OCR_CORRECTOR="ต้องการรัน OCR Corrector หรือไม่? (y/n): "
if /i "%RUN_OCR_CORRECTOR%"=="y" (
    python ai_pipeline\step1_5_ocr_corrector_api.py
)
echo.

echo ==============================================================
echo [STEP 2] Rewriter (Using: %REASONER_MODEL%)
echo ==============================================================
python ai_pipeline\step2_rewriter_api.py -m %REASONER_MODEL%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Step 2 completed with warnings
)
echo.

echo ==============================================================
echo [STEP 3] Article Extractor (Using: %REASONER_MODEL%)
echo ==============================================================
python ai_pipeline\step3_extractor_api.py -m %REASONER_MODEL%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Step 3 completed with warnings
)
echo.

echo ==============================================================
echo [STEP 4] Exam Parser (Using: %ROUTER_MODEL%)
echo ==============================================================
python ai_pipeline\step4_exam_parser_api.py -m %ROUTER_MODEL%
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Step 4 completed with warnings
)
echo.

echo ==============================================================
echo [STEP 5] Web Ingestor
echo ==============================================================
python ai_pipeline\ingest_all.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Step 5 failed!
    pause
    exit /b 1
)
echo.

echo ==============================================================
echo ✅ Process Completed Successfully!
echo 🌐 Data has been ingested and your website is ready!
echo ==============================================================
echo.
echo 📊 Summary:
echo    - OCR Method: %OCR_METHOD%
echo    - Output: data/01_raw_text/, js/content-data.js
echo.
pause
