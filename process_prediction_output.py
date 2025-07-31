from utils.reason_generator import generate_verdict_reason
from utils.mongo_utils import insert_predictions

def process_and_store_predictions(db, predictions, min_confidence_threshold=0.3):
    """
    Adds final scores and verdicts, while preserving all original fields used in Streamlit and reports.
    """

    final_preds = []

    for p in predictions:
        # --- Normalize Required Fields ---
        p["confidence"] = round(p.get("confidence", 0), 2)
        p["trap_risk"] = round(p.get("trap_risk", 0), 3)
        p["replay_match"] = round(p.get("replay_match", 0.0), 3)
        p["buy_signal"] = False  # default, will be updated below

        # --- Required Defaults (if missing) ---
        p["sector"] = p.get("sector", "Unknown")
        p["operator_cost"] = p.get("operator_cost", 0.0)
        p["ltp"] = p.get("ltp", 0.0)
        p["forecast_label"] = p.get("forecast_label", "N/A")
        p["days_to_profit"] = p.get("days_to_profit", 90)
        p["drl_signal"] = p.get("drl_signal", "Hold")
        p["llm_insight"] = p.get("llm_insight", "")

        # --- Verdict Logic ---
        trap = p["trap_risk"]
        confidence = p["confidence"]
        drl_signal = p["drl_signal"]

        if trap >= 0.7:
            verdict = "Avoid"
        elif confidence >= min_confidence_threshold * 100 and drl_signal == "Buy":
            verdict = "Buy"
        elif drl_signal == "Sell":
            verdict = "Sell"
        else:
            verdict = "Hold"

        # --- Update Final Keys ---
        p["verdict"] = verdict
        p["verdict_reason"] = generate_verdict_reason(p)
        p["buy_signal"] = (verdict == "Buy")

        final_preds.append(p)

    # --- Confidence Filter ---
    final_filtered = [x for x in final_preds if x["confidence"] >= min_confidence_threshold * 100]

    print(f"📥 Inserting {len(final_filtered)} predictions into DB (confidence ≥ {min_confidence_threshold*100}%)...")
    if not final_filtered:
        return print ("No data to insert")
    insert_predictions(db, final_filtered)
