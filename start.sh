#!/bin/bash

echo "🚀 Starting NODASIS Pro Lite..."

# Step 1: Activate virtual environment
if [ -d "venv" ]; then
    source ./venv/Script/activate
else
    echo "❌ Virtual environment not found. Creating one..."
    py -m venv venv
    source venv/Script/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Step 2: Fix parquet issues (if any)
echo "🔧 Checking and repairing parquet files if needed..."
py fix_parquet_and_run.py || {
    echo "❌ Parquet repair or scoring failed."
    exit 1
}

# Step 3: Launch Streamlit dashboard
echo "📊 Launching dashboard on http://localhost:8501 ..."
streamlit run streamlit_app.py
