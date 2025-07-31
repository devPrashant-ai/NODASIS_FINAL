# utils/mongo_utils.py

from datetime import datetime, timedelta
from mongo_connector import get_mongo_connection
import pandas as pd
import numpy as np
def get_db():
    client = get_mongo_connection()
    return client["scraped_data"]

def get_symbol_list(fs_collection):
    """
    Return a sorted list of unique symbols.
    """
    return sorted(fs_collection.distinct("symbol"))

def get_symbol_data(fs_collection, symbol):
    """
    Fetch all trade records for a given symbol as DataFrame.
    """
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    print(ninety_days_ago)
    cursor = fs_collection.find({
        "symbol": symbol,
        "transaction_date": {"$gte": ninety_days_ago}
    })
    
    data = list(cursor)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data).drop(columns=["_id"], errors="ignore")  # Safely drops _id if it exists

    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["date"] = pd.to_datetime(df.get("transaction_date", pd.Timestamp.now()))
    return df
def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types for MongoDB compatibility."""
    if isinstance(obj, (np.integer)):
        return int(obj)
    elif isinstance(obj, (np.floating)):
        return float(obj)
    elif isinstance(obj, (np.ndarray)):  # Handle numpy arrays
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    else:
        return obj
def insert_predictions(db, predictions):
    """
    Inserts predictions into the MongoDB collection.
    Overwrites the old predictions.
    """
    pred_collection = db["predictions"]
    pred_collection.delete_many({})
    # Convert all NumPy types in predictions to native Python types
    converted_predictions = [convert_numpy_types(pred) for pred in predictions]
    print(converted_predictions)
    # Insert new predictions
    if converted_predictions:  # Only insert if list is not empty
        result = pred_collection.insert_many(converted_predictions)
        import pdb;pdb.set_trace()
        print(f"✅ Inserted {len(result.inserted_ids)} records into 'predictions'")
    else:
        print("⚠️ No predictions to insert")
    
def get_prediction_data(db):
    """
    Load predictions from MongoDB and return as a DataFrame.
    """
    pred_collection = db["predictions"]
    data = list(pred_collection.find({}))
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)
\
def get_prediction_collection(db):
    return db["scraped_data"]["predictions"]
