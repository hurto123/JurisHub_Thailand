import multiprocessing
import subprocess
import sys
import time

def run_task_a():
    """Task A: Run Ollama Summarizer (GPU Intenstive)"""
    print("▶️ [Task A] Starting Ollama Summarizer Process...")
    # Using subprocess to call the other script guarantees separate process space
    process = subprocess.Popen([sys.executable, "ollama_summarizer.py"])
    process.communicate()
    print("⏹️ [Task A] Ollama Summarizer Finished.")

def run_task_b():
    """Task B: Run JSON/OCR Builder (CPU Intensive - Tesseract)"""
    print("▶️ [Task B] Starting JSON & OCR Builder Process...")
    # Tesseract OCR runs primarily on CPU, safe to run alongside Ollama
    process = subprocess.Popen([sys.executable, "json_builder.py"])
    process.communicate()
    print("⏹️ [Task B] JSON & OCR Builder Finished.")

if __name__ == "__main__":
    print("=================================================")
    print("🚀 Starting JurisHub Parallel Processing Pipeline")
    print("System constrained for RTX 3050 (4GB VRAM)")
    print("=================================================")
    
    # Create two distinct processes to prevent GIL locking and separate resource usage
    p1 = multiprocessing.Process(target=run_task_a)
    p2 = multiprocessing.Process(target=run_task_b)

    # Start both
    start_time = time.time()
    p1.start()
    p2.start()

    # Wait for both to finish
    p1.join()
    p2.join()

    end_time = time.time()
    print("=================================================")
    print(f"🎉 All Parallel Tasks Completed in {end_time - start_time:.2f} seconds.")
    print("=================================================")
