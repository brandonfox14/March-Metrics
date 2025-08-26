import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------
# Data Loader
# ----------------------
@st.cache_data
def load_data():
    # Build correct path (case-sensitive on Streamlit Cloud)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "Data", "All_stats.xlsx")
    return pd.read_excel(data_path)

df = load_data()

# ----------------------
# Main Page Layout
# ----------------------
st.set_page_config(
    page_title="March Metrics",
    page_icon="🏀",
    layout="wide"
)

# Title & intro
st.title("🏀 March Metrics: College Basketball Analytics")
st.markdown(
    """
    Welcome to **March Metrics** — your all-in-one dashboard for college basketball stats & insights.  
    Use the sidebar to navigate between pages (Teams, Players, Games, Predictions).  
    """
)

# ----------------------
# Team Selector
# ----------------------
teams = df['Team'].dropna().unique()
team_choice = st.selectbox("Select a Team:", sorted(teams))

team_data = df[df['Team'] == team_choice]

# ----------------------
# Summary Stats
# ----------------------
st.subheader(f"📊 Season Summary: {team_choice}")

if not team_data.empty:
    wins = team_data['Wins'].iloc[0] if 'Wins' in team_data.columns else "N/A"
    losses = team_data['Losses'].iloc[0] if 'Losses' in team_data.columns else "N/A"
    avg_points = team_data['Points'].mean() if 'Points' in team_data.columns else 0
    avg_allowed = team_data['Opponent Points'].mean() if 'Opponent Points' in team_data.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Wins", wins)
    col2.metric("Losses", losses)
    col3.metric("Avg Points Scored", f"{avg_points:.1f}")
    col4.metric("Avg Points Allowed", f"{avg_allowed:.1f}")

# ----------------------
# Chart: Scoring Trends
# ----------------------
if 'Game Number' in team_data.columns and 'Points' in team_data.columns:
    st.subheader("📈 Scoring Trend")
    fig, ax = plt.subplots()
    ax.plot(team_data['Game Number'], team_data['Points'], marker="o", label="Points Scored")
    if 'Opponent Points' in team_data.columns:
        ax.plot(team_data['Game Number'], team_data['Opponent Points'], marker="x", label="Points Allowed")
    ax.set_xlabel("Game #")
    ax.set_ylabel("Points")
    ax.legend()
    st.pyplot(fig)

# ----------------------
# Footer
# ----------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Data: College Basketball Stats")
