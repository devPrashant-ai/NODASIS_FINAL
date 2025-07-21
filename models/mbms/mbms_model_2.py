import polars as pl

def score_bz(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculate MBMS confidence and generate trading signals.
    - Confidence: 1 - (trap_score * 0.8)
    - Signal: 'Buy' if confidence > 0.6, else 'Sell'
    
    Args:
        df: Input DataFrame containing at least 'trap_score' column
        
    Returns:
        DataFrame with two new columns:
        - mbms_confidence: Calculated confidence score (float)
        - mbms_signal: Trading signal ('Buy' or 'Sell')
    """
    return df.with_columns(
        # Calculate confidence (vectorized operation)
        (1 - (pl.col("trap_score") * 0.8)).alias("mbms_confidence"),
        
        # Generate signal (ternary expression)
        pl.when(pl.col("mbms_confidence") > 0.6)
          .then("Buy")
          .otherwise("Sell")
          .alias("mbms_signal")
    )