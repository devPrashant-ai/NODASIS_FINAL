
import duckdb
import pandas as pd
import json

def clean_and_load_floorsheet(json_path, duckdb_path):
    with open(json_path) as f:
        records = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(records)
    if 'transaction_date' in df.columns:
        df = df.rename(columns={"transaction_date": "date"})
    con = duckdb.connect(duckdb_path)
    con.execute("DROP TABLE IF EXISTS floorsheet")
    con.execute("CREATE TABLE floorsheet AS SELECT * FROM df")
