def replay_signal_history(symbol, db):
    trades = list(db.find({"symbol": symbol}))
    # Convert transaction_date to datetime if it's a string for proper sorting
    for trade in trades:
        if isinstance(trade.get("transaction_date"), str):
            from datetime import datetime
            trade["transaction_date"] = datetime.fromisoformat(trade["transaction_date"])

    trades.sort(key=lambda x: x["transaction_date"])

    replay = []
    avg_cost = 0
    total_qty = 0
    for trade in trades:
        rate = trade["rate"]
        qty = trade["quantity"]
        total_qty += qty
        avg_cost = ((avg_cost * (total_qty - qty)) + (rate * qty)) / total_qty
        # Format transaction_date back to 'YYYY-MM-DD' string format
        time_str = trade["transaction_date"].strftime('%Y-%m-%d') if hasattr(trade["transaction_date"], 'strftime') else trade["transaction_date"]
        replay.append({"time": time_str, "avg_cost": round(avg_cost, 2)})

    return replay
