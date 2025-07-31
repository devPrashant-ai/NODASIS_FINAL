# streamlit_app.py

from mongo_connector import get_mongo_connection
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.mongo_utils import get_prediction_data


db = get_mongo_connection()
collection = db["predictions"]

st.set_page_config(layout="wide", page_title="NODASIS Pro Lite v2.9")

st.title("📊 NODASIS Pro Lite v2.9 – NEPSE Prediction Dashboard (MongoDB Edition)")

# --- Sidebar Filters ---
st.sidebar.header("Filter Predictions")

sector_filter = st.sidebar.text_input("Sector Contains (optional)")
min_confidence = st.sidebar.slider("Min Confidence %", 0, 100, 30)
show_buy_only = st.sidebar.checkbox("Show Buy Signals Only", value=True)

# --- Load Data from MongoDB ---
df = get_prediction_data(db)


if df.empty:
    st.warning("No prediction data found in MongoDB.")
    st.stop()

# --- Filter Logic ---
df = df[df["confidence"] >= min_confidence]

if show_buy_only:
    df = df[df["buy_signal"] == True]

if sector_filter:
    df = df[df["sector"].str.contains(sector_filter, case=False, na=False)]

# --- Column Selector ---
default_cols = [
    "symbol", "operator_cost", "ltp", "confidence", "trap_risk","drl_signal",
    "buy_signal", "readiness", "days_to_profit", "forecast_label", "llm_insight", "replay_match"
]
cols = st.multiselect("Select Columns to Display", df.columns.tolist(), default=default_cols)

# --- Display Table ---
st.subheader(f"📌 {len(df)} Predictions Matching Filters")

st.dataframe(df[cols].sort_values(by="confidence", ascending=False), use_container_width=True)

# --- Operator Cost vs LTP Chart ---
st.subheader("📈 Operator Cost vs LTP")

fig = px.scatter(df,
    x="operator_cost",
    y="ltp",
    color="confidence",
    hover_data=["symbol", "readiness", "days_to_profit", "trap_risk", "buy_signal"]
)
st.plotly_chart(fig, use_container_width=True)

# --- Days to Profit Histogram ---
st.subheader("⏱️ Days to Profit Forecast")

fig2 = px.histogram(df, x="days_to_profit", nbins=20, title="Days to Reach 10% Profit")
st.plotly_chart(fig2, use_container_width=True)

# --- Symbol Commentary ---
st.subheader("🧠 LLM Insights")

for _, row in df.iterrows():
    st.markdown(f"**{row['symbol']}**: {row.get('llm_insight', 'No commentary available.')}")
