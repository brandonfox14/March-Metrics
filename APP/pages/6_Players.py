import streamlit as st
import pandas as pd
import plotly.express as px

# Cache the data loading
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# Dropdowns
team_choice = st.selectbox("Select a Team", sorted(df["Teams"].unique()))
conf = df.loc[df["Teams"] == team_choice, "Conference"].values[0]

# --- Define columns to drop
drop_cols = [
    "FGM_TOP7", "FGA-Top7", "FG3sM-Top7", "FG3sA-Top7", 
    "FTM-Top7", "FTA-Top7"
]
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# --- Define percentage columns (convert to actual percentages)
percent_cols = [
    "FG_PERC-Top7", "FG3_PERC-Top7", "FT_PERC-Top7",
    "FG_PERC_Top7_per", "FG3_PERC_Top7_per", "FT_PERC_Top7_per",
    "OReb-Top7-Perc", "DReb-Top7-Perc", "Rebounds-Top7-Perc",
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc",
    "Points-Top7-Perc", "Start Percentage top 7"
]

for col in percent_cols:
    if col in df.columns:
        df[col] = df[col] * 100

# --- Map columns to common language
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
df = df.rename(columns=rename_map)

# --- Subset for summary table (percentages)
summary_cols = [
    "Field Goal Percentage", "3 Field Goal Percentage", "Free Throw Percentage",
    "Offensive Rebounds Per Game", "Defensive Rebounds Per Game", "Rebounds Per Game",
    "Assists Per Game", "Turnover Per Game", "Steals Per Game", "Points Per Game",
    "Starting Percentage",
    "Core 7 Percentage of Team Field Goals Made",
    "Core 7 Percentage of Team 3 Field Goals Made",
    "Core 7 Percentage of Team Free Throws Made"
]

summary_df = df.loc[df["Teams"] == team_choice, summary_cols].T.reset_index()
summary_df.columns = ["Stat", "Value"]

# --- Show summary table
st.subheader(f"{team_choice} Core 7 Players Statistics")
st.dataframe(summary_df)

# --- Stats for bar + line chart
chart_cols = [
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

chart_df = df.loc[df["Teams"] == team_choice, chart_cols].T.reset_index()
chart_df.columns = ["Stat", "Value"]

# --- Bar chart
fig1 = px.bar(chart_df, x="Stat", y="Value", title=f"{team_choice} Percent of Team Stats for Core 7 Players")
st.plotly_chart(fig1, use_container_width=True)
