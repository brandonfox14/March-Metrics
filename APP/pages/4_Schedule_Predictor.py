# schedule_predictor_page.py
import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Data loading (use exactly your loader)
# ---------------------------
@st.cache_data
def load_data_allstats():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

@st.cache_data
def load_data_history():
    # history file you mentioned
    return pd.read_csv("Data/Daily_predictor_excel.csv", encoding="latin1")

df_all = load_data_allstats()
df_hist = load_data_history()

st.title("Schedule Predictor — Randomized Schedule + Predictions")

# ---------------------------
# Utilities to detect columns in history file
# ---------------------------
def find_column_like(df, candidates):
    """Return first matching column name in df whose lowercase contains any candidate (or exact match)."""
    cols = list(df.columns)
    for cand in candidates:
        # try exact first
        if cand in cols:
            return cand
    lower_cols = {c.lower(): c for c in cols}
    for cand in candidates:
        lc = cand.lower()
        for c_lower, c_orig in lower_cols.items():
            if lc in c_lower or c_lower in lc:
                return c_orig
    return None

# Try to find common columns
home_col = find_column_like(df_hist, ["HomeTeam", "Home", "home_team", "home"])
away_col = find_column_like(df_hist, ["AwayTeam", "Away", "away_team", "away"])
home_score_col = find_column_like(df_hist, ["HomeScore", "Home_Score", "home_score", "Score_Home", "Hscore"])
away_score_col = find_column_like(df_hist, ["AwayScore", "Away_Score", "away_score", "Score_Away", "Ascore"])
date_col = find_column_like(df_hist, ["Date", "GameDate", "game_date", "date"])

# Inform user about detection
st.markdown("**Detected historical columns**")
st.write({
    "home_col": home_col,
    "away_col": away_col,
    "home_score_col": home_score_col,
    "away_score_col": away_score_col,
    "date_col": date_col
})

