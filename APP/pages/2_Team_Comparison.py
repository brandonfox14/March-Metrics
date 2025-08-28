import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    # ✅ Make sure this CSV is in the APP/ folder or adjust path
    return pd.read_csv("Data/All_stats.csv")  

df = load_data()

# ----------------------------
# Category Definitions
# ----------------------------
categories = {
    "Offense": ["Points", "FG%", "3P%", "FT%", "Off_Efficiency"],
    "Defense": ["Opp_PPG", "Opp_FG%", "Opp_3P%", "Def_Efficiency"],
    "Rebounding": ["OReb", "DReb", "Rebound_Rate"],
    "Ball Movement": ["AST", "TO", "AST/FGM", "STL"],
    "Discipline": ["PF", "Foul_Diff"],
    "Tempo": ["Pace", "Extra_Scoring_Opportunities"]
}

# Columns we don’t want in the radar
exclude_cols = ["SOS_*", "Top7", "Clutch"]

# ----------------------------
# Helper: Compute Category Averages
# ----------------------------
def compute_category_scores(team_name):
    team_row = df[df["Team"] == team_name]
    scores = {}
    for cat, cols in categories.items():
        valid_cols = [c for c in cols if c in team_row.columns]
        if len(valid_cols) > 0:
            scores[cat] = team_row[valid_cols].mean(axis=1).values[0]
        else:
            scores[cat] = None
    return scores

# ----------------------------
# Streamlit Layout
# ----------------------------
st.title("Team Comparison")

team1 = st.selectbox("Select Team 1", df["Team"].unique())
team2 = st.selectbox("Select Team 2", df["Team"].unique())

if team1 and team2:
    scores1 = compute_category_scores(team1)
    scores2 = compute_category_scores(team2)

    categories_list = list(categories.keys())

    # Radar Chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(scores1.values()),
        theta=categories_list,
        fill='toself',
        name=team1
    ))

    fig.add_trace(go.Scatterpolar(
        r=list(scores2.values()),
        theta=categories_list,
        fill='toself',
        name=team2
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                autorange="reversed"  
            )
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Supporting Comparison Table
    st.subheader("Category Scores")
    comparison_df = pd.DataFrame({
        "Category": categories_list,
        team1: list(scores1.values()),
        team2: list(scores2.values())
    })
    st.dataframe(comparison_df, use_container_width=True)

