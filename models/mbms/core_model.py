import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate BZ scoring metrics using Polars and attach them to each row."""
    # Ensure 'rate' column exists
    if "rate" not in df.columns:
        df = df.with_columns(pl.lit(0).alias("rate"))
    operator_cost = df["rate"].mean()
    ltp = df["rate"].tail(1).item()

    if operator_cost == 0:
        readiness = 0.0
    else:
        readiness = 100 - (abs(ltp - operator_cost) / operator_cost) * 100

    return df.with_columns([
        pl.lit(round(operator_cost, 2)).alias("operator_cost"),
        pl.lit(round(ltp, 2)).alias("ltp"),
        pl.lit(round(readiness, 2)).alias("readiness")
    ])
