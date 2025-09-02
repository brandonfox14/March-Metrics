import streamlit as st
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ------------------------------
# Load data
# ------------------------------
@st.cache_data
def load_data():
    all_stats = pd.read_csv("Data/All_stats.csv", encoding="latin1")
    game_history = pd.read_csv("Data/Daily_predictor_excel.csv", encoding="latin1")
    return all_stats, game_history

all_stats, game_history = load_data()

# ------------------------------
# Train model
# ------------------------------
def train_predictor(game_history):
    # Encode categorical columns if any
    game_history = game_history.dropna(axis=0)  # drop missing rows

    # Dynamically select numeric features
    numeric_cols = game_history.select_dtypes(include=[np.number]).columns.tolist()
    if "Winner" not in game_history.columns:
        st.error("❌ 'Winner' column not found in game history.")
        st.stop()

    X = game_history[numeric_cols]
    y = game_history["Winner"]

    # Encode target if not numeric
    if y.dtype == "object":
        le = LabelEncoder()
        y = le.fit_transform(y)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    return model, numeric_cols

predictor_model, model_features = train_predictor(game_history)

# ------------------------------
# Generate randomized schedule
# ------------------------------
def generate_schedule(teams, conferences, num_days=160):
    schedule = []
    day_games = {d: [] for d in range(1, num_days + 1)}
    team_games = {team: [] for team in teams}

    for team in teams:
        team_conf = conferences[team]

        # Conference opponents
        conf_opponents = [t for t in teams if conferences[t] == team_conf and t != team]
        selected_conf = random.sample(conf_opponents, min(20, len(conf_opponents)))

        # Non-conference opponents
        non_conf_opponents = [t for t in teams if conferences[t] != team_conf]
        num_non_conf = random.randint(8, 12)
        selected_non_conf = random.sample(non_conf_opponents, min(num_non_conf, len(non_conf_opponents)))

        opponents = selected_conf + selected_non_conf
        random.shuffle(opponents)

        home_games = 0
        for i, opp in enumerate(opponents):
            if len(team_games[team]) >= 40:
                break

            # Randomize home/away ensuring min 15 home games
            if home_games < 15:
                home = True
            else:
                home = random.choice([True, False])

            # Assign day with constraints
            if i < len(selected_non_conf):
                day = random.randint(1, 20)  # non-conference first 20 days
            else:
                day = random.randint(21, num_days)  # conference games in the rest

            # Ensure constraints
            while (
                len(day_games[day]) >= 50 or
                any(g["Home"] == team or g["Away"] == team for g in day_games[day])
            ):
                day = random.randint(1, num_days)

            game = {
                "Day": day,
                "Home": team if home else opp,
                "Away": opp if home else team
            }
            day_games[day].append(game)
            team_games[team].append(game)
            if home:
                home_games += 1
            schedule.append(game)

    return pd.DataFrame(schedule)

teams = all_stats["Team"].unique().tolist()
conferences = dict(zip(all_stats["Team"], all_stats["Conference"]))
schedule_df = generate_schedule(teams, conferences)

# ------------------------------
# Predict outcomes
# ------------------------------
def predict_game(home_team, away_team):
    # Look up stats
    home_stats = all_stats[all_stats["Team"] == home_team].drop(columns=["Team", "Conference"])
    away_stats = all_stats[all_stats["Team"] == away_team].drop(columns=["Team", "Conference"])

    if home_stats.empty or away_stats.empty:
        return None

    # Align columns to model
    game_features = pd.DataFrame(np.abs(home_stats.values - away_stats.values), columns=home_stats.columns)
    game_features = game_features.reindex(columns=model_features, fill_value=0)

    pred = predictor_model.predict(game_features)[0]
    return home_team if pred == 1 else away_team

schedule_df["Predicted_Winner"] = schedule_df.apply(
    lambda row: predict_game(row["Home"], row["Away"]), axis=1
)

# ------------------------------
# Streamlit UI
# ------------------------------
st.title("📅 Schedule Predictor")

view_choice = st.selectbox("View By", ["Day", "Team", "Conference"])

if view_choice == "Day":
    day_choice = st.slider("Select Day", 1, 160, 1)
    st.dataframe(schedule_df[schedule_df["Day"] == day_choice])

elif view_choice == "Team":
    team_choice = st.selectbox("Select Team", teams)
    st.dataframe(schedule_df[(schedule_df["Home"] == team_choice) | (schedule_df["Away"] == team_choice)])

elif view_choice == "Conference":
    conf_choice = st.selectbox("Select Conference", all_stats["Conference"].unique())
    conf_teams = all_stats[all_stats["Conference"] == conf_choice]["Team"].tolist()
    st.dataframe(schedule_df[(schedule_df["Home"].isin(conf_teams)) | (schedule_df["Away"].isin(conf_teams))])
