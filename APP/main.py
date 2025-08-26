import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data (adjust path & file type)
@st.cache_data
def load_data():
    return pd.read_excel("Data/All_stats.xlsx")

df = load_data()

# Main Page
st.title("🏀 College Basketball Analytics Dashboard")

st.write("Welcome to the College Basketball Analytics app! Explore team stats, player performance, game breakdowns, and custom March Metrics.")

# Team selector
teams = df['Team'].unique()
team_choice = st.selectbox("Select a Team:", teams)

team_data = df[df['Team'] == team_choice]

# Summary stats
st.subheader(f"Season Summary: {team_choice}")
st.write(f"Wins: {team_data['Wins'].iloc[0]}, Losses: {team_data['Losses'].iloc[0]}")
st.write(f"Avg Points Scored: {team_data['Points'].mean():.1f}")
st.write(f"Avg Points Allowed: {team_data['Opponent Points'].mean():.1f}")

# Chart example
st.subheader("Scoring Trend")
fig, ax = plt.subplots()
ax.plot(team_data['Game Number'], team_data['Points'], label="Points Scored")
ax.plot(team_data['Game Number'], team_data['Opponent Points'], label="Points Allowed")
ax.set_xlabel("Game #")
ax.set_ylabel("Points")
ax.legend()
st.pyplot(fig)
