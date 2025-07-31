# utils/forecast_utils.py

import numpy as np

def compute_gap_pct(operator_cost, ltp):
    """
    Calculate the gap percentage between operator cost and current price.
    """
    if operator_cost == 0:
        return 0.0
    return (operator_cost - ltp) / operator_cost

def estimate_days_to_profit(gap_pct, readiness, trap, confidence):
    """
    Estimate the number of days to reach 10% profit, adjusted for risk.
    """
    if readiness <= 0:
        readiness = 0.05

    base_days = (0.10 / (gap_pct + 1e-6)) * (1 / readiness)
    trap_penalty = 1 + trap * 2
    conf_boost = 1 - (confidence / 200)

    days = base_days * trap_penalty * conf_boost
    return np.clip(days, 1, 30)
