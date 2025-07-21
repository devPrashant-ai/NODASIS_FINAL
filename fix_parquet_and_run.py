import os
import json
import polars as pl
import duckdb
from pathlib import Path
import pyarrow.parquet as pq

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent
PARQUET_DIR = PROJECT_ROOT / "data" / "parquet"
JSONL_SOURCE = PROJECT_ROOT / "data" / "floorsheet_sample.jsonl"
JSON_SOURCE = PROJECT_ROOT / "data" / "floorsheet_7days_simulated.json"
DUCKDB_FILE = PROJECT_ROOT / "data" / "floorsheet.duckdb"

# === Validate if Parquet file is readable ===
def is_valid_parquet(filepath):
    try:
        pq.ParquetFile(filepath)
        return True
    except Exception:
        return False

# === Rebuild parquet files and DuckDB table ===
def rebuild_parquets():
    # Load data from JSONL or JSON
    if JSONL_SOURCE.exists():
        with open(JSONL_SOURCE, "r") as f:
            records = [json.loads(line) for line in f]
        df = pl.DataFrame(records)
        print("✅ Loaded data from JSONL")
    elif JSON_SOURCE.exists():
        df = pl.read_json(JSON_SOURCE)
        print("✅ Loaded data from JSON")
    else:
        print("❌ No valid input data found.")
        return

    if "symbol" not in df.columns:
        print("❌ 'symbol' column missing in data.")
        return

    # Write one parquet file per symbol
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    for symbol in df["symbol"].unique():
        sdf = df.filter(pl.col("symbol") == symbol)
        out_path = PARQUET_DIR / f"{symbol}.parquet"
        sdf.write_parquet(str(out_path))
        print(f"✅ Rebuilt: {out_path.name}")

    # Save full dataset to DuckDB
    con = duckdb.connect(str(DUCKDB_FILE))
    con.execute("CREATE OR REPLACE TABLE floorsheet AS SELECT * FROM df")
    print("✅ DuckDB table rebuilt.")

# === Main: check for broken files and rebuild ===
if __name__ == "__main__":
    broken_files = []

    if not PARQUET_DIR.exists():
        print("📁 Parquet folder missing. Rebuilding all.")
        rebuild_parquets()
    else:
        for file in os.listdir(PARQUET_DIR):
            if file.endswith(".parquet"):
                path = PARQUET_DIR / file
                if not is_valid_parquet(path):
                    print(f"❌ Broken parquet: {file}")
                    path.unlink()
                    broken_files.append(file)

        if broken_files:
            print("⚠️ Rebuilding broken files...")
            rebuild_parquets()
        else:
            print("✅ All Parquet files valid. No rebuild needed.")
