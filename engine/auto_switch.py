
import pandas as pd

def auto_switch_strategy(df, history_dict):
    # history_dict: {symbol: {model_name: [wins, total]}}
    model_performance = {}

    for model_name in df['active_model'].unique():
        df_model = df[df['active_model'] == model_name]
        for symbol in df_model['symbol'].unique():
            past = history_dict.get(symbol, {}).get(model_name, [0, 1])
            recent_win = ((df_model['signal'] == 'Buy') & (df_model['ltp'] < df_model['operator_cost'])).sum()
            history_dict.setdefault(symbol, {})[model_name] = [
                past[0] + recent_win,
                past[1] + len(df_model[df_model['symbol'] == symbol])
            ]

    # Select best model per symbol
    best_model = {}
    for symbol, models in history_dict.items():
        best = max(models.items(), key=lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0)
        best_model[symbol] = best[0]

    # Apply model decision
    df['strategy_selected'] = df.apply(lambda row: 'Buy' if row['active_model'] == best_model.get(row['symbol'], '') else 'Hold', axis=1)
    return df, history_dict
