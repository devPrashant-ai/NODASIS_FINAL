
# NODASIS Pro Lite v2.9 – Operator Intelligence

## How to Use
1. Place your floor sheet JSON (line-delimited) in `data/floorsheet_sample.json`.
2. Run: `python run_scoring_pipeline.py`
3. Then launch: `streamlit run streamlit_app.py`
4. View predictions, operator cost, readiness, traps, and profit timing.

## Folders
- `data/parquet/`: Output predictions per symbol
- `models/mbms/`: Add your strategy or operator logic models here


## Added Features
- MBMS model selector
- Trap detection utils
- Accuracy tracker (analytics)
- Filtered prediction table in Streamlit
- CSV export for predictions

## DuckDB Schema (floorsheet)
- symbol (str)
- rate (float)
- quantity (int)
- amount (float)
- transaction_date (str)


## Dependencies
Run this before starting:
```bash
pip install -r requirements.txt
```

OR, if installing manually:
```bash
pip install duckdb pandas streamlit pyarrow
```
