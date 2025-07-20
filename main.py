
""" 
NODASIS Pro Lite v2.9 - Starter File (Runtime Safe)

This script allows you to:
1. Run scoring pipeline (safe fallback if duckdb missing)
2. Launch Streamlit dashboard

Usage:
    python main.py
"""

import os
import subprocess
import importlib.util

def module_available(name):
    return importlib.util.find_spec(name) is not None

if module_available("duckdb"):
    print("🔄 Running floor sheet cleaner and scoring pipeline...")
    os.system("python run_scoring_pipeline.py")
else:
    print("⚠️ WARNING: duckdb module not installed. Skipping scoring pipeline.")

print("🚀 Launching Streamlit dashboard at http://localhost:8501 ...")
subprocess.call(["streamlit", "run", "streamlit_app.py"])