# ---------------------------
# Build randomized schedule
# ---------------------------
@st.cache_data
def build_randomized_schedule(all_stats_df, days_total=100, conf_games=20, nonconf_min=8, nonconf_max=12, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    teams = all_stats_df["Teams"].dropna().unique().tolist()
    conf_map = all_stats_df.set_index("Teams")["Conference"].to_dict()

    schedule_rows = []
    for team in teams:
        team_conf = conf_map.get(team, None)
        # conference opponents
        conf_pool = [t for t in teams if t != team and conf_map.get(t) == team_conf]
        # If not enough opponents, allow sampling with replacement
        if len(conf_pool) == 0:
            conf_opps = []
        else:
            if len(conf_pool) >= conf_games:
                conf_opps = random.sample(conf_pool, conf_games)
            else:
                # sample with replacement
                conf_opps = [random.choice(conf_pool) for _ in range(conf_games)]

        # non-conf opponents
        nonconf_pool = [t for t in teams if t != team and conf_map.get(t) != team_conf]
        n_nonconf = random.randint(nonconf_min, nonconf_max)
        if len(nonconf_pool) == 0:
            nonconf_opps = []
        else:
            if len(nonconf_pool) >= n_nonconf:
                nonconf_opps = random.sample(nonconf_pool, n_nonconf)
            else:
                nonconf_opps = [random.choice(nonconf_pool) for _ in range(n_nonconf)]

        # assign days and home/away
        # non-conf on days 1..20
        for opp in nonconf_opps:
            day = random.randint(1, min(20, days_total))
            home = random.choice([True, False])
            home_team = team if home else opp
            away_team = opp if home else team
            schedule_rows.append({
                "Day": int(day),
                "Home": home_team,
                "Away": away_team,
                "Conference_Game": False,
                "Team": team  # anchor team for reference (team's schedule)
            })

        # conf games on days 21..days_total
        for i, opp in enumerate(conf_opps):
            day = random.randint(21, days_total)
            home = random.choice([True, False])
            home_team = team if home else opp
            away_team = opp if home else team
            schedule_rows.append({
                "Day": int(day),
                "Home": home_team,
                "Away": away_team,
                "Conference_Game": True,
                "Team": team
            })

    schedule_df = pd.DataFrame(schedule_rows)
    # normalize day type and sort
    schedule_df = schedule_df.drop_duplicates(subset=["Day", "Home", "Away"]).reset_index(drop=True)
    return schedule_df

schedule_df = build_randomized_schedule(df_all, days_total=100, conf_games=20)

st.success(f"Random schedule generated: {len(schedule_df)} games total ({len(schedule_df['Home'].unique())} unique home teams)")

# ---------------------------
# Train a simple ML model on history (if possible)
# ---------------------------
@st.cache_data
def train_predictor(history_df, teams_stats_df):
    """
    Tries to build features from history by merging team-level stats for home and away teams
    Returns a pipeline (model) and the feature columns used
    """
    # Validate we have required columns
    if not home_col or not away_col or not home_score_col or not away_score_col:
        return None, None, "history_columns_missing"

    hist = history_df.copy()
    # Build a binary target 'home_win'
    hist["home_score_num"] = pd.to_numeric(hist[home_score_col], errors="coerce")
    hist["away_score_num"] = pd.to_numeric(hist[away_score_col], errors="coerce")
    hist = hist.dropna(subset=["home_score_num", "away_score_num"]).copy()
    hist["home_win"] = (hist["home_score_num"] > hist["away_score_num"]).astype(int)

    # Merge team stats for home and away
    # choose numeric columns from teams_stats_df as features
    numeric_cols = teams_stats_df.select_dtypes(include=[np.number]).columns.tolist()
    # remove columns that are obviously not team-level (e.g., index) keep 'Average Ranking' etc. If 'Teams' present drop it
    numeric_cols = [c for c in numeric_cols if c != "index"]  # safe-guard
    # prepare home and away features
    home_feat = teams_stats_df.set_index("Teams")[numeric_cols].add_prefix("home_")
    away_feat = teams_stats_df.set_index("Teams")[numeric_cols].add_prefix("away_")

    # try to merge; detect column names in hist for home/away team labels
    hist_merged = hist.merge(home_feat, left_on=home_col, right_index=True, how="left")
    hist_merged = hist_merged.merge(away_feat, left_on=away_col, right_index=True, how="left")

    # drop rows with missing features
    feature_cols = [c for c in hist_merged.columns if c.startswith("home_") or c.startswith("away_")]
    hist_merged = hist_merged.dropna(subset=feature_cols + ["home_win"])

    if hist_merged.shape[0] < 50:
        # not enough rows to train reliably
        return None, None, "not_enough_history"

    X = hist_merged[feature_cols]
    y = hist_merged["home_win"].astype(int)

    # Simple pipeline
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=200, random_state=0))
    ])
    model.fit(X, y)
    return model, feature_cols, None

model, feature_cols, train_err = train_predictor(df_hist, df_all)

if train_err:
    if train_err == "history_columns_missing":
        st.warning("Historical dataset is missing expected Home/Away/score columns. ML predictor is disabled; predictions will use a baseline heuristic.")
    elif train_err == "not_enough_history":
        st.warning("Not enough merged historical rows to train a model. ML predictor is disabled; predictions will use a baseline heuristic.")
else:
    st.success("ML predictor trained on historical data.")

