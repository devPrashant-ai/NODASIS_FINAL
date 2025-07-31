# run_scoring_pipeline.py

import time
from mongo_connector import get_mongo_connection
from process_prediction_output import process_and_store_predictions
from score_main_pipeline import run_full_scoring
from forecast_engine import generate_forecast
from train_drl_batch import apply_drl_signal
from llm_insight_generator import generate_llm_comment
from mbms_loader import load_all_models

def main():
    print("🔄 Starting NODASIS Scoring Pipeline...")

    # Connect to MongoDB
    db = get_mongo_connection()
    fs_collection = db["scraped_data"]
    companies = db['companies']

    # Load models
    print("📦 Loading MBMS models...")
    model_dict = load_all_models()

    # Run MBMS scoring logic
    print("🧠 Running MBMS scoring per symbol...")
    predictions = run_full_scoring(fs_collection, companies, model_dict)

    # Run Forecast logic
    print("📈 Generating Days to Profit forecast...")
    for p in predictions:
        forecast = generate_forecast(p)
        p.update(forecast)

    # Apply DRL signal logic
    print("🎮 Applying DRL signal overlay...")
    for p in predictions:
        drl_result = apply_drl_signal(p)
        p.update(drl_result)

    # Generate LLM-style commentary
    print("💬 Generating LLM commentary...")
    for p in predictions:
        p["llm_insight"] = generate_llm_comment(p)

    # Store predictions in MongoDB
    print("🗄️ Inserting predictions to MongoDB...")
    process_and_store_predictions(db, predictions,.3)

    print(f"✅ Done. {len(predictions)} symbols scored and stored.")

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"⏱️ Execution Time: {round(end - start, 2)} seconds")
