from mbms_loader import load_all_models
from utils.feature_engineering import generate_features
from forecast_engine import add_forecast_columns
from llm_insight_generator import generate_llm_insight

def run_full_pipeline(db):
    records = list(db["floorsheet"].find())
    if not records:
        print("❌ No floorsheet data in DB.")
        return

    features_df = generate_features(records)
    models = load_all_models()

    predictions = []
    for _, row in features_df.iterrows():
        symbol = row["symbol"]
        inputs = row.to_dict()
        scores = [model.score_bz(inputs) for model in models.get(symbol, [])]
        avg_score = sum(score["confidence"] for score in scores) / len(scores) if scores else 0
        buy_signal = any(score["buy_signal"] for score in scores)

        prediction = {
            "symbol": symbol,
            "ltp": inputs["ltp"],
            "operator_cost": inputs.get("operator_cost"),
            "confidence": round(avg_score, 2),
            "trap_risk": max(score.get("trap_risk", 0) for score in scores) if scores else 0,
            "buy_signal": buy_signal,
            "readiness": inputs.get("readiness", 0),
            "days_to_profit": inputs.get("days_to_profit", -1),
        }

        add_forecast_columns(prediction, inputs)
        prediction["llm_insight"] = generate_llm_insight(prediction)
        predictions.append(prediction)

    db["predictions"].delete_many({})
    db["predictions"].insert_many(predictions)
