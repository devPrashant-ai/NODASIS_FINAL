import polars as pl

def train_drl_model(df: pl.DataFrame) -> pl.DataFrame:
    """
    Simulates DRL scoring:
    - Higher reward when LTP is close to operator_cost AND trap_score is low.
    - Updates readiness based on reward.
    """
    # Step 1: create drl_reward
    df = df.with_columns(
        (((1 - pl.col("trap_score")) * 100 - abs(pl.col("ltp") - pl.col("operator_cost")) * 0.05)
         .alias("drl_reward"))
    )
    
    # Step 2: create drl_signal based on drl_reward
    df = df.with_columns(
        pl.when(pl.col("drl_reward") > 60)
          .then(pl.lit("Buy"))
          .when(pl.col("drl_reward") > 40)
          .then(pl.lit("Hold"))
          .otherwise(pl.lit("Sell"))
          .alias("drl_signal")
    )
    
    # Step 3: update readiness if it exists
    if "readiness" in df.columns:
        df = df.with_columns(
            (pl.col("readiness") + pl.col("drl_reward") * 0.05).alias("readiness")
        )
    
    return df
