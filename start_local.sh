#!/bin/bash
pip install -r requirements.txt
python run_scoring_pipeline.py
streamlit run streamlit_app.py
