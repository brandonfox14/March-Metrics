import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# -----------------------
# Load data
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Data/All_stats.csv", encoding="latin1")
    # clean headers just in case
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# -----------------------
# Helpers / formatting
# -----------------------
def format_value(key_or_label, val):
    """Format numeric or percent values for display."""
    if pd.isna(val):
        return "N/A"
    try:
        v = float(val)
    except Exception:
        return str(val)
    # treat as percent if key/label indicates percent
    if ("PERC" in str(key_or_label).upper()) or ("%" in str(key_or_label)):
        # if stored as fraction (<=1) show 0-100%, else assume already 0-100
        return f"{v:.1%}" if v <= 1 else f"{v:.1f}%"
    # integer-friendly formatting
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.1f}"

def format_rank(val):
    """Right-column rank formatting."""
    if val is None:
        return "No rank mapping defined"
    if pd.isna(val) or val == "N/A":
        return "Not enough games played for ranking"
    try:
        return int(float(val))
    except Exception:
        return val

def robust_normalize(df_section: pd.DataFrame) -> pd.DataFrame:
    """Normalize each column to [0,1] with robust handling of constant or empty columns."""
    out = pd.DataFrame(index=df_section.index, columns=df_section.columns, dtype=float)
    for c in df_section.columns:
        col = pd.to_numeric(df_section[c], errors='coerce')
        if col.dropna().empty:
            out[c] = 0.5
            continue
        mn = col.min(skipna=True)
        mx = col.max(skipna=True)
        if pd.isna(mn) or pd.isna(mx) or mx == mn:
            out[c] = 0.5
        else:
            out[c] = (col - mn) / (mx - mn)
    return out

def find_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first existing column from candidates (exact match), else None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

# -----------------------
# Default team selection: most Wins (fallbacks to first)
# -----------------------
teams_sorted = sorted(df["Teams"].dropna().unique().tolist())
default_index = 0
if "Wins" in df.columns:
    wins = pd.to_numeric(df["Wins"], errors="coerce")
    if wins.notna().any():
        try:
            default_team_raw = df.at[wins.idxmax(), "Teams"]
            if default_team_raw in teams_sorted:
                default_index = teams_sorted.index(default_team_raw)
        except Exception:
            pass

selected_team = st.selectbox("Select a Team", teams_sorted, index=default_index)
team_row = df[df["Teams"] == selected_team].iloc[0]
team_conf = team_row.get("Conference", None)

# -----------------------
# Top note (per your request)
# -----------------------
st.info("ℹ️ **Right column shows the team’s ranking for that stat** (1 = best). "
        "If a rank isn’t available in the dataset, you’ll see a note instead.")

# -----------------------
# Section definitions with explicit, adjustable mappings
# (label, stat column candidates, rank column candidates)
# -----------------------
offense_defs = [
    {"label": "Points Per Game", "stat": ["Points"], "rank": ["Points_RANK", "Points_Rank"]},
    {"label": "Field Goal Percentage", "stat": ["FG_PERC"], "rank": ["FG_PERC_Rank", "FG_PERC_RANK"]},
    {"label": "Field Goals Made per Game", "stat": ["FGM/G"], "rank": ["FGM/G_Rank", "FGM/G_RANK"]},
    {"label": "3 Point Field Goal Percentage", "stat": ["FG3_PERC"], "rank": ["FG3_PERC_Rank", "FG3_PERC_RANK"]},
    {"label": "3 Point Field Goals Made per Game", "stat": ["FG3M/G"], "rank": ["FG3M/G_Rank", "FG3M/G_RANK"]},
    {"label": "Free Throw Percentage", "stat": ["FT_PERC"], "rank": ["FT_PERC_Rank", "FT_PERC_RANK"]},
    {"label": "Free Throws Made per Game", "stat": ["FTM/G"], "rank": ["FTM/G_RANK", "FTM/G_Rank"]},
    {"label": "Percent of Points from 3", "stat": ["% of Points from 3"],
     "rank": ["% of Points from 3_RANK", "% of Points from 3_Rank"]},
    {"label": "Percent of Shots Taken from 3", "stat": ["% of shots taken from 3"],
     "rank": ["% of shots taken from 3_RANK", "% of shots taken from 3_Rank"]},
]

