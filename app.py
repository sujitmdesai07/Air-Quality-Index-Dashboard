import streamlit as st
import pandas as pd
import numpy as np


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: white;
    }
    .stMetric label { font-size: 0.82rem !important; color: #888 !important; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-top: 1rem;
        border-left: 4px solid #667eea;
        padding-left: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ── AQI category colours ──────────────────────────────────────────────────────
AQI_COLORS = {
    "Good":          "#00b050",
    "Satisfactory":  "#92d050",
    "Moderate":      "#ffff00",
    "Poor":          "#ff9900",
    "Very Poor":     "#ff0000",
    "Severe":        "#c00000",
}
POLLUTANTS = ["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene"]

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("city_day.csv", parse_dates=["Date"])
    df["Year"]  = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["AQI_Bucket"] = df["AQI_Bucket"].fillna("Unknown")
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌫️ Filters")

    cities = sorted(df["City"].unique())
    selected_cities = st.multiselect(
        "Cities",
        options=cities,
        default=["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai"],
    )

    years = sorted(df["Year"].unique())
    year_range = st.slider(
        "Year range",
        min_value=int(years[0]),
        max_value=int(years[-1]),
        value=(int(years[0]), int(years[-1])),
    )

    pollutant = st.selectbox("Pollutant for deep-dive", POLLUTANTS, index=0)

    st.markdown("---")
    st.markdown("**Dataset info**")
    st.caption(f"22 Indian cities · 2015 – 2020  \n{len(df):,} daily records")

# ── Filter data ───────────────────────────────────────────────────────────────
if not selected_cities:
    st.warning("Please select at least one city from the sidebar.")
    st.stop()

mask = (
    df["City"].isin(selected_cities) &
    df["Year"].between(*year_range)
)
fdf = df[mask].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🌫️ India City Air Quality Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Daily pollution data across 22 Indian cities · 2015 – 2020</div>', unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

avg_aqi    = fdf["AQI"].mean()
max_aqi    = fdf["AQI"].max()
max_city   = fdf.loc[fdf["AQI"].idxmax(), "City"] if not fdf["AQI"].isna().all() else "N/A"
good_pct   = (fdf["AQI_Bucket"].isin(["Good", "Satisfactory"])).mean() * 100
severe_pct = (fdf["AQI_Bucket"] == "Severe").mean() * 100

k1.metric("Avg AQI",        f"{avg_aqi:.0f}")
k2.metric("Peak AQI",       f"{max_aqi:.0f}", help=f"Recorded in {max_city}")
k3.metric("City with peak", max_city)
k4.metric("Good/Satisfactory days", f"{good_pct:.1f}%")
k5.metric("Severe days",    f"{severe_pct:.1f}%")

st.markdown("---")

# ── Row 1: AQI trend + AQI distribution ──────────────────────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown('<div class="section-title">📈 Monthly Average AQI Over Time</div>', unsafe_allow_html=True)
    monthly = (
        fdf.groupby(["City", pd.Grouper(key="Date", freq="MS")])["AQI"]
        .mean().reset_index()
    )
    fig_trend = px.line(
        monthly, x="Date", y="AQI", color="City",
        markers=False,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_trend.update_layout(
        height=340, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.25),
        yaxis_title="AQI",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">🥧 AQI Category Breakdown</div>', unsafe_allow_html=True)
    bucket_counts = fdf["AQI_Bucket"].value_counts().reset_index()
    bucket_counts.columns = ["Category", "Days"]
    bucket_counts = bucket_counts[bucket_counts["Category"] != "Unknown"]
    cat_order = list(AQI_COLORS.keys())
    bucket_counts["Category"] = pd.Categorical(bucket_counts["Category"], categories=cat_order, ordered=True)
    bucket_counts = bucket_counts.sort_values("Category")
    fig_pie = px.pie(
        bucket_counts, names="Category", values="Days",
        color="Category",
        color_discrete_map=AQI_COLORS,
        hole=0.45,
    )
    fig_pie.update_layout(
        height=340, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.15),
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 2: City comparison bar + Seasonality ─────────────────────────────────
col_c, col_d = st.columns([2, 3])

with col_c:
    st.markdown('<div class="section-title">🏙️ City-wise Average AQI</div>', unsafe_allow_html=True)
    city_avg = (
        fdf.groupby("City")["AQI"].mean()
        .reset_index().sort_values("AQI", ascending=True)
    )
    fig_bar = px.bar(
        city_avg, x="AQI", y="City", orientation="h",
        color="AQI",
        color_continuous_scale=["#00b050", "#ffff00", "#ff9900", "#c00000"],
    )
    fig_bar.update_layout(
        height=370, margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        yaxis_title="",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_d:
    st.markdown('<div class="section-title">📅 Seasonal Pattern (Monthly Avg AQI by City)</div>', unsafe_allow_html=True)
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonal = (
        fdf.groupby(["City", "Month_Name"])["AQI"]
        .mean().reset_index()
    )
    seasonal["Month_Name"] = pd.Categorical(seasonal["Month_Name"], categories=month_order, ordered=True)
    seasonal = seasonal.sort_values("Month_Name")
    fig_season = px.line(
        seasonal, x="Month_Name", y="AQI", color="City",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_season.update_layout(
        height=370, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.25),
        xaxis_title="Month", yaxis_title="Avg AQI",
    )
    st.plotly_chart(fig_season, use_container_width=True)

# ── Row 3: Pollutant deep-dive ────────────────────────────────────────────────
st.markdown(f'<div class="section-title">🔬 Deep Dive: {pollutant} Levels</div>', unsafe_allow_html=True)

col_e, col_f = st.columns(2)

with col_e:
    poll_monthly = (
        fdf.groupby(["City", pd.Grouper(key="Date", freq="MS")])[pollutant]
        .mean().reset_index()
    )
    fig_poll = px.line(
        poll_monthly, x="Date", y=pollutant, color="City",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_poll.update_layout(
        height=300, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.3),
        title_text=f"Monthly avg {pollutant} over time",
    )
    st.plotly_chart(fig_poll, use_container_width=True)

with col_f:
    fig_box = px.box(
        fdf.dropna(subset=[pollutant]),
        x="City", y=pollutant,
        color="City",
        color_discrete_sequence=px.colors.qualitative.Bold,
        points=False,
    )
    fig_box.update_layout(
        height=300, margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        xaxis_tickangle=-35,
        title_text=f"{pollutant} distribution by city",
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ── Row 4: Correlation heatmap ────────────────────────────────────────────────
st.markdown('<div class="section-title">🔗 Pollutant Correlation Heatmap</div>', unsafe_allow_html=True)

available_cols = [p for p in POLLUTANTS + ["AQI"] if fdf[p].notna().sum() > 100]
corr = fdf[available_cols].corr().round(2)

fig_heat = go.Figure(go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.columns.tolist(),
    colorscale="RdBu_r",
    zmin=-1, zmax=1,
    text=corr.values.round(2),
    texttemplate="%{text}",
    textfont={"size": 10},
))
fig_heat.update_layout(
    height=380,
    margin=dict(t=10, b=10, l=10, r=10),
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Row 5: Year-over-year AQI + worst days ────────────────────────────────────
col_g, col_h = st.columns([3, 2])

with col_g:
    st.markdown('<div class="section-title">📊 Year-over-Year Avg AQI by City</div>', unsafe_allow_html=True)
    yoy = fdf.groupby(["Year", "City"])["AQI"].mean().reset_index()
    fig_yoy = px.bar(
        yoy, x="Year", y="AQI", color="City",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_yoy.update_layout(
        height=330, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.3),
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

with col_h:
    st.markdown('<div class="section-title">🚨 Top 10 Worst Pollution Days</div>', unsafe_allow_html=True)
    worst = (
        fdf.dropna(subset=["AQI"])
        .nlargest(10, "AQI")[["Date", "City", "AQI", "AQI_Bucket"]]
        .reset_index(drop=True)
    )
    worst["Date"] = worst["Date"].dt.strftime("%Y-%m-%d")
    worst["AQI"] = worst["AQI"].round(0).astype(int)
    worst.index += 1

    def color_bucket(val):
        color = AQI_COLORS.get(val, "#aaa")
        return f"background-color: {color}; color: {'#fff' if val in ('Poor','Very Poor','Severe') else '#333'}; border-radius:4px; padding:2px 6px;"

    styled = worst.style.applymap(color_bucket, subset=["AQI_Bucket"])
    st.dataframe(styled, use_container_width=True, height=330)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Data source: India Air Quality dataset (Kaggle) · Dashboard built with Streamlit + Plotly")
