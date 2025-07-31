# forecast_engine.py

import numpy as np

def generate_forecast(pred):
    """
    Estimate days to 10–20% profit based on:
    - Gap between LTP and operator cost
    - Readiness %
    - Trap Risk
    - Confidence
    """

    operator_cost = pred.get("operator_cost", 0)
    ltp = pred.get("ltp", 0)
    readiness = pred.get("readiness", 0)
    confidence = pred.get("confidence", 0)
    trap = pred.get("trap_risk", 0)

    if operator_cost == 0 or ltp == 0 or ltp >= operator_cost:
        return {
            "days_to_profit": None,
            "forecast_label": "Late Entry",
        }

    gap_pct = (operator_cost - ltp) / operator_cost
    gain_target = 0.10  # 10% target profit

    if readiness <= 0:
        readiness = 0.1  # avoid divide-by-zero

    base_days = (gain_target / (gap_pct + 1e-6)) * (1 / readiness)

    # Adjust for trap and confidence
    trap_penalty = 1 + trap * 2
    conf_boost = 1 - (confidence / 200)

    estimated_days = base_days * trap_penalty * conf_boost
    estimated_days = np.clip(estimated_days, 1, 30)
    print("--------------------------------------")
    print(estimated_days)

    # Forecast Label
    if estimated_days <= 5:
        label = "Best Entry"
    elif estimated_days <= 10:
        label = "Moderate Entry"
    else:
        label = "Late Entry"

    return {
        "days_to_profit": round(estimated_days, 1),
        "forecast_label": label,
    }
