#!/bin/bash
cd "$(dirname "$0")"
streamlit run opt/nodasis/streamlit_app.py --server.port 8501
