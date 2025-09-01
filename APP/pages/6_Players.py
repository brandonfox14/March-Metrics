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
    "FGA-Top7-Perc", "FG3sA-Top7-Perc", "FTA-Top7-Perc"
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
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc",
    "Points-Top7-Perc", "Start Percentage top 7"
]
for col in percent_cols:
    if col in team_df.columns:
        team_df[col] = team_df[col] * 100
    if col in conf_df.columns:
        conf_df[col] = conf_df[col] * 100

# --------------------
# Rename columns to Common Language
# --------------------
rename_map = {
    "FG_PERC_Top7_per": "Field Goal Percentage",
    "FG3_PERC_Top7_per": "3 Field Goal Percentage",
    "FT_PERC_Top7_per": "Free Throw Percentage",
    "OReb-Top7-Perc": "Offensive Rebounds Per Game",
    "DReb-Top7-Perc": "Defensive Rebounds Per Game",
    "Rebounds-Top7-Perc": "Rebounds Per Game",
    "AST-Top7-Perc": "Assists Per Game",
    "TO-Top7-Perc": "Turnover Per Game",
    "STL-Top7-Perc": "Steals Per Game",
    "Points-Top7-Perc": "Points Per Game",
    "Start Percentage top 7": "Starting Percentage",
    "FGM-Top7-Perc": "Core 7 Percentage of Team Field Goals Made",
    "FG3sM-Top7-Perc": "Core 7 Percentage of Team 3 Field Goals Made",
    "FTM-Top7-Perc": "Core 7 Percentage of Team Free Throws Made",
    "FG_PERC-Top7": "Core 7 Percentage of Team Field Goal Percentage",
    "FG3_PERC-Top7": "Core 7 Percentage of Team 3 Point Field Goal Percentage",
    "FT_PERC-Top7": "Core 7 Percentage of Team Free Throw Percentage",
    "OReb-Top7": "Core 7 Percentage of Team Offensive Rebounds",
    "DReb-Top7": "Core 7 Percentage of Team Defensive Rebounds",
    "Rebounds-Top7": "Core 7 Percentage of Team Rebounds",
    "AST-Top7": "Core 7 Percentage of Team Assistants",
    "TO-Top7": "Core 7 Percentage of Team Turnovers",
    "STL-Top7": "Core 7 Percentage of Team Steals",
    "Points per Game-Top7": "Core 7 Percentage of Team Points"
}
team_df = team_df.rename(columns=rename_map)
conf_df = conf_df.rename(columns=rename_map)

# --------------------
# Summary Tables
# --------------------
# Table 1: Core Top7 percentages
core_cols = [
    "Field Goal Percentage", "3 Field Goal Percentage", "Free Throw Percentage",
    "Offensive Rebounds Per Game", "Defensive Rebounds Per Game", "Rebounds Per Game",
    "Assists Per Game", "Turnover Per Game", "Steals Per Game", "Points Per Game",
    "Starting Percentage",
    "Core 7 Percentage of Team Field Goals Made",
    "Core 7 Percentage of Team 3 Field Goals Made",
    "Core 7 Percentage of Team Free Throws Made"
]

summary_core = pd.DataFrame({
    "Stat": core_cols,
    "Team Value": [team_df.iloc[0][c] for c in core_cols],
    "Conference Average": [conf_df[c].mean() for c in core_cols]
})

# Table 2: Raw performance stats for Top7
stat_cols = [
    "Core 7 Percentage of Team Field Goal Percentage",
    "Core 7 Percentage of Team 3 Point Field Goal Percentage",
    "Core 7 Percentage of Team Free Throw Percentage",
    "Core 7 Percentage of Team Offensive Rebounds",
    "Core 7 Percentage of Team Defensive Rebounds",
    "Core 7 Percentage of Team Rebounds",
    "Core 7 Percentage of Team Assistants",
    "Core 7 Percentage of Team Turnovers",
    "Core 7 Percentage of Team Steals",
    "Core 7 Percentage of Team Points"
]

summary_stats = pd.DataFrame({
    "Stat": stat_cols,
    "Team Value": [team_df.iloc[0][c] for c in stat_cols],
    "Conference Average": [conf_df[c].mean() for c in stat_cols]
})

# --------------------
# Show Summary Tables
# --------------------
st.subheader(f"{team_choice} Core 7 Players Statistics")
st.dataframe(summary_core)

st.subheader(f"{team_choice} Percent of Team Stats for Core 7 Players")
st.dataframe(summary_stats)

# --------------------
# Visual 1: Core Contribution (Conference-based)
# --------------------
fig1 = px.bar(summary_core, x="Stat", y=["Team Value", "Conference Average"],
              barmode="group",
              title=f"{team_choice} vs {conf} – Core 7 Players Statistics")
st.plotly_chart(fig1)

# --------------------
# Visual 2: Stats Bar with Ranking Overlay
# --------------------
rankings = {col: df[col].rank(ascending=False).loc[df["Teams"] == team_choice].values[0]
            for col in stat_cols if col in df.columns}

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
    title=f"{team_choice} Percent of Team Stats for Core 7 Players with Rankings Overlay",
    yaxis=dict(title="Stat Value"),
    yaxis2=dict(title="Ranking (1 = Top)", overlaying="y", side="right")
)

st.plotly_chart(fig2)
