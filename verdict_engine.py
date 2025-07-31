def compute_verdict(row):
    if row["buy_signal"]:
        return "Buy"
    elif row["trap_risk"] > 0.35 or row["forecast_label"].lower() == "late entry":
        return "Sell"
    elif row["confidence"] < 60 or row["drl_signal"].lower() == "hold":
        return "Hold"
    else:
        return "Avoid"
