import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Superior EHS Dashboard", layout="wide")
st.title("Superior Huntingdon Composites - EHS Dashboard")
st.markdown(f"*Last updated: {datetime.now().strftime('%B %d, %Y')}*")

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
r2026 = [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0]  # From Safety Alert list
r2025 = [0]*12  # Fill from loss runs
benchmark = 3.3  # NAICS 326199 - update from loss runs

col1, col2, col3, col4 = st.columns(4)
col1.metric("YTD Recordables", sum(r2026))
col2.metric("Loss Time YTD", 3)
col3.metric("Near Misses YTD", 21)
col4.metric("Industry Benchmark", benchmark)

st.subheader("Monthly Recordable Incidents")
df = pd.DataFrame({"Month": months, "2026": r2026, "2025": r2025})
fig = go.Figure()
fig.add_trace(go.Bar(x=df["Month"], y=df["2026"], name="2026", marker_color="#f59e0b"))
fig.add_trace(go.Bar(x=df["Month"], y=df["2025"], name="2025", marker_color="#3b82f6"))
fig.add_hline(y=benchmark/12, line_dash="dash", line_color="#ef4444",
              annotation_text=f"Industry avg ({benchmark}/yr)")
fig.update_layout(barmode="group", height=400)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Raw Data"):
    st.dataframe(df)
    st.markdown("Data from 2026 Safety Alert List. Update hours worked + 2025 data from loss runs.")
