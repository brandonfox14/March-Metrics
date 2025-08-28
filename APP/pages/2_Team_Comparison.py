import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ------------------ Categories ------------------ #
CATEGORIES = {
    "Offense": ["Points_RANK", "FG_PERC_Rank", "FG3_PERC_Rank", "FT_PERC_Rank", "Off_eff_rank", "Off_eff_hybrid_rank"],
    "Defense": ["OPP_PPG_RANK", "OPP_FG_PERC_Rank", "OPP_FG3_PERC_Rank", "Def_eff_hybrid_rank"],
    "Rebounding": ["OReb Rank", "DReb Rank", "Rebounds Rank", "Rebound Rate Rank"],
    "Ball Movement": ["AST Rank", "TO Rank", "AST/FGM Rank", "STL Rank"],
    "Discipline": ["PF_Rank", "Foul Differential Rank"],
    "Tempo/Extras": ["Extra Scoring Chances Rank", "PTS_OFF_TURN_RANK", "FST_BREAK_RANK", "PTS_PAINT_RANK"]
}

# ------------------ Load Data ------------------ #
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()
TEAM_COL = "Teams"

# ------------------ Sidebar ------------------ #
st.sidebar.header("Select Teams")
team1 = st.sidebar.selectbox("Team 1", sorted(df[TEAM_COL].unique()))
team2 = st.sidebar.selectbox("Team 2", sorted(df[TEAM_COL].unique()))

# ------------------ Category Averaging ------------------ #
def compute_category_scores(team_row):
    scores = {}
    for cat, cols in CATEGORIES.items():
        valid = [team_row[c] for c in cols if c in team_row and pd.notna(team_row[c])]
        scores[cat] = sum(valid) / len(valid) if valid else None
    return scores

team1_data = df[df[TEAM_COL] == team1].iloc[0]
team2_data = df[df[TEAM_COL] == team2].iloc[0]

scores1 = compute_category_scores(team1_data)
scores2 = compute_category_scores(team2_data)

# ------------------ Radar Chart ------------------ #
categories = list(CATEGORIES.keys())

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=[365 - scores1[c] for c in categories],  # invert so rank 1 = far out
    theta=categories,
    fill='toself',
    name=team1
))

fig.add_trace(go.Scatterpolar(
    r=[365 - scores2[c] for c in categories],
    theta=categories,
    fill='toself',
    name=team2
))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 365])),
    showlegend=True,
    title="Team Category Comparison"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ Color Table ------------------ #
def color_for_rank(rank):
    if rank <= 150:
        return f"background-color: rgba(0, 128, 0, {1 - (rank/150):.2f})"  # gradient green
    elif rank <= 200:
        return "background-color: lightgray"
    else:
        return f"background-color: rgba(255, 0, 0, {(rank-200)/165:.2f})"  # gradient red

comparison_df = pd.DataFrame({
    "Category": categories,
    team1: [scores1[c] for c in categories],
    team2: [scores2[c] for c in categories],
}).set_index("Category")

st.dataframe(comparison_df.style.applymap(color_for_rank, subset=[team1, team2]))