# ---------------------------
# Prediction function for schedule games
# ---------------------------
def predict_game(home, away, model, feature_cols, teams_stats_df):
    # Baseline: if model missing, use simple heuristic using Average Ranking if available
    if model is None or feature_cols is None:
        # Try to use 'Average Ranking' (lower better)
        if "Average Ranking" in teams_stats_df.columns:
            try:
                hr = float(teams_stats_df.loc[teams_stats_df["Teams"] == home, "Average Ranking"].values[0])
                ar = float(teams_stats_df.loc[teams_stats_df["Teams"] == away, "Average Ranking"].values[0])
                # translate to probability (simple)
                diff = (ar - hr)  # if hr < ar team home is better => positive diff
                prob_home = 1 / (1 + np.exp(-diff/50))  # temperature scaling
                return float(prob_home)
            except Exception:
                return 0.5
        return 0.5

    # otherwise build feature vector
    numeric_cols = [c for c in teams_stats_df.select_dtypes(include=[np.number]).columns.tolist()]
    numeric_cols = [c for c in numeric_cols if c != "index"]
    home_feats = teams_stats_df.set_index("Teams").loc[home, numeric_cols].add_prefix("home_")
    away_feats = teams_stats_df.set_index("Teams").loc[away, numeric_cols].add_prefix("away_")
    # create vector in feature_cols order
    Xrow = pd.concat([home_feats, away_feats], axis=0)
    Xrow = Xrow.reindex(feature_cols).fillna(0).values.reshape(1, -1)
    prob = model.predict_proba(Xrow)[0,1]
    return float(prob)

# ---------------------------
# Predict entire schedule
# ---------------------------
@st.cache_data
def predict_schedule(schedule_df, model, feature_cols, teams_stats_df):
    rows = []
    for _, row in schedule_df.iterrows():
        home = row["Home"]
        away = row["Away"]
        day = int(row["Day"])
        prob_home = predict_game(home, away, model, feature_cols, teams_stats_df)
        winner = home if prob_home >= 0.5 else away
        rows.append({
            "Day": day,
            "Home": home,
            "Away": away,
            "Prob_Home_Win": prob_home,
            "Pred_Winner": winner,
            "Conference_Game": row.get("Conference_Game", False)
        })
    return pd.DataFrame(rows)

pred_df = predict_schedule(schedule_df, model if model is not None else None, feature_cols, df_all)

# ---------------------------
# UI: selectors to view predictions
# ---------------------------
st.sidebar.header("View options")
view_by = st.sidebar.selectbox("View by", ["Day", "Team", "Conference"])

if view_by == "Day":
    day_sel = st.sidebar.slider("Select Day", min_value=int(pred_df["Day"].min()), max_value=int(pred_df["Day"].max()), value=int(pred_df["Day"].min()))
    view_df = pred_df[pred_df["Day"] == day_sel].copy()
elif view_by == "Team":
    team_sel = st.sidebar.selectbox("Select Team", sorted(df_all["Teams"].unique()))
    view_df = pred_df[(pred_df["Home"] == team_sel) | (pred_df["Away"] == team_sel)].copy()
else:  # Conference
    conf_sel = st.sidebar.selectbox("Select Conference", sorted(df_all["Conference"].dropna().unique()))
    # Find teams in conf
    teams_in_conf = df_all[df_all["Conference"] == conf_sel]["Teams"].unique()
    view_df = pred_df[(pred_df["Home"].isin(teams_in_conf)) | (pred_df["Away"].isin(teams_in_conf))].copy()

st.header("Predicted Games")
st.write(f"Showing {len(view_df)} games for filter: {view_by}")
if view_df.empty:
    st.info("No games found for this filter.")
else:
    # show sorted by day then prob
    view_df = view_df.sort_values(["Day", "Prob_Home_Win"], ascending=[True, False]).reset_index(drop=True)
    # add nice columns
    view_df["Prob_Home_Win_pct"] = (view_df["Prob_Home_Win"]*100).round(1).astype(str) + "%"
    view_df["Pred_Winner_Label"] = view_df["Pred_Winner"]
    display_cols = ["Day", "Home", "Away", "Prob_Home_Win_pct", "Pred_Winner_Label", "Conference_Game"]
    st.dataframe(view_df[display_cols], use_container_width=True)

    # quick aggregate visual: probability histogram for the filtered set
    fig = px.histogram(view_df, x="Prob_Home_Win", nbins=20, title="Distribution of Home Win Probabilities")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Export / download option
# ---------------------------
@st.cache_data
def make_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")

csv_bytes = make_csv_bytes(pred_df)
st.download_button("Download full predictions CSV", data=csv_bytes, file_name="predicted_schedule.csv", mime="text/csv")


