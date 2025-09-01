import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Top 7 Player Contribution Analysis")

@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# Dropdown to select team
teams = sorted(df["Teams"].unique())
team_choice = st.selectbox("Select a Team", teams)

# Filter data
team_df = df[df["Teams"] == team_choice]

# Drop unnecessary columns
drop_cols = [
    "FGM_TOP7","FGA-Top7","FG3sM-Top7","FG3sA-Top7","FTM-Top7","FTA-Top7",
    "FGM-Top7-Perc","FGA-Top7-Perc","FG3sM-Top7-Perc","FG3sA-Top7-Perc",
    "FTM-Top7-Perc","FTA-Top7-Perc"
]
team_df = team_df.drop(columns=[c for c in drop_cols if c in team_df.columns])

# Columns to convert to percentages
percent_cols = [
    "FG_PERC-Top7","FG3_PERC-Top7","FT_PERC-Top7",
    "FG_PERC_Top7_per","FG3_PERC_Top7_per","FT_PERC_Top7_per",
    "OReb-Top7-Perc","DReb-Top7-Perc","Rebounds-Top7-Perc",
    "AST-Top7-Perc","TO-Top7-Perc","STL-Top7-Perc","Points-Top7-Perc"
]

for col in percent_cols:
    if col in team_df.columns:
        team_df[col] = team_df[col] * 100

# --- Summary Table 1: Raw Stats ---
summary_stats = [
    "FG_PERC-Top7","FG3_PERC-Top7","FT_PERC-Top7",
    "OReb-Top7","DReb-Top7","Rebounds-Top7",
    "AST-Top7","TO-Top7","STL-Top7","Points per Game-Top7"
]

summary1 = team_df[summary_stats].T.reset_index()
summary1.columns = ["Stat", "Team Value"]

st.subheader(f"{team_choice} – Top 7 Player Stats")
st.dataframe(summary1)

# --- Summary Table 2: Percentages of Team ---
summary_perc = [
    "FG_PERC_Top7_per","FG3_PERC_Top7_per","FT_PERC_Top7_per",
    "OReb-Top7-Perc","DReb-Top7-Perc","Rebounds-Top7-Perc",
    "AST-Top7-Perc","TO-Top7-Perc","STL-Top7-Perc",
    "Points-Top7-Perc","Start Percentage top 7"
]

summary2 = team_df[summary_perc].T.reset_index()
summary2.columns = ["Stat", "Team % of Total"]

st.subheader(f"{team_choice} – Top 7 Contribution to Team (%)")
st.dataframe(summary2)

# --- Visualization: Bar + Line Chart ---
rank_cols = [s + "_Rank" for s in summary_stats if s + "_Rank" in team_df.columns]

if rank_cols:
    melted = []
    for stat, rank in zip(summary_stats, rank_cols):
        if stat in team_df.columns:
            melted.append({
                "Stat": stat,
                "Team Value": team_df.iloc[0][stat],
                "Rank": team_df.iloc[0][rank]
            })

    compare_df = pd.DataFrame(melted)

    fig = go.Figure()

    # Bar chart
    fig.add_trace(go.Bar(
        x=compare_df["Stat"],
        y=compare_df["Team Value"],
        name="Team Value"
    ))

    # Line chart (Ranks)
    fig.add_trace(go.Scatter(
        x=compare_df["Stat"],
        y=compare_df["Rank"],
        mode="lines+markers",
        name="Rank",
        yaxis="y2"
    ))

    # Dual y-axis
    fig.update_layout(
        title=f"{team_choice} – Top 7 Player Stats with Ranks",
        xaxis_title="Stat",
        yaxis_title="Team Value",
        yaxis2=dict(
            title="Rank (1=Best)",
            overlaying="y",
            side="right",
            autorange="reversed"  # Rank 1 at top
        ),
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)
