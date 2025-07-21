import polars as pl

def compute_operator_cost(df):
    return (
        df.group_by("symbol")
        .agg([
            (pl.col("rate") * pl.col("quantity")).sum().alias("weighted_sum"),
            pl.col("quantity").sum().alias("qty_sum")
        ])
        .with_columns(
            (pl.col("weighted_sum") / (pl.col("qty_sum") + 1e-9)).alias("operator_cost")
        )
        .select(["symbol", "operator_cost"])
    )

def compute_ltp(df):
    return (
        df.sort("transaction_date")
        .group_by(["symbol", "transaction_date"])
        .agg(pl.col("rate").last().alias("ltp"))
    )

def compute_trap_score(df):
    return (
        df.group_by(["symbol", "transaction_date"])
        .agg(
            (pl.col("buyer") - pl.col("seller")).abs().mean().alias("trap_score_raw")
        )
        .with_columns(
            (pl.col("trap_score_raw") / 100).clip(0, 1).alias("trap_score")
        )
        .select(["symbol", "transaction_date", "trap_score"])
    )

def compute_readiness(ltp, operator_cost):
    return (
        (1 - (ltp - operator_cost).abs() / (operator_cost + 1)) * 100
    ).clip(0, 100)

def generate_signal_vec(ltp, operator_cost, trap_score):
    return pl.when(trap_score > 0.7).then(pl.lit("Hold")) \
             .when(ltp < operator_cost * 0.95).then(pl.lit("Buy")) \
             .when(ltp > operator_cost * 1.1).then(pl.lit("Sell")) \
             .otherwise(pl.lit("Hold"))

def estimate_days_to_profit(df: pl.DataFrame, threshold=0.10) -> pl.Series:
    estimates = []
    symbols = df["symbol"].to_list()
    ltp_series = df["ltp"].to_list()
    date_series = df["transaction_date"].to_list()

    for i in range(len(df)):
        symbol = symbols[i]
        price = ltp_series[i]
        date = date_series[i]
        target = price * (1 + threshold)

        found = None
        for j in range(i + 1, len(df)):
            if symbols[j] != symbol:
                continue
            if ltp_series[j] >= target:
                found = (date_series[j] - date).days
                break
        estimates.append(found)

    return pl.Series("profit_days_estimate", estimates)

def process_floorsheet(df: pl.DataFrame) -> pl.DataFrame:
    # Ensure proper type casting before using the fields
    df = df.with_columns([
        pl.col("rate").cast(pl.Float64),
        pl.col("quantity").cast(pl.Float64),
        pl.col("buyer").cast(pl.Int64),
        pl.col("seller").cast(pl.Int64),
        pl.col("transaction_date")
    ])

    # Compute necessary fields
    ltp_df = compute_ltp(df)
    op_df = compute_operator_cost(df)
    trap_df = compute_trap_score(df)

    # Merge DataFrames while keeping `rate`
    merged = df.select(["symbol", "transaction_date", "rate"]).join(  # Keep rate from original DF
        ltp_df, on=["symbol", "transaction_date"], how="inner"
    ).join(
        op_df, on="symbol", how="inner"
    ).join(
        trap_df, on=["symbol", "transaction_date"], how="inner"
    )

    # Add readiness and signal
    merged = merged.with_columns([
        compute_readiness(merged["ltp"], merged["operator_cost"]).alias("readiness"),
        generate_signal_vec(merged["ltp"], merged["operator_cost"], merged["trap_score"]).alias("signal")
    ])

    # Estimate profit days
    profit_days = estimate_days_to_profit(merged)
    merged = merged.with_columns([profit_days])
    print(merged)
    return merged.select([
        "symbol", "transaction_date","rate", "signal", "readiness",
        "profit_days_estimate", "ltp", "operator_cost", "trap_score"
    ])
