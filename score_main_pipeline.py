import os
from datetime import datetime, timedelta
from pathlib import Path
import polars as pl

from db_config import get_mongo_client
from helpers.generate_predictions_from_floorsheet import process_floorsheet

# Set project path
PROJECT_ROOT = Path(__file__).resolve().parent
parquet_out_dir = PROJECT_ROOT / "data" / "parquet"
os.makedirs(parquet_out_dir, exist_ok=True)

def generate_predictions():
    try:
        client = get_mongo_client()
        db = client['admin']
        records_cursor = db.scraped_data.find({}, {"_id": 0})
        records = list(records_cursor)
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB or fetch records: {e}")
        return

    if not records:
        print("⚠️ No records found in MongoDB.")
        client.close()
        return

    try:
        df = pl.DataFrame(records)

        # Directly parse the transaction_date column to pl.Date
        df = df.with_columns([
            pl.col("transaction_date").str.strptime(pl.Date, "%Y-%m-%d").alias("transaction_date"),
            pl.col("rate").cast(pl.Float64),
            pl.col("quantity").cast(pl.Float64),
            pl.col("buyer").cast(pl.Int64),
            pl.col("seller").cast(pl.Int64),
            pl.col("symbol").cast(pl.String)
        ])
    except Exception as e:
        print(f"❌ Error parsing records into Polars DataFrame: {e}")
        client.close()
        return

    if 'symbol' not in df.columns or 'transaction_date' not in df.columns:
        print("❌ Required columns missing in data.")
        client.close()
        return

    today = datetime.today().date()
    seven_days_ago = today - timedelta(days=5)

    try:
        # Safely filter the data by the transaction_date
        df = df.filter(pl.col("transaction_date") <= pl.lit(seven_days_ago).cast(pl.Date))
    except Exception as e:
        print(f"❌ Error filtering data by date: {e}")
        client.close()
        return

    if df.is_empty():
        print("⚠️ No data before 5 days ago.")
        client.close()
        return

    success_count = 0
    fail_count = 0

    for symbol in df['symbol'].unique():
        try:
            sdf = df.filter(pl.col("symbol") == symbol)
            if sdf.height < 2:
                continue

            processed = process_floorsheet(sdf)

            latest = processed.sort("transaction_date").select([
                "symbol", "transaction_date", "signal", "readiness",
                "profit_days_estimate", "ltp", "operator_cost", "trap_score"
            ]).tail(1)

            out_path = parquet_out_dir / f"{symbol}.parquet"
            latest.write_parquet(str(out_path))
            success_count += 1
        except Exception as e:
            print(f"⚠️ Error processing symbol {symbol}: {e}")
            fail_count += 1

    print(f"✅ Saved {success_count} symbols | ❌ Failed {fail_count} symbols.")
    client.close()

if __name__ == "__main__":
    generate_predictions()
