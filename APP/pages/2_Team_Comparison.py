import streamlit as st
import pandas as pd

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()

# Determine team column name
TEAM_COL = "Teams" if "Teams" in df.columns else ("Team" if "Team" in df.columns else df.columns[0])

# ----------------------------
# Page header + selectors
# ----------------------------
st.title("Team Comparison — Full Stats")

col_a, col_b = st.columns(2)
with col_a:
    team1 = st.selectbox("Team 1", sorted(df[TEAM_COL].unique()), key="team1")
with col_b:
    team2 = st.selectbox("Team 2", sorted(df[TEAM_COL].unique()), index=1, key="team2")

if team1 == team2:
    st.warning("Please select two different teams to compare.")
    st.stop()

# ----------------------------
# Filter out unwanted columns (clutch, top7, sos)
# ----------------------------
cols_to_keep = [
    c for c in df.columns 
    if not any(bad in str(c).lower() for bad in ["clutch", "top7", "sos"])
]
df = df[cols_to_keep]

# ----------------------------
# Pull rows for selected teams
# ----------------------------
row1 = df[df[TEAM_COL] == team1]
row2 = df[df[TEAM_COL] == team2]

if row1.empty or row2.empty:
    st.error("One of the selected teams was not found in the data.")
    st.stop()

s1 = row1.iloc[0]
s2 = row2.iloc[0]

# ----------------------------
# Build comparison DataFrame
# ----------------------------
comp = pd.DataFrame({team1: s1, team2: s2})
comp = comp.loc[df.columns]  # preserve order

# ----------------------------
# Format helper
# ----------------------------
def format_pair(col, v):
    try:
        f = float(v)
        if ("PERC" in str(col).upper()) or ("% of" in str(col)) or (f <= 1 and "PERC" not in str(col).upper()):
            return f"{f*100:.1f}%" if f <= 1 else f"{f:.1f}%"
        else:
            return f"{f:.1f}"
    except Exception:
        return v

display = comp.copy()
for col in display.index:
    display.at[col, team1] = format_pair(col, display.at[col, team1])
    display.at[col, team2] = format_pair(col, display.at[col, team2])

display_df = display.reset_index().rename(columns={"index": "Statistic"})

# ----------------------------
# Render
# ----------------------------
st.subheader("All stats (side-by-side)")
st.dataframe(display_df, use_container_width=True)

# ----------------------------
# Quick snapshot (key stats only)
# ----------------------------
key_stats = ["Points", "FG_PERC", "FT_PERC", "OReb", "DReb", "AST", "TO", "SM", "Off_eff", "OPP_PPG"]
present_keys = [k for k in key_stats if k in df.columns]

if present_keys:
    st.subheader("Quick snapshot")
    left, right = st.columns(2)
    with left:
        st.markdown(f"#### {team1}")
        for k in present_keys:
            st.write(f"**{k}:** {format_pair(k, s1.get(k, ''))}")
    with right:
        st.markdown(f"#### {team2}")
        for k in present_keys:
            st.write(f"**{k}:** {format_pair(k, s2.get(k, ''))}")
