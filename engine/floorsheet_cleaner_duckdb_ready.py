
import duckdb
import pandas as pd
import json

def clean_and_load_floorsheet(json_path, duckdb_path):
    con = duckdb.connect(duckdb_path)
    con.execute("DROP TABLE IF EXISTS floorsheet")
    con.execute("""
        CREATE TABLE floorsheet (
            symbol TEXT,
            broker INTEGER,
            rate DOUBLE,
            quantity INTEGER,
            amount DOUBLE,
            transaction_date TEXT
        )
    """)
    rows = []
    with open(json_path, 'r') as f:
        for line in f:
            rows.append(json.loads(line))
    df = pd.DataFrame(rows)
    con.register("df_temp", df)
    con.execute("INSERT INTO floorsheet SELECT * FROM df_temp")
    con.close()
