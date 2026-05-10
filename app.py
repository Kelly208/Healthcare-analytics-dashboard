import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.queries import (
    fetch_patient_trends,
    fetch_appointment_trends,
    fetch_services_usage,
    fetch_operational_efficiency,
    fetch_psychologist_load,
    fetch_appointment_status,
    fetch_kpis,
    fetch_heatmap_data,
    fetch_monthly_growth,
)

st.set_page_config(
    page_title="Healthcare Analytics", layout="wide", initial_sidebar_state="expanded"
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #111827;
        color: #E5E7EB;
        font-family: 'Inter', sans-serif;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}

    h1, h2, h3, h4, h5, h6 {
        color: #E5E7EB !important;
        font-weight: 500;
    }
    
    p {
        color: #D1D5DB;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #E5E7EB;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("Healthcare Operational Analytics Dashboard")
st.markdown(
    "*End-to-end healthcare analytics pipeline for operational efficiency and patient trend analysis.*"
)
st.divider()

try:
    total_p, total_a, avg_s = fetch_kpis()
    eff_df = fetch_operational_efficiency()
    avg_wait = eff_df["avg_wait_time"].iloc[0]
    cancel_rate = eff_df["cancellation_rate"].iloc[0]
    avg_duration = eff_df["avg_service_duration_mins"].iloc[0]
    monthly_growth = fetch_monthly_growth()
except Exception as e:
    st.error(f"Error loading data: {e}. Please ensure the database is generated.")
    st.stop()

custom_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#E5E7EB"),
        xaxis=dict(gridcolor="#1F2937", zerolinecolor="#1F2937"),
        yaxis=dict(gridcolor="#1F2937", zerolinecolor="#1F2937"),
    )
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Patients",
        value=f"{total_p:,}",
        delta=f"{monthly_growth:.1f}% Monthly Growth",
    )
with col2:
    st.metric(label="Avg Wait Time", value=f"{avg_wait:.1f} min")
with col3:
    st.metric(label="Satisfaction Score", value=f"{avg_s:.1f} / 5.0")
with col4:
    st.metric(label="Avg Service Duration", value=f"{avg_duration:.1f} min")

st.divider()

st.markdown("### Peak Operational Periods")
heatmap_df = fetch_heatmap_data()
heatmap_pivot = heatmap_df.pivot(
    index="day_of_week", columns="hour_of_day", values="appointment_count"
)
days_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
heatmap_pivot = heatmap_pivot.reindex(days_order)

fig_heat = px.imshow(
    heatmap_pivot,
    labels=dict(x="Hour of Day", y="Day of Week", color="Appointments"),
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    color_continuous_scale="Teal",
    aspect="auto",
    height=500,
)
fig_heat.update_layout(template=custom_template, margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

st.markdown("### Monthly Registrations")
pt_trends = fetch_patient_trends()
fig_pt = px.line(
    pt_trends,
    x="month",
    y="new_patients",
    markers=True,
    line_shape="spline",
    color_discrete_sequence=["#E5E7EB"],
    height=450,
)
fig_pt.update_layout(
    xaxis_title="",
    yaxis_title="New Patients",
    template=custom_template,
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_pt, use_container_width=True)

st.divider()

st.markdown("### Workload Distribution")
psych_load = fetch_psychologist_load()
fig_load = px.bar(
    psych_load,
    x="specialty",
    y="total_appointments",
    color_discrete_sequence=["#4B5563"],
    height=450,
)
fig_load.update_layout(
    xaxis_title="",
    yaxis_title="Appointments",
    template=custom_template,
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_load, use_container_width=True)

st.divider()

st.markdown("### Most Requested Services")
serv_usage = fetch_services_usage()
fig_serv = px.bar(
    serv_usage,
    x="count",
    y="service_type",
    orientation="h",
    color_discrete_sequence=["#374151"],
    height=400,
)
fig_serv.update_layout(
    xaxis_title="Appointments",
    yaxis_title="",
    template=custom_template,
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_serv, use_container_width=True)

st.divider()

st.markdown("### Cancellation Impact")
status_df = fetch_appointment_status()
fig_status = px.pie(
    status_df,
    values="count",
    names="status",
    hole=0.5,
    color="status",
    color_discrete_map={
        "Completed": "#4B6356",
        "Cancelled": "#374151",
        "Rescheduled": "#4B5563",
        "No Show": "#1F2937",
    },
    height=500,
)
fig_status.update_layout(template=custom_template, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_status, use_container_width=True)
st.caption(f"**No-Show / Cancellation Rate:** {cancel_rate:.1f}%")
