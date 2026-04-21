@echo off
chcp 65001 >nul
echo ==============================================================
echo JurisHub Thailand AI Factory (Multimodal Pipeline)
echo ==============================================================
echo.

rem --- CONFIGURATION ---
set ROUTER_MODEL=gemma2:2b
set REASONER_MODEL=deepseek-r1:8b
rem ---------------------

echo [Step 0] Pre-processing Multimodal Files (PDF/Images)...
echo --------------------------------------------------------------
python ai_pipeline/step0_multimodal.py

echo.
echo [Step 0.5] Checking Ollama Service...
curl -s http://localhost:11434/api/tags >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not running. Please open Ollama app first!
    pause
    exit /b
)

echo.
echo --------------------------------------------------------------
echo [STEP 1] Classifier (Using: %ROUTER_MODEL%)
echo Sorting files...
echo --------------------------------------------------------------
python ai_pipeline/step1_classifier.py -m %ROUTER_MODEL%

echo.
echo --------------------------------------------------------------
echo [STEP 2] Rewriter (Using: %REASONER_MODEL%)
echo Paraphrasing content...
echo --------------------------------------------------------------
python ai_pipeline/step2_rewriter.py -m %REASONER_MODEL%

echo.
echo --------------------------------------------------------------
echo [STEP 3] Article Extractor (Using: %REASONER_MODEL%)
echo Summarizing legal articles...
echo --------------------------------------------------------------
python ai_pipeline/step3_extractor.py -m %REASONER_MODEL%

echo.
echo --------------------------------------------------------------
echo [STEP 4] Exam Parser (Using: %ROUTER_MODEL%)
echo Extracting questions and answers...
echo --------------------------------------------------------------
python ai_pipeline/step4_exam_parser.py -m %ROUTER_MODEL%

echo.
echo --------------------------------------------------------------
echo [STEP 5] Web Ingestor
echo Updating website database and building final JS files...
echo --------------------------------------------------------------
python ai_pipeline/ingest_all.py

echo.
echo --------------------------------------------------------------
echo Process Completed Successfully!
echo Data has been ingested and your website is ready to use!
echo --------------------------------------------------------------
echo.
pause
