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
st.info("⚠These are randomly created games and matchups to highlight the predicted qualities that are produced. Most of the full methodology is held back as a competitive advantage, but this example ties the workflow together while showing pieces of the coding approach.")

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
    nav_card("Team Breakdown", "Dive into detailed team stats and player impact.", "#E8F8F5", "Team_Breakdown")

with cols[1]:
    nav_card("Conference Projections", "See how conferences stack up against each other.", "#FDEDEC", "Conference_Projections")

with cols[2]:
    nav_card("Clutch Performance", "Who delivers when the game is on the line?", "#FEF9E7", "Clutch_Performance")


# The team being pulled from statistical strength to be white background and words black for the team because night mode messes it up
# Properly connect the links to the different pages
