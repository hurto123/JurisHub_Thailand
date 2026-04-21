@echo off
chcp 65001 >nul
echo ==============================================================
echo JurisHub OCR Comparison Tool
echo ==============================================================
echo.

REM Check if file is provided
if "%~1"=="" (
    echo การใช้งาน: run_ocr_comparison.bat [path\to\file.pdf]
    echo.
    echo ตัวอย่าง:
    echo   run_ocr_comparison.bat data\00_inbox\document.pdf
    echo   run_ocr_comparison.bat "C:\Users\Name\Documents\scan.jpg"
    echo.
    pause
    exit /b 1
)

set "INPUT_FILE=%~1"

REM Check if file exists
if not exist "%INPUT_FILE%" (
    echo ❌ ไม่พบไฟล์: %INPUT_FILE%
    pause
    exit /b 1
)

echo 📄 ไฟล์ที่เลือก: %INPUT_FILE%
echo.
echo ==============================================================
echo 🔍 กำลังเปรียบเทียบ OCR Methods...
echo ==============================================================
echo.

python ai_pipeline\ocr_comparison.py --input "%INPUT_FILE%" --method both

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ เกิดข้อผิดพลาดในการประมวลผล
    pause
    exit /b 1
)

echo.
echo ==============================================================
echo ✅ เสร็จสิ้น!
echo 📁 ผลลัพธ์อยู่ใน: data\ocr_comparison\
echo ==============================================================
echo.
pause
