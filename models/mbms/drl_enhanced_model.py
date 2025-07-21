import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add fixed BZ scoring metrics (for testing/demo purposes) as new columns.

    Args:
        df: A Polars DataFrame

    Returns:
        The same DataFrame with added columns:
            - confidence: 95
            - trap: False
            - replay_match: 0.95
    """
    return df.with_columns([
        pl.lit(95).alias("confidence"),
        pl.lit(False).alias("trap"),
        pl.lit(0.95).alias("replay_match")
    ])
