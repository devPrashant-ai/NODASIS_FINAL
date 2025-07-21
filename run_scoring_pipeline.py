import os
import polars as pl
from pathlib import Path
import importlib.util
import pandas as pd

from db_config import get_mongo_client
from drltuner.drl_tuner import train_drl_model
from engine.auto_switch import auto_switch_strategy

# Paths and config
PROJECT_ROOT = Path(__file__).resolve().parent
PARQUET_DIR = PROJECT_ROOT / "data" / "parquet"
MBMS_MODEL_PATH = PROJECT_ROOT / "models" / "mbms"
MONGO_DB = "nodasis"
MONGO_COLLECTION = "predictions"

# Connect to MongoDB
try:
    mongo_client = get_mongo_client()
    mongo_coll = mongo_client[MONGO_DB][MONGO_COLLECTION]
except Exception as e:
    print("⚠️ MongoDB unavailable:", e)
    mongo_coll = None

# Load all MBMS model functions
def load_all_models():
    model_funcs = []
    for fname in os.listdir(MBMS_MODEL_PATH):
        if fname.endswith(".py"):
            path = MBMS_MODEL_PATH / fname
            module_name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod, "score_bz"):
                    model_funcs.append(mod.score_bz)
                else:
                    print(f"⚠️ Skipped {fname}: no score_bz() found.")
            except Exception as e:
                print(f"❌ Failed to load {fname}: {e}")
    return model_funcs

mbms_models = load_all_models()

# Process all parquet prediction files
# Process all parquet prediction files

for file in os.listdir(PARQUET_DIR):
    if file.endswith(".parquet"):
        fpath = PARQUET_DIR / file
        df = pl.read_parquet(fpath)
        
        # Process models
        df = train_drl_model(df)  # Assuming this returns a Polars DataFrame
        for model_func in mbms_models:
            try:
                df = model_func(df)       # Apply MBMS model
            except Exception as e:
                print(f"⚠️ MBMS model failed on {file}: {e}")
        
        # Handle 'mbms_confidence' (Polars syntax)
        if "mbms_confidence" in df.columns:
            df = df.with_columns(
                (pl.col("mbms_confidence") * 100).clip(0, 100).alias("readiness")
            )
        
        # Add 'active_model' column
        df = df.with_columns(
            pl.lit("mbms_drl_combo").alias("active_model")
        )
        
        # Auto-switch strategy (ensure it returns a Polars DataFrame)
        try:
            df, _ = auto_switch_strategy(df, {})  # Must return Polars DF
        except Exception as e:
            print(f"⚠️ auto_switch_strategy failed: {e}")
        
        # Overwrite parquet (Polars syntax)
        df.write_parquet(fpath)  # No `index=False` (Polars doesn't use indexes)
        
        # Insert into MongoDB (convert to dicts first)
        if mongo_coll is not None:
            try:
                mongo_coll.insert_many(df.to_dicts())  # Polars: `to_dicts()`
            except Exception as e:
                print(f"⚠️ Mongo insert failed for {file}: {e}")

print("✅ All MBMS + DRL predictions processed and pushed to MongoDB.")