defense_defs = [
    {"label": "Opponent Points Per Game", "stat": ["OPP_PPG"], "rank": ["OPP_PPG_RANK", "OPP_PPG_Rank"]},
    {"label": "Opponent Field Goal Percentage", "stat": ["OPP_FG_PERC"], "rank": ["OPP_FG_PERC_Rank", "OPP_FG_PERC_RANK"]},
    {"label": "Opponent FGM per Game", "stat": ["OPP_FGM/G"], "rank": ["OPP_FGM/G_Rank", "OPP_FGM/G_RANK"]},
    {"label": "Opponent 3PT Percentage", "stat": ["OPP_FG3_PERC"], "rank": ["OPP_FG3_PERC_Rank", "OPP_FG3_PERC_RANK"]},
    {"label": "Opponent 3PTM per Game", "stat": ["OPP_FG3M/G"], "rank": ["OPP_FG3M/G_Rank", "OPP_FG3M/G_RANK"]},
    {"label": "Opponent % of Points from 3", "stat": ["OPP_% of Points from 3"],
     "rank": ["OPP_% of Points from 3_RANK", "OPP_% of Points from 3 rank", "OPP_% of Points from 3_Rank"]},
    {"label": "Opponent % of Shots Taken from 3", "stat": ["OPP_% of shots taken from 3"],
     "rank": ["OPP_% of shots taken from 3_RANK", "OPP_% of shots taken from 3 Rank", "OPP_% of shots taken from 3_Rank"]},
    {"label": "Opponent Offensive Rebounds", "stat": ["OPP_OReb"], "rank": ["OPP_OReb_RANK", "OPP_OReb_Rank"]},
]

other_defs = [
    {"label": "Offensive Rebounds", "stat": ["OReb"], "rank": ["OReb Rank", "OReb_RANK"]},
    {"label": "Offensive Rebound Chances", "stat": ["OReb chances", "OReb_chances"],
     "rank": ["OReb chances Rank", "OReb_chances Rank", "OReb chances_Rank"]},
    {"label": "Defensive Rebounds", "stat": ["DReb"], "rank": ["DReb Rank", "DReb_RANK"]},
    {"label": "Total Rebounds", "stat": ["Rebounds"], "rank": ["Rebounds Rank", "Rebounds_RANK"]},
    {"label": "Rebound Rate", "stat": ["Rebound Rate"], "rank": ["Rebound Rate Rank", "Rebound Rate_Rank"]},
    {"label": "Assists", "stat": ["AST"], "rank": ["AST Rank", "AST_RANK"]},
    {"label": "Assists per Field Goal Made", "stat": ["AST/FGM"], "rank": ["AST/FGM Rank", "AST/FGM_Rank"]},
    {"label": "Turnovers", "stat": ["TO"], "rank": ["TO Rank", "TO_RANK"]},
    {"label": "Steals", "stat": ["STL"], "rank": ["STL Rank", "STL_RANK"]},
]

extras_defs = [
    {"label": "Extra Scoring Chances", "stat": ["Extra Scoring Chances"],
     "rank": ["Extra Scoring Chances Rank", "Extra Scoring Chances_Rank"]},
    {"label": "Points Off Turnovers", "stat": ["PTS_OFF_TURN"], "rank": ["PTS_OFF_TURN_RANK", "PTS_OFF_TURN_Rank"]},
    {"label": "Fast Break Points", "stat": ["FST_BREAK"], "rank": ["FST_BREAK_RANK", "FST_BREAK_Rank"]},
    {"label": "Points in Paint", "stat": ["PTS_PAINT"], "rank": ["PTS_PAINT_RANK", "PTS_PAINT_Rank"]},
    {"label": "Personal Fouls", "stat": ["PF"], "rank": ["PF_Rank", "PF_RANK"]},
    {"label": "Foul Differential", "stat": ["Foul Differential"], "rank": ["Foul Differential Rank", "Foul Differential_Rank"]},
]

