
import polars as pl

def auto_switch_strategy(df, history_dict):
    # history_dict: {symbol: {model_name: [wins, total]}}
    model_performance = {}

    # Get unique models and symbols
    models = df.select('active_model').unique().to_series().to_list()
    symbols = df.select('symbol').unique().to_series().to_list()

    for model_name in models:
        df_model = df.filter(pl.col('active_model') == model_name)
        for symbol in symbols:
            df_symbol = df_model.filter(pl.col('symbol') == symbol)
            past = history_dict.get(symbol, {}).get(model_name, [0, 1])
            recent_win = ((df_symbol['signal'] == 'Buy') & (df_symbol['ltp'] < df_symbol['operator_cost'])).sum()
            history_dict.setdefault(symbol, {})[model_name] = [
                past[0] + recent_win,
                past[1] + df_symbol.height
            ]

    # Select best model per symbol
    best_model = {}
    for symbol, models in history_dict.items():
        best = max(models.items(), key=lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0)
        best_model[symbol] = best[0]

    # Apply model decision using Polars
    df = df.with_columns([
        pl.when(pl.col('active_model') == pl.col('symbol').map_elements(lambda s: best_model.get(s, ''), return_dtype=pl.Utf8))
        .then(pl.lit('Buy'))
        .otherwise(pl.lit('Hold'))
        .alias('strategy_selected')
    ])
    return df, history_dict
