
from engine.floorsheet_cleaner_duckdb_ready import clean_and_load_floorsheet
from engine.run_scoring_pipeline import generate_predictions
import os

json_path = r"/mnt/data/nodasis_v2.9_runtime_ready_test/data/test/floorsheet_7d.json"
duckdb_path = r"/mnt/data/NODASIS_Pro_Lite_v2.9_RUNTIME_SIM_TEST/floorsheet.duckdb"
parquet_out_dir = r"/mnt/data/NODASIS_Pro_Lite_v2.9_RUNTIME_SIM_TEST/data/parquet"

clean_and_load_floorsheet(json_path, duckdb_path)
generate_predictions(duckdb_path, parquet_out_dir)

print("✅ Simulation complete. Files generated:")
for f in sorted(os.listdir(parquet_out_dir)):
    print(" -", f)
