import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ------------------ Load Data ------------------ #
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

# ------------------ APP ------------------ #
st.title("Team Comparison Dashboard")

df = load_data()
TEAM_COL = "Teams"   # adjust if needed

# Sidebar team selectors
st.sidebar.header("Select Teams to Compare")
team1 = st.sidebar.selectbox("Team 1", sorted(df[TEAM_COL].unique()))
team2 = st.sidebar.selectbox("Team 2", sorted(df[TEAM_COL].unique()))

# Get team data
team1_data = df[df[TEAM_COL] == team1].iloc[0]
team2_data = df[df[TEAM_COL] == team2].iloc[0]

# Display side by side stats
st.subheader("Team Comparison")
cols = st.columns(2)

with cols[0]:
    st.markdown(f"### {team1}")
    st.write(team1_data)

with cols[1]:
    st.markdown(f"### {team2}")
    st.write(team2_data)

# Example visualization: bar chart comparison
st.subheader("Field Goal % Comparison")
fig, ax = plt.subplots()
teams = [team1, team2]
fgp = [team1_data["FG%"], team2_data["FG%"]]  # adjust column name if needed
ax.bar(teams, fgp)
ax.set_ylabel("Field Goal %")
st.pyplot(fig)
