# utils/reason_generator.py

def generate_verdict_reason(pred):
    reasons = []

    # Confidence
    if pred["confidence"] >= 75:
        reasons.append("High model confidence")
    elif pred["confidence"] >= 55:
        reasons.append("Moderate confidence")
    else:
        reasons.append("Low model confidence")

    # Trap Risk
    if pred["trap_risk"] >= 0.7:
        reasons.append("High trap risk — avoid")
    elif pred["trap_risk"] >= 0.4:
        reasons.append("Moderate trap risk")
    else:
        reasons.append("Low trap risk")

    # DRL Signal
    if pred.get("drl_signal") == "Buy":
        reasons.append("DRL supports Buy")
    elif pred.get("drl_signal") == "Sell":
        reasons.append("DRL recommends exit")
    elif pred.get("drl_signal") == "Hold":
        reasons.append("DRL suggests caution")

    # Operator Cost vs LTP
    if pred["ltp"] < pred["operator_cost"] * 0.95:
        reasons.append("LTP is significantly below operator cost")
    elif pred["ltp"] > pred["operator_cost"] * 1.1:
        reasons.append("LTP is above operator range — possible exit")

    # Forecast Label
    if "forecast_label" in pred:
        reasons.append(f"Forecast: {pred['forecast_label']}")

    # Readiness
    if pred.get("readiness", 0) > 0.85:
        reasons.append("Symbol is fully ready for entry")
    elif pred.get("readiness", 0) < 0.2:
        reasons.append("Still in early setup phase")

    return " | ".join(reasons)
