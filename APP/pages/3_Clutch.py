import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# -----------------------
# Team Selection
# -----------------------
teams_sorted = sorted(df["Teams"].dropna().unique().tolist())
col1, col2 = st.columns(2)
with col1:
    team_a = st.selectbox("Select Left Team", teams_sorted, index=0, key="clutch_team_a")
with col2:
    team_b = st.selectbox("Select Right Team", teams_sorted, index=1, key="clutch_team_b")

team_a_data = df[df["Teams"] == team_a].iloc[0]
team_b_data = df[df["Teams"] == team_b].iloc[0]

# -----------------------
# Clutch Stats List
# -----------------------
clutch_stats = [
    "CLUTCH_FGM","CLUTCH_FGA","CLUTCH_FGPERC","CLUTCH_FG_RANK",
    "CLUTCH_3FGM","CLUTCH_3FGA","CLUTCH_3FGPERC","CLUTCH_3_RANK",
    "CLUTCH_FTM","CLUTCH_FTA","CLUTCH_FTPERC","CLUTCH_FT_RANK",
    "CLUTCH_SM","CLUTCH_SM_RANK",
    "CLUTCH_REB","CLUTCH_REB_RANK",
    "OPP_CLTCH_REB","OPP_CLTCH_REB_RANK",
    "CLTCH_OFF_REB","CLTCH_OFF_REB_RANK",
    "OPP_CLTCH_OFF_REB","OPP_CLTCH_OFF_REB_RANK",
    "CLTCH_TURN","CLTCH_TURN_RANK",
    "CLTCH_OPP_TURN","CLTCH_OPP_TURN_RANK",
    "CLTCH_STL","CLTCH_STL_RANK",
    "TOP25_CLUTCH","OVERTIME_GAMES"
]

# -----------------------
# Summary Table
# -----------------------
st.subheader("Clutch Performance Summary")

summary_rows = []
for stat in clutch_stats:
    val_a = team_a_data.get(stat, np.nan)
    val_b = team_b_data.get(stat, np.nan)
    summary_rows.append({
        "Stat": stat,
        f"{team_a}": val_a,
        f"{team_b}": val_b
    })

summary_df = pd.DataFrame(summary_rows)
st.dataframe(summary_df, use_container_width=True)

# -----------------------
# Visualization: Shooting % Clutch vs Season
# -----------------------
st.subheader("Shooting: Clutch vs Season")

shooting_stats = ["FG%", "3PT%", "FT%"]
season_cols = ["FG_PERC", "FG3_PERC", "FT_PERC"]
clutch_cols = ["CLUTCH_FGPERC", "CLUTCH_3FGPERC", "CLUTCH_FTPERC"]

def build_shooting_chart(team_name, team_data):
    season_values = [team_data[c] * 100 for c in season_cols]
    clutch_values = [team_data[c] * 100 for c in clutch_cols]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=shooting_stats,
        y=season_values,
        name="Season",
        marker_color="lightblue"
    ))
    fig.add_trace(go.Bar(
        x=shooting_stats,
        y=clutch_values,
        name="Clutch",
        marker_color="orange"
    ))
    fig.update_layout(
        barmode="group",
        title=f"{team_name} Shooting: Season vs Clutch",
        yaxis=dict(title="Percentage"),
        template="plotly_white"
    )
    return fig

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(build_shooting_chart(team_a, team_a_data), use_container_width=True)
with col2:
    st.plotly_chart(build_shooting_chart(team_b, team_b_data), use_container_width=True)


