import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# --- TEAM SELECTION ---
st.header("Team Comparison")

teams = sorted(df["Teams"].unique())
col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Select Team 1", teams, index=0)
with col2:
    team2 = st.selectbox("Select Team 2", teams, index=1)

team1_data = df[df["Teams"] == team1].iloc[0]
team2_data = df[df["Teams"] == team2].iloc[0]

# --- Define Stats for Comparison ---
offense_cols = {
    "Points": "Points Per Game",
    "FG_PERC": "Field Goal Percentage",
    "FGM/G": "Field Goals Made per Game",
    "FG3_PERC": "3 Point Field Goal Percentage",
    "FG3M/G": "3 Point Field Goals Made per Game",
    "FT_PERC": "Free Throw Percentage",
    "FTM/G": "Free Throws Made per Game",
    "% of Points from 3": "% of Points from 3",
    "% of shots taken from 3": "% of Shots Taken from 3"
}

defense_cols = {
    "OPP_PPG": "Opponent Points Per Game",
    "OPP_FG_PERC": "Opponent Field Goal Percentage",
    "OPP_FGM/G": "Opponent FGM per Game",
    "OPP_FG3_PERC": "Opponent 3PT Percentage",
    "OPP_FG3M/G": "Opponent 3PTM per Game",
    "OPP_% of Points from 3": "Opponent % of Points from 3",
    "OPP_% of shots taken from 3": "Opponent % of Shots Taken from 3",
    "OPP_OReb": "Opponent Offensive Rebounds"
}

# --- Helper Function for Formatting ---
def format_value(col, val):
    if "PERC" in col or "%" in col:
        return f"{val:.1%}" if val <= 1 else f"{val:.1f}%"
    else:
        return f"{val:.1f}"

# =====================
# 📊 OFFENSE COMPARISON
# =====================
st.subheader("Offense Comparison")

for col, label in offense_cols.items():
    colA, colB, colC = st.columns([2,1,1])
    with colA:
        st.markdown(f"**{label}**")
    with colB:
        st.write(format_value(col, team1_data[col]))
    with colC:
        st.write(format_value(col, team2_data[col]))

# =====================
# 🛡️ DEFENSE COMPARISON
# =====================
st.subheader("Defense Comparison")

for col, label in defense_cols.items():
    colA, colB, colC = st.columns([2,1,1])
    with colA:
        st.markdown(f"**{label}**")
    with colB:
        st.write(format_value(col, team1_data[col]))
    with colC:
        st.write(format_value(col, team2_data[col]))


