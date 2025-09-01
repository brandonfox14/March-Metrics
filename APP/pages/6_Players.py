import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------
# Load Data
# --------------------
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# --------------------
# User Selection
# --------------------
team_choice = st.selectbox("Select Team", sorted(df["Teams"].unique()))
conf = df.loc[df["Teams"] == team_choice, "Conference"].values[0]

team_df = df[df["Teams"] == team_choice]
conf_df = df[df["Conference"] == conf]

# --------------------
# Drop unnecessary columns
# --------------------
drop_cols = [
    "FGM_TOP7", "FGA-Top7", "FG3sM-Top7", "FG3sA-Top7", "FTM-Top7", "FTA-Top7",
    "FGM-Top7-Perc", "FGA-Top7-Perc", "FG3sM-Top7-Perc", "FG3sA-Top7-Perc",
    "FTM-Top7-Perc", "FTA-Top7-Perc"
]
team_df = team_df.drop(columns=[c for c in drop_cols if c in team_df.columns])
conf_df = conf_df.drop(columns=[c for c in drop_cols if c in conf_df.columns])

# --------------------
# Convert decimal percentages -> true percentages
# --------------------
percent_cols = [
    "FG_PERC-Top7", "FG3_PERC-Top7", "FT_PERC-Top7",
    "FG_PERC_Top7_per", "FG3_PERC_Top7_per", "FT_PERC_Top7_per",
    "OReb-Top7-Perc", "DReb-Top7-Perc", "Rebounds-Top7-Perc",
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc", "Points-Top7-Perc"
]
for col in percent_cols:
    if col in team_df.columns:
        team_df[col] = team_df[col] * 100
    if col in conf_df.columns:
        conf_df[col] = conf_df[col] * 100

# --------------------
# Summary Tables
# --------------------
# Table 1: Core Top7 percentages
core_cols = [
    "FG_PERC_Top7_per", "FG3_PERC_Top7_per", "FT_PERC_Top7_per",
    "OReb-Top7-Perc", "DReb-Top7-Perc", "Rebounds-Top7-Perc",
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc", "Points-Top7-Perc",
    "Start Percentage top 7"
]

summary_core = pd.DataFrame({
    "Stat": core_cols,
    "Team Value": [team_df.iloc[0][c] for c in core_cols],
    "Conference Average": [conf_df[c].mean() for c in core_cols]
})

# Table 2: Raw performance stats for Top7
stat_cols = [
    "FG_PERC-Top7", "FG3_PERC-Top7", "FT_PERC-Top7",
    "OReb-Top7", "DReb-Top7", "Rebounds-Top7",
    "AST-Top7", "TO-Top7", "STL-Top7", "Points per Game-Top7"
]

summary_stats = pd.DataFrame({
    "Stat": stat_cols,
    "Team Value": [team_df.iloc[0][c] for c in stat_cols],
    "Conference Average": [conf_df[c].mean() for c in stat_cols]
})

st.subheader("Top 7 Core Contribution Percentages")
st.dataframe(summary_core)

st.subheader("Top 7 Raw Performance Stats")
st.dataframe(summary_stats)

# --------------------
# Visual 1: Core Contribution (Conference-based)
# --------------------
fig1 = px.bar(summary_core, x="Stat", y=["Team Value", "Conference Average"],
              barmode="group",
              title=f"{team_choice} vs {conf} – Top 7 Percentages")
st.plotly_chart(fig1)

# --------------------
# Visual 2: Stats Bar with Ranking Overlay
# --------------------
rankings = {col: df[col].rank(ascending=False).loc[df["Teams"] == team_choice].values[0]
            for col in stat_cols}

fig2 = go.Figure()

# Add bar chart (team vs conf)
fig2.add_trace(go.Bar(
    x=summary_stats["Stat"],
    y=summary_stats["Team Value"],
    name=f"{team_choice} Value",
    marker_color="blue"
))
fig2.add_trace(go.Bar(
    x=summary_stats["Stat"],
    y=summary_stats["Conference Average"],
    name=f"{conf} Avg",
    marker_color="gray"
))

# Add ranking overlay (line graph, flipped so 1 = top)
fig2.add_trace(go.Scatter(
    x=list(rankings.keys()),
    y=[365 - r for r in rankings.values()],
    mode="lines+markers",
    name="Team Ranking",
    yaxis="y2",
    line=dict(color="red", width=2)
))

fig2.update_layout(
    title=f"{team_choice} Top 7 Stats with Rankings Overlay",
    yaxis=dict(title="Stat Value"),
    yaxis2=dict(title="Ranking (1 = Top)", overlaying="y", side="right")
)

st.plotly_chart(fig2)
