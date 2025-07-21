import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns([
        pl.lit(92).alias("confidence"),
        pl.lit(True).alias("trap"),
        pl.lit(0.8).alias("replay_match"),
        pl.lit(8).alias("score")
    ])