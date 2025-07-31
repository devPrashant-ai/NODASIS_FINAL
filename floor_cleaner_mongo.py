import json
from datetime import datetime

def clean_and_store_floorsheet(filepath, db):
    with open(filepath, "r") as f:
        raw_lines = f.readlines()

    cleaned = []
    for line in raw_lines:
        try:
            record = json.loads(line)
            record["timestamp"] = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")
            record["rate"] = float(record["rate"])
            record["quantity"] = int(record["quantity"])
            cleaned.append(record)
        except Exception:
            continue

    db["floorsheet"].delete_many({})
    db["floorsheet"].insert_many(cleaned)
