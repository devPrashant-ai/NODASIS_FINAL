from collections import defaultdict
from utils.scoring_utils import aggregate_scores
from utils.operator_utils import detect_operator_cost
from utils.replay_utils import calculate_readiness_score
from utils.mongo_utils import get_symbol_list, get_symbol_data
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from replay_engine import replay_signal_history

def process_symbol(symbol, fs_collection, model_dict):
    data = get_symbol_data(fs_collection, symbol)
    if data.empty or len(data) < 30:
        return None  # Skip symbols with insufficient data

    scores = []
    for model_name, model in model_dict.items():
        try:
            result = model.score_bz(data)
            if not isinstance(result, dict):
                print(f"[{model_name}] returned non-dict result on {symbol}")
                continue
            result['model'] = model_name
            scores.append(result)
        except Exception as e:
            print(f"[{model_name}] error on {symbol}: {e}")
            continue

    if not scores:
        return None

    agg = aggregate_scores(scores)
    if not isinstance(agg, dict):
        print(f"aggregate_scores returned non-dict for {symbol}")
        return None

    operator_cost = detect_operator_cost(data)
    ltp = data["rate"].iloc[-1]
    readiness = calculate_readiness_score(data)

    # Calculate replay_match using replay_signal_history
    replay_data = replay_signal_history(symbol, fs_collection)
    print(replay_data[-1]["avg_cost"])
    replay_match = 0
    if replay_data:
        latest_avg_cost = replay_data[-1]["avg_cost"]
        # If latest avg_cost is within 1% of ltp, consider it a match
        if abs(latest_avg_cost - ltp) / ltp < 0.01:
            replay_match = 1

    return {
        "symbol": symbol,
        "operator_cost": round(operator_cost, 2),
        "ltp": round(ltp, 2),
        "confidence": round(agg.get("confidence", 0), 2),
        "trap_risk": round(agg.get("trap_risk", 0), 3),
        "buy_signal": agg.get("signal", "") == "Buy",
        "signal": agg.get("signal", ""),
        "readiness": round(readiness, 2),
        "sector": agg.get("sector", "Unknown"),
        "replay_match": replay_match
    }

def run_full_scoring(fs_collection, symbols_collection, model_dict, max_workers=8):
    predictions = []
    symbol_list = get_symbol_list(symbols_collection)
    print(symbol_list)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_symbol, symbol, fs_collection, model_dict): symbol
            for symbol in symbol_list
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Scoring in parallel"):
            result = future.result()
            if result:
                predictions.append(result)

    return predictions
