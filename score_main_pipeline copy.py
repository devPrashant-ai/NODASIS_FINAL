from collections import defaultdict
from utils.scoring_utils import aggregate_scores
from utils.operator_utils import detect_operator_cost
from utils.replay_utils import calculate_readiness_score
from utils.mongo_utils import get_symbol_list, get_symbol_data
from tqdm import tqdm  # ✅ added tqdm for progress tracking
import numpy as np

def run_full_scoring(fs_collection, symbols_collection, model_dict):
    predictions = []

    symbol_list = get_symbol_list(symbols_collection)
    
    # ✅ Wrap symbol_list in tqdm for progress bar
    for symbol in tqdm(symbol_list, desc="Scoring Symbols"):
        data = get_symbol_data(fs_collection, symbol)
        if data.empty or len(data) < 30:
            continue  # Skip symbols with insufficient data

        scores = []
        for model_name, model in model_dict.items():
            try:
                result = model.score_bz(data)
                result['model'] = model_name
                scores.append(result)
            except Exception as e:
                print(f"[{model_name}] error on {symbol}: {e}")
                continue

        if not scores:
            continue

        agg = aggregate_scores(scores)

        # Add operator logic
        operator_cost = detect_operator_cost(data)
        ltp = data["rate"].iloc[-1]

        # Readiness calculation
        readiness = calculate_readiness_score(data)

        # Final prediction record
        prediction = {
            "symbol": symbol,
            "operator_cost": round(operator_cost, 2),
            "ltp": round(ltp, 2),
            "confidence": round(agg["confidence"], 2),
            "trap_risk": round(agg["trap_risk"], 3),
            "buy_signal": agg["signal"] == "Buy",
            "signal": agg["signal"],
            "readiness": round(readiness, 2),
            "sector": agg.get("sector", "Unknown")
        }

        predictions.append(prediction)

    return predictions
