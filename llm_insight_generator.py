# llm_insight_generator.py

def generate_llm_comment(pred):
    """
    Generate a simple, readable insight based on key prediction fields.
    """

    symbol = pred.get("symbol", "N/A")
    oc = pred.get("operator_cost", 0)
    ltp = pred.get("ltp", 0)
    conf = pred.get("confidence", 0)
    trap = pred.get("trap_risk", 0)
    drl = pred.get("drl_signal", "Hold")
    days = pred.get("days_to_profit", None)
    forecast = pred.get("forecast_label", "N/A")

    comment = f"{symbol}: Operator cost at Rs. {oc}, LTP is Rs. {ltp}. "

    if conf > 85:
        comment += "Very strong model confidence. "
    elif conf > 65:
        comment += "Moderate confidence. "
    else:
        comment += "Low model confidence. "

    if trap > 0.5:
        comment += "⚠️ High trap risk detected. "
    else:
        comment += "🟢 Trap risk is low. "

    if drl == "Buy":
        comment += "DRL also recommends buying. "
    elif drl == "Sell":
        comment += "DRL recommends exiting. "

    if days:
        comment += f"Estimated {days} days to 10% gain ({forecast})."

    return comment
