import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# ===============================
# Data loading (robust encoding)
# ===============================
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Data", "All_stats.csv")
    # Try common encodings to avoid UnicodeDecodeError
    for enc in ("ISO-8859-1", "latin1", "utf-8-sig"):
        try:
            df = pd.read_csv(data_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        # Last resort: replace bad bytes so the app never crashes
        df = pd.read_csv(data_path, encoding="latin1", on_bad_lines="skip", engine="python")
    # Standardize column names (strip)
    df.columns = [c.strip() for c in df.columns]
    # Also standardize team column name if needed
    if "Teams" in df.columns:
        team_col = "Teams"
    elif "Team" in df.columns:
        team_col = "Team"
    else:
        raise ValueError("Could not find a 'Teams' or 'Team' column in All_stats.csv")
    return df, "Teams" if "Teams" in df.columns else "Team"

df, TEAM_COL = load_data()

st.title("Team Comparison – Radar by Category Rank")

# =====================================================
# Define categories using RANK columns only (lower=better)
# Exclude SOS_*, *Top7*, and *Clutch* by not listing them
# =====================================================
CATEGORIES = {
    # Offense: core scoring efficiency & volume ranks
    "Offense": [
        "Points_RANK", "FG_PERC_Rank", "FG3_PERC_Rank", "FT_PERC_Rank",
        "FGM/G_Rank", "FG3M/G_Rank", "FTM/G_RANK",
        "Off_eff_rank", "Off_eff_hybrid_rank"
    ],
    # Defense: opponent scoring/efficiency ranks (lower is better)
    "Defense": [
        "OPP_PPG_RANK", "OPP_FG_PERC_Rank", "OPP_FG3_PERC_Rank",
        "OPP_FGM/G_Rank", "OPP_FG3M/G_Rank",
        "Def_eff_hybrid_rank"
    ],
    # Rebounding: rates and totals
    "Rebounding": [
        "OReb Rank", "DReb Rank", "Rebounds Rank", "Rebound Rate Rank"
    ],
    # Ball Movement: creation, mistakes, disruption
    "Ball Movement": [
        "AST Rank", "AST/FGM Rank", "TO Rank", "STL Rank"
    ],
    # Discipline: fouls and differential
    "Discipline": [
        "PF_Rank", "Foul Differential Rank"
    ],
    # Extra/Tempo: extra chances and style proxies
    "Extra/Tempo": [
        "Extra Scoring Chances Rank", "FTA/FGA Rank",
        "PTS_OFF_TURN_RANK", "FST_BREAK_RANK", "PTS_PAINT_RANK"
    ],
}

# Keep only columns that actually exist in the file
CATEGORIES = {
    cat: [c for c in cols if c in df.columns]
    for cat, cols in CATEGORIES.items()
}

# If any category is empty after filtering, drop it
CATEGORIES = {cat: cols for cat, cols in CATEGORIES.items() if len(cols) > 0}

# =========================
# Team selectors
# =========================
teams = sorted(df[TEAM_COL].dropna().unique().tolist())
left, right = st.columns(2)
with left:
    team1 = st.selectbox("Select Team 1", teams, index=0, key="team1")
with right:
    team2 = st.selectbox("Select Team 2", teams, index=1, key="team2")

if team1 == team2:
    st.info("Select two different teams to compare.")
    st.stop()

row1 = df[df[TEAM_COL] == team1].iloc[0]
row2 = df[df[TEAM_COL] == team2].iloc[0]

# =========================
# Helper functions
# =========================
def category_avg_rank(row: pd.Series, cols: list[str]) -> float | None:
    vals = pd.to_numeric(row[cols], errors="coerce")
    if vals.notna().sum() == 0:
        return None
    return float(vals.mean())

def league_category_avg_rank(cols: list[str]) -> float | None:
    vals = pd.to_numeric(df[cols], errors="coerce")
    vals_row_means = vals.mean(axis=1, numeric_only=True)
    if vals_row_means.notna().sum() == 0:
        return None
    return float(vals_row_means.mean())

def color_for_rank(rank: float) -> str:
    """
    Coloring rules:
      - 1..150  : green gradient (#90EE90 -> #006400)
      - 150..200: neutral gray (#BEBEBE)
      - 200+    : red gradient (#FFB6B6 -> #8B0000)
    """
    if pd.isna(rank):
        return "#FFFFFF"  # white for missing
    r = float(rank)
    if r <= 150:
        # map 1..150 to light->dark green
        t = (150 - r) / 149.0  # 0 at 150, 1 at 1
        # interpolate between (144,238,144) and (0,100,0)
        g1, g2 = np.array([144, 238, 144]), np.array([0, 100, 0])
        rgb = (g1 + t * (g2 - g1)).astype(int)
        return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
    elif 150 < r <= 200:
        return "#BEBEBE"
    else:
        # map 201..365 to light->dark red
        # clamp at 365
        r_clamp = min(r, 365.0)
        t = (r_clamp - 201.0) / (365.0 - 201.0)  # 0 at 201, 1 at 365
        r1, r2 = np.array([255, 182, 182]), np.array([139, 0, 0])
        rgb = (r1 + t * (r2 - r1)).astype(int)
        return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

# =========================
# Compute category averages
# =========================
cats = list(CATEGORIES.keys())
team1_scores = []
team2_scores = []
league_scores = []

for cat in cats:
    cols = CATEGORIES[cat]
    team1_scores.append(category_avg_rank(row1, cols))
    team2_scores.append(category_avg_rank(row2, cols))
    league_scores.append(league_category_avg_rank(cols))

# If all are None (no ranks found), stop
if all(v is None for v in team1_scores + team2_scores):
    st.error("No ranking columns found for the selected categories in All_stats.csv.")
    st.stop()

# Replace None with NaN for plotting
team1_r = [np.nan if v is None else v for v in team1_scores]
team2_r = [np.nan if v is None else v for v in team2_scores]
league_r = [np.nan if v is None else v for v in league_scores]

# =========================
# Radar chart (rank 1 outer)
# =========================
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=team1_r, theta=cats, fill='toself', name=team1, mode="lines+markers"
))
fig.add_trace(go.Scatterpolar(
    r=team2_r, theta=cats, fill='toself', name=team2, mode="lines+markers"
))
fig.add_trace(go.Scatterpolar(
    r=league_r, theta=cats, fill='toself', name="League Avg", mode="lines+markers", line=dict(dash="dot")
))

