import polars as pl
from models.mbms import trap_aware_model, replay_aligned_model, drl_enhanced_model

def score_bz(df: pl.DataFrame) -> dict[str, float]:
    """
    Evaluate DataFrame against multiple MBMS models and return the highest-confidence result.
    
    Args:
        df: Input DataFrame containing required features for all models
        
    Returns:
        Dictionary with the best model's results (highest confidence score)
        Example: {'confidence': 0.95, 'trap': False, ...}
    """
    # Get scores from all models (assumes each returns a dict)
    scores = [
        trap_aware_model.score(df),
        replay_aligned_model.score(df),
        drl_enhanced_model.score(df)
    ]
    
    # Find result with maximum confidence
    return max(scores, key=lambda x: x['confidence'])