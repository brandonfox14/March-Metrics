import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# -----------------------
# Pick default team = highest Points per Game-Top7
# -----------------------
default_team = df.loc[df["Points per Game-Top7"].idxmax(), "Teams"]
teams_sorted = sorted(df["Teams"].dropna().unique().tolist())
team_name = st.selectbox("Select Team", teams_sorted, index=teams_sorted.index(default_team), key="player_team")

team_data = df[df["Teams"] == team_name].iloc[0]
conf = team_data["Conference"]

# -----------------------
# Stat categories
# -----------------------
stat_cols = [
    "FGM_TOP7","FGA-Top7","FG3sM-Top7","FG3sA-Top7",
    "FTM-Top7","FTA-Top7","FG_PERC-Top7","FG3_PERC-Top7","FT_PERC-Top7",
    "OReb-Top7","DReb-Top7","Rebounds-Top7","AST-Top7","TO-Top7","STL-Top7","Points per Game-Top7"
]

perc_cols = [
    "FGM-Top7-Perc","FGA-Top7-Perc","FG3sM-Top7-Perc","FG3sA-Top7-Perc",
    "FTM-Top7-Perc","FTA-Top7-Perc","FG_PERC_Top7_per","FG3_PERC_Top7_per","FT_PERC_Top7_per",
    "OReb-Top7-Perc","DReb-Top7-Perc","Rebounds-Top7-Perc","AST-Top7-Perc","TO-Top7-Perc","STL-Top7-Perc","Points-Top7-Perc","Start Percentage top 7"
]

# -----------------------
# Summary Table
# -----------------------
st.subheader("Top 7 Players Summary")

summary_rows = []

# Raw stats
for col in stat_cols:
    summary_rows.append({
        "Category": "Stat",
        "Metric": col,
        "Value": team_data.get(col, np.nan)
    })

# Percentages
for col in perc_cols:
    summary_rows.append({
        "Category": "Percentage",
        "Metric": col,
        "Value": team_data.get(col, np.nan)  # values are fractions (e.g. 0.7 instead of 70%)
    })

summary_df = pd.DataFrame(summary_rows)
st.dataframe(summary_df, use_container_width=True)

# -----------------------
# Visualization: Conference Comparison for % stats
# -----------------------
st.subheader("Top 7 Contribution vs Conference")

team_vals = team_data[perc_cols]
conf_vals = df[df["Conference"] == conf][perc_cols].mean()

compare_df = pd.DataFrame({
    "Stat": perc_cols,
    "Team Value": team_vals.values,
    "Conference Average": conf_vals.values
})

compare_df["Team Value"] = pd.to_numeric(compare_df["Team Value"], errors="coerce")
compare_df["Conference Average"] = pd.to_numeric(compare_df["Conference Average"], errors="coerce")

compare_long = compare_df.melt(
    id_vars="Stat",
    value_vars=["Team Value", "Conference Average"],
    var_name="Category",
    value_name="Value"
)

fig1 = px.bar(
    compare_long,
    x="Stat",
    y="Value",
    color="Category",
    barmode="group",
    title=f"{team_name} vs {conf} – Top 7 Percentages"
)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------
# Visualization: Standard Points with Rankings Overlay
# -----------------------
st.subheader("Standard Points with Ranking Overlay")

points_df = df[["Teams", "Standard_Points", "Standard_Points_RANK"]].copy()
points_df = points_df.sort_values("Standard_Points_RANK")

fig2 = go.Figure()

# Bar chart for Standard Points
fig2.add_trace(go.Bar(
    x=points_df["Teams"],
    y=points_df["Standard_Points"],
    name="Standard Points"
))

# Line chart for Rank (invert so 1 is top)
fig2.add_trace(go.Scatter(
    x=points_df["Teams"],
    y=points_df["Standard_Points_RANK"],
    mode="lines+markers",
    name="Rank",
    yaxis="y2"
))

fig2.update_layout(
    title="Standard Points with Rankings",
    yaxis=dict(title="Standard Points"),
    yaxis2=dict(
        title="Rank (1=Top)",
        overlaying="y",
        side="right",
        autorange="reversed"
    ),
    xaxis=dict(showticklabels=False)  # hides team labels
)

st.plotly_chart(fig2, use_container_width=True)
