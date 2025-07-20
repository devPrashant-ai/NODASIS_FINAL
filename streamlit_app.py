from db_config import get_mongo_client
import streamlit as st
import pandas as pd

DUCKDB_FILE = "dashboard_data/final_predictions.duckdb"

# === Load data from DuckDB ===
@st.cache_data
def load_predictions():
    client = get_mongo_client()
    db = client['nodasis']
    records_cursor = db.predictions.find(
            {},                     # No filter — get all documents
            {"_id": 0} # Only include `symbol`, exclude `_id`
        )
    return  pd.DataFrame(records_cursor)


df = load_predictions()

# === SIDEBAR SUMMARY ===
st.sidebar.title("📌 Dashboard Summary")

st.sidebar.markdown("""
**Top Strategies:**
- FalseBreakSniper
- TrapFade15
- RetailFadeTrap

**Quick Stats:**
- 🔼 Top Readiness: NABIL (93%)
- ⚠️ Most Trap Risk: HDL
- ⏳ Fastest Profit: GBIME (4 days)
""")

# Optional: Show preview table in sidebar
preview_cols = ['symbol', 'strategy_selected', 'readiness', 'llm_comment']
available_preview = [col for col in preview_cols if col in df.columns]
if available_preview:
    st.sidebar.dataframe(df[available_preview].head(3), height=250)
else:
    st.sidebar.info("ℹ️ Preview columns (like 'llm_comment') not found.")

# Debugging: Show available columns
# st.sidebar.write("📌 Available columns:")
# st.sidebar.write(df.columns.tolist())

# === Main Dashboard ===
if df.empty:
    st.warning("No prediction data found.")
    st.stop()

st.set_page_config(layout="wide", page_title="📈 NODASIS NEPSE Operator Intelligence")
st.title("📊 NODASIS Pro v2.9 – Operator Intelligence Dashboard")

tabs = st.tabs([
    "Live Predictions",
    "Strategy Leaderboard",
    "Execution + Replay",
    "LLM Explanation",
    "Backtest Summary"
])

# --- Tab 1: Live Predictions ---
with tabs[0]:
    st.subheader("📡 Live Operator Predictions")
    if 'trap_score' in df.columns:
        df['Trap Alert'] = df['trap_score'].apply(lambda x: '⚠️ Yes' if x >= 0.7 else '✅ No')
    display_cols = ['symbol', 'transaction_date', 'ltp', 'operator_cost',
                    'strategy_selected', 'signal', 'readiness', 'profit_days_estimate', 'Trap Alert']
    available = [col for col in display_cols if col in df.columns]
    st.dataframe(df[available], use_container_width=True)

# --- Tab 2: Strategy Leaderboard ---
with tabs[1]:
    st.subheader("📈 Strategy Usage Frequency (per Symbol)")
    if 'strategy_selected' in df.columns:
        strat_leaderboard = (
            df.groupby(['symbol', 'strategy_selected'])
              .size()
              .reset_index(name='times_used')
              .sort_values(by='times_used', ascending=False)
        )
        st.dataframe(strat_leaderboard, use_container_width=True)
    else:
        st.warning("Strategy data not available.")

# --- Tab 3: Replay Timeline ---
with tabs[2]:
    st.subheader("⏱ Strategy Execution + Replay View")
    replay_cols = ['symbol', 'transaction_date', 'signal', 'strategy_selected',
                   'replay_match', 'trap_score', 'readiness', 'profit_days_estimate']
    available = [col for col in replay_cols if col in df.columns]
    st.dataframe(df[available], use_container_width=True)

# --- Tab 4: LLM Comments ---
with tabs[3]:
    st.subheader("🧠 AI-generated Commentary (LLM)")
    llm_cols = ['symbol', 'strategy_selected', 'readiness', 'llm_comment']
    available_llm = [col for col in llm_cols if col in df.columns]
    if available_llm:
        st.dataframe(df[available_llm], use_container_width=True)
    else:
        st.warning("⚠️ 'llm_comment' or related columns not found in data.")

# --- Tab 5: Backtest Results ---
with tabs[4]:
    st.subheader("📊 Backtest Simulation Results (Snapshot)")
    backtest_cols = ['symbol', 'transaction_date', 'signal', 'profit_days_estimate', 'readiness']
    available = [col for col in backtest_cols if col in df.columns]
    st.dataframe(df[available], use_container_width=True)
