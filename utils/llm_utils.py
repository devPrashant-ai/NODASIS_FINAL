# utils/llm_utils.py

def format_llm_insight(pred):
    """
    Return a full paragraph-style explanation using prediction fields.
    """
    symbol = pred.get("symbol", "N/A")
    oc = pred.get("operator_cost", 0)
    ltp = pred.get("ltp", 0)
    conf = pred.get("confidence", 0)
    trap = pred.get("trap_risk", 0)
    days = pred.get("days_to_profit", None)
    label = pred.get("forecast_label", "N/A")
    drl = pred.get("drl_signal", "Hold")

    parts = [
        f"Symbol {symbol} is currently trading at Rs. {ltp} with operator cost estimated at Rs. {oc}.",
        f"The model confidence is {conf}%.",
        "Trap risk is high." if trap > 0.5 else "Trap risk is low.",
        f"Estimated {days} days to 10% profit ({label})" if days else "Forecast unavailable.",
        f"DRL agent suggests to {drl} this symbol."
    ]

    return " ".join(parts)
# "Symbol NABIL is currently trading at Rs. 786 with operator cost estimated at Rs. 825. The model confidence is 91%. Trap risk is low. Estimated 4.2 days to 10% profit (Best Entry). DRL agent suggests to Buy this symbol."