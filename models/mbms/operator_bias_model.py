import polars as pl
from typing import Dict, Union


def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Add fixed BZ scoring metrics (for testing/demo purposes) as new columns.

    Args:
        df: A Polars DataFrame

    Returns:
        The same DataFrame with added columns:
            - confidence: 85
            - trap: False
            - replay_match: 0.7
    """
    return df.with_columns([
        pl.lit(85).alias("confidence"),
        pl.lit(False).alias("trap"),
        pl.lit(0.7).alias("replay_match")
    ])