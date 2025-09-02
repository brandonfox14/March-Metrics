import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import streamlit as st

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    all_stats = pd.read_csv("Data/All_stats.csv", encoding="latin1")
    game_history = pd.read_csv("Data/Daily_predictor_excel.csv", encoding="latin1")
    return all_stats, game_history

all_stats, game_history = load_data()

# -----------------------------
# Train basic ML model
# -----------------------------
def train_predictor(game_history):
    # Example features (adjust depending on your data schema)
    features = ["Team_FG%", "Team_PPG", "Opp_FG%", "Opp_PPG"]  
    target = "Win"  

    X = game_history[features]
    y = game_history[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    return model

predictor_model = train_predictor(game_history)

# -----------------------------
# Schedule Generator
# -----------------------------
def generate_schedule(all_stats):
    teams = all_stats["Team"].unique()
    conferences = dict(zip(all_stats["Team"], all_stats["Conference"]))

    schedule = []
    day_games_count = {d: 0 for d in range(1, 161)}  
    team_games_count = {t: 0 for t in teams}
    team_home_games = {t: 0 for t in teams}
    team_last_played = {t: 0 for t in teams}  

    for team in teams:
        team_conf = conferences[team]

        # Conference opponents
        conf_opponents = [t for t in teams if conferences[t] == team_conf and t != team]
        conf_games = random.sample(conf_opponents, 20)  

        # Non-conference opponents
        non_conf_opponents = [t for t in teams if conferences[t] != team_conf]
        non_conf_games = random.sample(non_conf_opponents, random.randint(8, 12))

        all_opponents = conf_games + non_conf_games

        for i, opp in enumerate(all_opponents):
            # Assign home/away
            if team_home_games[team] < 15:
                home_team, away_team = team, opp
                team_home_games[team] += 1
            else:
                if random.random() > 0.5:
                    home_team, away_team = team, opp
                    team_home_games[team] += 1
                else:
                    home_team, away_team = opp, team
                    team_home_games[opp] += 1

            # Assign day
            if i < len(non_conf_games):
                possible_days = list(range(1, 31))
            else:
                possible_days = list(range(31, 161))

            assigned_day = None
            random.shuffle(possible_days)
            for day in possible_days:
                if (
                    day_games_count[day] < 50
                    and team_games_count[team] < 40
                    and team_games_count[opp] < 40
                    and team_last_played[team] != day
                    and team_last_played[opp] != day
                ):
                    assigned_day = day
                    break

            if assigned_day:
                schedule.append({
                    "Day": assigned_day,
                    "Home": home_team,
                    "Away": away_team
                })
                day_games_count[assigned_day] += 1
                team_games_count[team] += 1
                team_games_count[opp] += 1
                team_last_played[team] = assigned_day
                team_last_played[opp] = assigned_day

    return pd.DataFrame(schedule)

schedule_df = generate_schedule(all_stats)

# -----------------------------
# Predict Outcomes
# -----------------------------
def predict_game(home, away):
    # Placeholder — should match features from training
    features = pd.DataFrame([{
        "Team_FG%": all_stats.loc[all_stats["Team"] == home, "FG_PERC"].values[0],
        "Team_PPG": all_stats.loc[all_stats["Team"] == home, "Points"].values[0],
        "Opp_FG%": all_stats.loc[all_stats["Team"] == away, "FG_PERC"].values[0],
        "Opp_PPG": all_stats.loc[all_stats["Team"] == away, "Points"].values[0]
    }])

    prob = predictor_model.predict_proba(features)[0]
    prediction = predictor_model.predict(features)[0]

    return prediction, prob

# -----------------------------
# Streamlit Interface
# -----------------------------
st.title("Schedule Predictor")

option = st.selectbox("View by:", ["Day", "Team", "Conference"])

if option == "Day":
    day_choice = st.slider("Select a Day", 1, 160, 1)
    day_games = schedule_df[schedule_df["Day"] == day_choice]
    st.write(day_games)

elif option == "Team":
    team_choice = st.selectbox("Select a Team", sorted(all_stats["Team"].unique()))
    team_games = schedule_df[(schedule_df["Home"] == team_choice) | (schedule_df["Away"] == team_choice)]
    st.write(team_games)

elif option == "Conference":
    conf_choice = st.selectbox("Select a Conference", sorted(all_stats["Conference"].unique()))
    conf_teams = all_stats[all_stats["Conference"] == conf_choice]["Team"].unique()
    conf_games = schedule_df[(schedule_df["Home"].isin(conf_teams)) | (schedule_df["Away"].isin(conf_teams))]
    st.write(conf_games)
