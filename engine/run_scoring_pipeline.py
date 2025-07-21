
import duckdb
import pandas as pd
import os

def generate_predictions(duckdb_path, output_dir):
    con = duckdb.connect(duckdb_path)
    df = con.execute("SELECT symbol, transaction_date, AVG(rate) as avg_rate, SUM(quantity) as total_qty FROM floorsheet GROUP BY symbol, transaction_date").df()
    os.makedirs(output_dir, exist_ok=True)
    for symbol in df["symbol"].unique():
        sdf = df[df["symbol"] == symbol].copy()
        sdf["readiness"] = (sdf["avg_rate"] / sdf["avg_rate"].max()) * 100
        sdf["signal"] = ["Buy" if r > 80 else "Hold" for r in sdf["readiness"]]
        sdf.to_parquet(os.path.join(output_dir, f"{symbol}.parquet"))
    con.close()