# Set a reasonable visible radial range if possible
# We assume ranks 1..365; autorange='reversed' makes 1 far out, 365 near center
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[1, 365], autorange="reversed", tickvals=[1,50,100,150,200,250,300,350])
    ),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    margin=dict(l=40, r=40, t=40, b=80),
)
st.plotly_chart(fig, use_container_width=True)

# =========================
# Color-coded per-stat table
# =========================
st.subheader("Per-stat ranks (colored)")

# Build a tall table: Category, Stat, Team1Rank, Team2Rank, LeagueAvgRank
rows = []
for cat, cols in CATEGORIES.items():
    for col in cols:
        t1 = pd.to_numeric(row1.get(col, np.nan), errors="coerce")
        t2 = pd.to_numeric(row2.get(col, np.nan), errors="coerce")
        # League avg rank for this single column:
        col_vals = pd.to_numeric(df[col], errors="coerce")
        league_col_avg = float(col_vals.mean()) if col_vals.notna().any() else np.nan
        rows.append([cat, col, t1, t2, league_col_avg])

table_df = pd.DataFrame(rows, columns=["Category", "Stat (Rank column)", team1, team2, "League Avg"])

# Build color arrays for Plotly Table
def color_col(series):
    return [color_for_rank(x) for x in series]

fill_colors = [
    ["#F7F7F7"] * len(table_df),                 # Category (neutral)
    ["#F7F7F7"] * len(table_df),                 # Stat name (neutral)
    color_col(table_df[team1]),                  # Team1 colored by rank bands
    color_col(table_df[team2]),                  # Team2 colored by rank bands
    color_col(table_df["League Avg"]),           # League avg colored by rank bands
]

fig_tbl = go.Figure(data=[go.Table(
    header=dict(
        values=list(table_df.columns),
        fill_color="#333333",
        font=dict(color="white"),
        align="left"
    ),
    cells=dict(
        values=[table_df[c] for c in table_df.columns],
        fill_color=fill_colors,
        align="left",
        format=[None, None, ".0f", ".0f", ".0f"],
        height=24
    )
)])
fig_tbl.update_layout(margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig_tbl, use_container_width=True)

st.caption(
    "Notes: Lower rank is better. Categories aggregate the mean of their listed rank columns. "
    "Excluded from this view: SOS, Top7, and Clutch-related fields."
)
