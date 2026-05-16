# app.py

import streamlit as st
import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception as e:
    st.error(f"Matplotlib Error: {e}")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Air Quality Dashboard",
    layout="wide"
)

st.title("🌍 Air Quality Index Dashboard")
st.markdown("Interactive dashboard for analyzing city air pollution data.")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("city_day.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filter Data")

cities = sorted(df["City"].dropna().unique())

selected_city = st.sidebar.selectbox(
    "Select City",
    cities
)

pollutants = [
    "PM2.5", "PM10", "NO2", "SO2", "CO", "O3", "AQI"
]

selected_pollutant = st.sidebar.selectbox(
    "Select Pollutant",
    pollutants
)

# Filter data
city_df = df[df["City"] == selected_city]

# -----------------------------
# Display Dataset
# -----------------------------
st.subheader("Dataset Preview")

st.dataframe(city_df.head())

# -----------------------------
# KPI Metrics
# -----------------------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

avg_aqi = round(city_df["AQI"].mean(), 2)
max_aqi = round(city_df["AQI"].max(), 2)
min_aqi = round(city_df["AQI"].min(), 2)

col1.metric("Average AQI", avg_aqi)
col2.metric("Maximum AQI", max_aqi)
col3.metric("Minimum AQI", min_aqi)

# -----------------------------
# Line Chart
# -----------------------------
st.subheader(f"{selected_pollutant} Trend Over Time")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    city_df["Date"],
    city_df[selected_pollutant]
)

ax.set_xlabel("Date")
ax.set_ylabel(selected_pollutant)
ax.set_title(f"{selected_pollutant} Levels in {selected_city}")

plt.xticks(rotation=45)

st.pyplot(fig)

# -----------------------------
# AQI Bucket Distribution
# -----------------------------
st.subheader("AQI Bucket Distribution")

aqi_bucket = city_df["AQI_Bucket"].value_counts()

fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.bar(aqi_bucket.index, aqi_bucket.values)

ax2.set_xlabel("AQI Bucket")
ax2.set_ylabel("Count")
ax2.set_title("AQI Category Distribution")

plt.xticks(rotation=45)

st.pyplot(fig2)

# -----------------------------
# Correlation Heatmap
# -----------------------------
st.subheader("Correlation Between Pollutants")

numeric_cols = city_df.select_dtypes(include="number")

corr = numeric_cols.corr()

fig3, ax3 = plt.subplots(figsize=(10, 6))

heatmap = ax3.imshow(corr)

ax3.set_xticks(range(len(corr.columns)))
ax3.set_yticks(range(len(corr.columns)))

ax3.set_xticklabels(corr.columns, rotation=90)
ax3.set_yticklabels(corr.columns)

plt.colorbar(heatmap)

st.pyplot(fig3)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Created using Streamlit 📊")
