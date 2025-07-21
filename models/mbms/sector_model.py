import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add fixed BZ scoring metrics (for testing/demo purposes) as new columns.

    Args:
        df: A Polars DataFrame

    Returns:
        The same DataFrame with added columns:
            - confidence: 81
            - trap: True
            - replay_match: 0.6
    """
    return df.with_columns([
        pl.lit(81).alias("confidence"),
        pl.lit(True).alias("trap"),
        pl.lit(0.6).alias("replay_match")
    ])