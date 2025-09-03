import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# --- HEADER WITH LOGO + TITLE ---
col1, col2 = st.columns([3,1])  # ratio keeps title bigger and logo smaller

with col1:
    st.title("March Metrics")

with col2:
    st.image("Assets/FullLogo.png", use_container_width=True)

# --- HIGHLIGHTED TEAM ---
# Pick team with *lowest* Statistical Strength value
best_team = df.loc[df["Statistical Strength "].idxmin()]

st.subheader("Highlighted Team")
st.markdown(
    f"""
    <div style="padding:15px; border-radius:12px; background-color:#FFFFFF; 
                box-shadow:0px 4px 10px rgba(0,0,0,0.15); text-align:center; color:#000000;">
        <h2 style="margin:0; color:#000000;">{best_team['Teams']}</h2>
        <p style="margin:5px 0; color:#000000;">Wins: {best_team['Wins']} | Losses: {best_team['Losses']}</p>
        <p style="margin:5px 0; font-weight:bold; color:#2E86C1;">
            Statistical Strength: {best_team['Statistical Strength']}
        </p>
        <p style="margin:5px 0; font-weight:bold; color:#117A65;">
            Avg Scoring Margin: {best_team['SM']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Confidentiality Note
st.info("⚠️ This is not the full dataset. This example app is built for portfolio purposes only to maintain business confidentiality.")

st.divider()

# --- NAVIGATION CARDS ---
st.subheader("📊 Explore the Data")

cols = st.columns(3)

with cols[0]:
    st.markdown(
        """
        <a href="/Team_Breakdown" target="_self" style="text-decoration:none;">
            <div style="padding:15px; border-radius:12px; background-color:#E8F8F5; 
                        box-shadow:0px 4px 8px rgba(0,0,0,0.1); text-align:center; color:black;">
                <h3>Team Breakdown</h3>
                <p>Dive into detailed team stats and player impact.</p>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

with cols[1]:
    st.markdown(
        """
        <a href="/Conference_Projections" target="_self" style="text-decoration:none;">
            <div style="padding:15px; border-radius:12px; background-color:#FDEDEC; 
                        box-shadow:0px 4px 8px rgba(0,0,0,0.1); text-align:center; color:black;">
                <h3>Conference Projections</h3>
                <p>See how conferences stack up against each other.</p>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

with cols[2]:
    st.markdown(
        """
        <a href="/Clutch_Performance" target="_self" style="text-decoration:none;">
            <div style="padding:15px; border-radius:12px; background-color:#FEF9E7; 
                        box-shadow:0px 4px 8px rgba(0,0,0,0.1); text-align:center; color:black;">
                <h3>Clutch Performance</h3>
                <p>Who delivers when the game is on the line?</p>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