# -----------------------
# Section builder
# -----------------------
def build_section_chart(section_defs: list[dict], section_title: str):
    st.header(f"{selected_team} {section_title}")

    # Determine which columns will actually be used based on availability
    used = []  # list of dicts: label, stat_col_used, rank_col_used
    missing_stats = []
    for item in section_defs:
        stat_col = find_existing_column(df, item["stat"])
        rank_col = find_existing_column(df, item["rank"])
        used.append({
            "label": item["label"],
            "stat_col": stat_col,
            "rank_col": rank_col
        })
        if stat_col is None:
            missing_stats.append(item["label"])

    if missing_stats:
        st.warning(f"Missing stat columns for: {missing_stats}. These will be skipped in charts.")

    # Display rows (Label | Value | Rank)
    for u in used:
        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            st.markdown(f"**{u['label']}**")
        with col2:
            if u["stat_col"] is None:
                st.write("Missing")
            else:
                st.write(format_value(u["stat_col"], team_row.get(u["stat_col"], float("nan"))))
        with col3:
            if u["rank_col"] is None:
                st.write("No rank mapping defined")
            else:
                st.write(format_rank(team_row.get(u["rank_col"], pd.NA)))

    # Build normalized comparison (only for found stat columns)
    stat_cols_used = [u["stat_col"] for u in used if u["stat_col"] is not None]
    labels_used = [u["label"] for u in used if u["stat_col"] is not None]

    if len(stat_cols_used) == 0:
        st.info("No available columns for chart in this section.")
        return

    section_df = df[stat_cols_used].apply(pd.to_numeric, errors="coerce")
    normalized = robust_normalize(section_df)

    # team line
    team_norm_row = normalized.loc[df["Teams"] == selected_team]
    team_norm = team_norm_row.iloc[0].tolist() if team_norm_row.shape[0] > 0 else [0.5] * len(stat_cols_used)

    # conference line
    conf_norm = None
    if team_conf and "Conference" in df.columns:
        conf_rows = normalized[df["Conference"] == team_conf]
        if conf_rows.shape[0] > 0:
            conf_norm = conf_rows.mean(skipna=True).tolist()

    # league mean line
    league_norm = normalized.mean(skipna=True).tolist()

    # hover texts (pull raw values + ranks + aggregates)
    hover_texts = []
    for u in used:
        if u["stat_col"] is None:
            continue
        val = team_row.get(u["stat_col"], float("nan"))
        rank_val = format_rank(team_row.get(u["rank_col"], pd.NA)) if u["rank_col"] else "No rank mapping defined"
        col_min = section_df[u["stat_col"]].min(skipna=True)
        col_max = section_df[u["stat_col"]].max(skipna=True)
        conf_avg = df[df["Conference"] == team_conf][u["stat_col"]].mean() if team_conf and "Conference" in df.columns else float("nan")
        league_avg = section_df[u["stat_col"]].mean()
        hover_texts.append(
            f"<b>{u['label']}</b><br>"
            f"{selected_team}: {format_value(u['stat_col'], val)} (Rank: {rank_val})<br>"
            f"Min: {format_value(u['stat_col'], col_min)} — Max: {format_value(u['stat_col'], col_max)}<br>"
            f"{(team_conf + ' Avg') if team_conf else 'Conf Avg'}: {format_value(u['stat_col'], conf_avg)}<br>"
            f"League Avg: {format_value(u['stat_col'], league_avg)}"
        )

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels_used, y=team_norm, mode="lines+markers",
                             name=selected_team, hoverinfo="text", hovertext=hover_texts))
    if conf_norm is not None:
        fig.add_trace(go.Scatter(x=labels_used, y=conf_norm, mode="lines+markers",
                                 name=f"{team_conf} Avg", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=labels_used, y=league_norm, mode="lines+markers",
                             name="League Avg", line=dict(dash="dot")))

    fig.update_layout(
        title=f"{section_title} Comparison (Normalized)",
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, 1]),
        xaxis=dict(tickangle=45),
        plot_bgcolor="white",
        margin=dict(t=60, b=120)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mapping summary (for your adjustments)
    with st.expander(f"Show mapping used for {section_title}"):
        map_df = pd.DataFrame(used)
        st.dataframe(map_df, use_container_width=True)

# -----------------------
# Build sections
# -----------------------
build_section_chart(offense_defs, "Offensive Statistics")
build_section_chart(defense_defs, "Defensive Statistics")
build_section_chart(other_defs, "Rebounds / AST / TO / STL")
build_section_chart(extras_defs, "Extra Statistics")
