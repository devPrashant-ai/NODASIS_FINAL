# train_drl_batch.py

def apply_drl_signal(pred):
    """
    Apply a lightweight DRL overlay based on:
    - Confidence
    - Trap Risk
    - Readiness
    - Price gap from operator cost
    """

    confidence = pred.get("confidence", 0)
    trap = pred.get("trap_risk", 0)
    readiness = pred.get("readiness", 0)
    operator_cost = pred.get("operator_cost", 0)
    ltp = pred.get("ltp", 0)

    if ltp == 0 or operator_cost == 0:
        return {"drl_signal": "Hold"}

    gap_pct = (operator_cost - ltp) / operator_cost
    score = confidence * readiness - trap * 100 + gap_pct * 100

    # Simple policy logic (can be replaced by real model)
    if score > 80:
        signal = "Buy"
    elif score < 40:
        signal = "Sell"
    else:
        signal = "Hold"

    return {
        "drl_signal": signal
    }
