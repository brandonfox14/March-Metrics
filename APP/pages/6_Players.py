import streamlit as st
import pandas as pd
import plotly.express as px




@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()



# --- Team Selection ---
teams = sorted(df["Teams"].unique())
default_team = teams[0]
team_choice = st.selectbox("Select a Team", teams, index=teams.index(default_team))
team_data = df[df["Teams"] == team_choice].iloc[0]

st.header(f"Top 7 Players Summary – {team_choice}")

# --- Summary Table ---
# Stats without percentages
stats = [
    "FGM_TOP7", "FGA-Top7", "FG3sM-Top7", "FG3sA-Top7",
    "FTM-Top7", "FTA-Top7", "FG_PERC-Top7", "FG3_PERC-Top7",
    "FT_PERC-Top7", "OReb-Top7", "DReb-Top7", "Rebounds-Top7",
    "AST-Top7", "TO-Top7", "STL-Top7", "Points per Game-Top7"
]

# Percentage stats
perc_stats = [
    "FGM-Top7-Perc", "FGA-Top7-Perc", "FG3sM-Top7-Perc", "FG3sA-Top7-Perc",
    "FTM-Top7-Perc", "FTA-Top7-Perc", "FG_PERC_Top7_per", "FG3_PERC_Top7_per",
    "FT_PERC_Top7_per", "OReb-Top7-Perc", "DReb-Top7-Perc", "Rebounds-Top7-Perc",
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc", "Points-Top7-Perc"
]

summary_data = {
    "Stat": stats + perc_stats,
    "Value": [team_data[s] for s in stats + perc_stats]
}
summary_df = pd.DataFrame(summary_data)

st.dataframe(summary_df)

# --- Visual 1: Conference Comparison (Top 7 Percentages vs Conference) ---
conf = team_data["Conference"]
conf_df = df[df["Conference"] == conf]

conf_avg = conf_df[perc_stats].mean().reset_index()
conf_avg.columns = ["Stat", "Conference Average"]

team_perc = team_data[perc_stats].reset_index()
team_perc.columns = ["Stat", "Team Value"]

compare_df = pd.merge(team_perc, conf_avg, on="Stat")

fig1 = px.bar(compare_df, x="Stat", y=["Team Value", "Conference Average"],
              barmode="group", title=f"{team_choice} vs {conf} – Top 7 Percentages")
st.plotly_chart(fig1, use_container_width=True)

# --- Visual 2: Points per Game (bar + ranking line) ---
# Make sure ranking column exists (you may need to replace with actual name)
df["Points per Game-Top7-Rank"] = df["Points per Game-Top7"].rank(ascending=False)

points_df = df.sort_values("Points per Game-Top7", ascending=False).reset_index()

fig2 = px.bar(points_df, x="Teams", y="Points per Game-Top7",
              title="Top 7 Players – Points per Game with Ranking")

# Add ranking line
fig2.add_scatter(x=points_df["Teams"], y=points_df["Points per Game-Top7-Rank"],
                 mode="lines+markers", name="Rank (lower is better)", yaxis="y2")

fig2.update_layout(
    yaxis2=dict(title="Rank", overlaying="y", side="right", autorange="reversed")
)

st.plotly_chart(fig2, use_container_width=True)
