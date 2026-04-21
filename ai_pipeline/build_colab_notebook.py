import json
import os

NOTEBOOK_PATH = "d:/LAW_WAT/ai_pipeline/juris_hub_colab.ipynb"

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# JurisHub Thailand - AI Content Factory (Colab Version)\n",
            "This notebook runs the entire JurisHub OCR and Pipeline process heavily utilizing Colab GPUs."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 1. Install Dependencies\n",
            "!pip install -q torch transformers einops accelerate pdfplumber pdf2image PyMuPDF\n",
            "!curl -fsSL https://ollama.com/install.sh | sh\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 2. Start Background Ollama Engine\n",
            "import subprocess\n",
            "import threading\n",
            "import time\n",
            "\n",
            "def run_ollama_serve():\n",
            "    subprocess.Popen([\"ollama\", \"serve\"])\n",
            "\n",
            "thread = threading.Thread(target=run_ollama_serve)\n",
            "thread.start()\n",
            "time.sleep(5)\n",
            "print(\"Ollama server running in background...\")\n",
            "\n",
            "# Pull Models (Uncomment or change as needed)\n",
            "!ollama pull gemma:2b\n",
            "!ollama pull deepseek-r1:8b\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 3. Upload Zip Data (Contains data/00_inbox, data/01_raw_text...)\n",
            "from google.colab import files\n",
            "import zipfile\n",
            "import os\n",
            "\n",
            "print(\"Upload your 'law_data.zip' (Must contain the 'data' folder)\")\n",
            "uploaded = files.upload()\n",
            "\n",
            "for filename in uploaded.keys():\n",
            "    print(f\"Extracting {filename}...\")\n",
            "    with zipfile.ZipFile(filename, 'r') as zip_ref:\n",
            "        zip_ref.extractall('.')\n",
            "print(\"Data ready. Folder structure created.\")\n"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Note: Upload the pipeline scripts below.\n",
            "You should map your `ai_pipeline` folder to Colab so it can run the Python scripts."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 4. Upload Pipeline Scripts\n",
            "import os\n",
            "os.makedirs('ai_pipeline', exist_ok=True)\n",
            "print(\"Upload ai_pipeline scripts (step0 to ingest_all)...\")\n",
            "# In practice, users can upload the whole project as a zip\n",
            "# or clone a git repo.\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 5. Run Pipeline\n",
            "!python ai_pipeline/step0_multimodal.py\n",
            "!python ai_pipeline/step1_classifier.py -m gemma:2b\n",
            "!python ai_pipeline/step2_rewriter.py -m deepseek-r1:8b\n",
            "!python ai_pipeline/step3_extractor.py -m deepseek-r1:8b\n",
            "!python ai_pipeline/step4_exam_parser.py -m gemma:2b\n",
            "!python ai_pipeline/ingest_all.py\n"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 6. Export Results\n",
            "import shutil\n",
            "from google.colab import files\n",
            "\n",
            "print(\"Zipping processed data and JS...\")\n",
            "shutil.make_archive('colab_results', 'zip', '.', 'data/database')\n",
            "shutil.make_archive('colab_js', 'zip', '.', 'js')\n",
            "\n",
            "files.download('colab_results.zip')\n",
            "files.download('colab_js.zip')\n",
            "print(\"Download initiated!\")\n"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"gpuType": "T4"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print(f"Build completed: {NOTEBOOK_PATH}")
