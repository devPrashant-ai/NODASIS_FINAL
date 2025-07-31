import numpy as np

def calculate_final_scores(df):
    df = df.copy()

    if "confidence" in df.columns:
        max_conf = df["confidence"].max()
        df["confidence"] = df["confidence"].apply(lambda x: round(x, 2))
        if max_conf > 0:
            df["confidence_norm"] = df["confidence"] / max_conf
        else:
            df["confidence_norm"] = 0.0
    else:
        df["confidence"] = 0
        df["confidence_norm"] = 0.0

    df["readiness"] = df["days_to_profit"].apply(
        lambda x: round(100 / x, 2) if x and x > 0 else 0
    )

    def buy_logic(row):
        trap_risk = row["trap_risk"] if "trap_risk" in row else 1.0
        replay_match = row["replay_match"] if "replay_match" in row else 0
        forecast_label = row["forecast_label"].lower() if "forecast_label" in row and isinstance(row["forecast_label"], str) else ""
        drl_signal = row["drl_signal"].lower() if "drl_signal" in row and isinstance(row["drl_signal"], str) else ""

        return (
            row["confidence"] > 65 and
            trap_risk < 0.25 and
            replay_match == 1 and
            forecast_label != "late entry" and
            drl_signal == "buy"
        )

    df["buy_signal"] = df.apply(buy_logic, axis=1)

    return df
