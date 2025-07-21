import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Computes MBMS trading signals with:
    - Confidence score, trap filtering, pattern matching, and buy/hold signals.
    """
    return (
        df
        .with_columns(
            # Confidence score (safe division)
            ((pl.col("ltp") - pl.col("operator_cost")) / pl.col("ltp").replace(0, 1e-9))
            .alias("mbms_confidence"),
            
            # Trap filter (ternary condition)
            (pl.when(pl.col("trap_score") > 0.7)
              .then(0)
              .otherwise(1)
              .alias("trap_filter")),
            
            # Fake pattern match (modulo operation)
            (pl.col("ltp") % 100 < 10).alias("replay_match")
        )
        .with_columns(
            # Buy signal (compound condition)
            (pl.when(
                (pl.col("mbms_confidence") > 0.05) & 
                (pl.col("trap_filter") == 1) & 
                (pl.col("replay_match"))
              .then("Buy")
              .otherwise("Hold")
              .alias("mbms_signal"))
    )))