import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Data/All_stats.csv", encoding="latin1")
    df.columns = df.columns.str.strip()  # clean headers
    return df

df = load_data()

# --- HEADER WITH LOGO + TITLE ---
col1, col2 = st.columns([3,1])

with col1:
    st.title("March Metrics")

with col2:
    st.image("Assets/FullLogo.png", use_container_width=True)

# --- HIGHLIGHTED TEAM ---
best_team = df.loc[df["STAT_STREN"].idxmin()]

st.subheader("Highlighted Team")
st.markdown(
    f"""
    <div style="padding:15px; border-radius:12px; background-color:#ffffff; 
                color:#000000; box-shadow:0px 4px 10px rgba(0,0,0,0.15); text-align:center;">
        <h2 style="margin:0;">{best_team['Teams']}</h2>
        <p style="margin:5px 0;">Wins: {best_team['Wins']} | Losses: {best_team['Losses']}</p>
        <p style="margin:5px 0; font-weight:bold; color:#2E86C1;">
            Statistical Strength: {best_team['STAT_STREN']}
        </p>
        <p style="margin:5px 0; font-weight:bold; color:#117A65;">
            Avg Scoring Margin: {best_team['SM']}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Confidentiality Note
st.info("This is not the full dataset. This example app is built for portfolio purposes only to maintain business confidentiality.")

st.divider()

# --- NAVIGATION CARDS ---
st.subheader("📊 Explore the Data")
cols = st.columns(3)

# Navigation Card Function
def nav_card(title, desc, color, page_path):
    st.markdown(
        f"""
        <a href="/{page_path}" target="_self" style="text-decoration:none;">
            <div style="padding:15px; border-radius:12px; background-color:{color}; 
                        box-shadow:0px 4px 8px rgba(0,0,0,0.1); text-align:center; color:black;">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

with cols[0]:
    nav_card("Team Breakdown", "Dive into detailed team stats.", "#E8F8F5")

with cols[1]:
    nav_card("Team Comparison", "Compare stats across multiple teams side by side.", "#FDEDEC")

with cols[2]:
    nav_card("Clutch Performance", "Who delivers when the game is on the line?", "#FEF9E7")

# second row of cards for the other pages
cols2 = st.columns(2)

with cols2[0]:
    nav_card("Schedule Predictor", "Explore randomized schedules and projections.", "#EBF5FB")

with cols2[1]:
    nav_card("Players", "Analyze core player stats and contributions.", "#F9EBEA")
