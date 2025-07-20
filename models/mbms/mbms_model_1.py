import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Computes MBMS trading signals with:
    - Confidence score, trap filtering, pattern matching, and buy/hold signals.
    """
    # Ensure 'trap_score' column exists
    if "trap_score" not in df.columns:
        df = df.with_columns(pl.lit(0).alias("trap_score"))
    return (
        df
        .with_columns(
            # Confidence score (safe division)
            ((pl.col("ltp") - pl.col("operator_cost")) / pl.col("ltp").replace(0, 1e-9))
            .alias("mbms_confidence"),
            # Trap filter (ternary condition)
            (pl.when(pl.col("trap_score") > 0.7)
              .then(pl.lit(0))
              .otherwise(pl.lit(1))
              .alias("trap_filter")),
            # Fake pattern match (modulo operation, ensure boolean)
            ((pl.col("ltp") % 100 < 10).cast(bool).alias("replay_match"))
        )
        .with_columns(
            # Buy signal (compound condition)
            (pl.when(
                (pl.col("mbms_confidence") > 0.05) & 
                (pl.col("trap_filter") == 1) & 
                (pl.col("replay_match") == True)
            )
            .then(pl.lit("Buy"))
            .otherwise(pl.lit("Hold"))
            .alias("mbms_signal"))
        )
    )