import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("team_stats.csv")  # replace with your file
    return df

df = load_data()

st.title("🏀 Team Comparison Radar")

# --- Team Selection ---
teams = sorted(df["Teams"].unique())
team1 = st.selectbox("Select Team 1", teams, index=0)
team2 = st.selectbox("Select Team 2", teams, index=1)

# --- Define Stat Categories ---
categories = {
    "Offense": ["Points", "FG_PERC", "FGM/G", "FG3_PERC", "FG3M/G", "FT_PERC", "FTM/G"],
    "Defense": ["OPP_PPG", "OPP_FG_PERC", "OPP_FGM/G", "OPP_FG3_PERC", "OPP_FG3M/G", "OPP_% of Points from 3", "OPP_% of shots taken from 3", "OPP_OReb"],
    "Rebounding": ["OReb", "DReb"],
    "Ball Movement": ["AST", "TO", "AST/FGM", "STL"],
    "Discipline": ["PF", "Foul_Diff"],   # adjust if diff column names
    "Tempo": ["Pace", "Extra_Scoring_Chances"]  # adjust if diff column names
}

# --- Function to Calculate Category Averages ---
def get_category_scores(team, df):
    row = df[df["Teams"] == team].iloc[0]
    scores = {}
    for cat, cols in categories.items():
        valid_cols = [c for c in cols if c in df.columns]
        if valid_cols:
            scores[cat] = row[valid_cols].mean()
        else:
            scores[cat] = None
    return scores

team1_scores = get_category_scores(team1, df)
team2_scores = get_category_scores(team2, df)

# League average (baseline)
league_scores = {}
for cat, cols in categories.items():
    valid_cols = [c for c in cols if c in df.columns]
    if valid_cols:
        league_scores[cat] = df[valid_cols].mean(axis=1).mean()
    else:
        league_scores[cat] = None

# --- Radar Chart ---
fig = go.Figure()

def add_trace(scores, name, color):
    fig.add_trace(go.Scatterpolar(
        r=list(scores.values()),
        theta=list(scores.keys()),
        fill='toself',
        name=name,
        line=dict(color=color)
    ))

add_trace(team1_scores, team1, "blue")
add_trace(team2_scores, team2, "red")
add_trace(league_scores, "League Avg", "gray")

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            autorange="reversed"  # so rank 1 is outside
        )
    ),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
