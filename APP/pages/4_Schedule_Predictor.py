# APP/pages/4_Schedule_Predictor.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    all_stats = pd.read_csv("Data/All_stats.csv", encoding="latin1")
    game_history = pd.read_csv("Data/Daily_predictor_excel.csv", encoding="latin1")
    schedule = pd.read_csv("Data/Randomized_Schedule.csv", encoding="latin1")
    return all_stats, game_history, schedule

all_stats, game_history, schedule = load_data()

# ----------------------------
# Preprocess Data
# ----------------------------
# Choose features for training (basic efficiency + shooting + rebounding + assists + turnovers)
features = [
    "FG_PERC", "FG3_PERC", "FT_PERC",
    "OReb", "DReb", "Rebounds",
    "AST", "TO", "STL",
    "Off_eff", "Def_efficiency hybrid"
]

# Clean historical games to match features
game_history = game_history.dropna(subset=["Points", "Opp Points"])
game_history["Result"] = (game_history["Points"] > game_history["Opp Points"]).astype(int)

# Merge stats for Team and Opponent
def attach_team_stats(df, team_col, prefix):
    return df.merge(all_stats[["Teams"] + features], left_on=team_col, right_on="Teams", how="left") \
             .drop(columns=["Teams"]) \
             .rename(columns={col: f"{prefix}_{col}" for col in features})

game_history = attach_team_stats(game_history, "Team", "Team")
game_history = attach_team_stats(game_history, "Opponent", "Opp")

# Final feature set
X = game_history[[f"Team_{f}" for f in features] + [f"Opp_{f}" for f in features]].fillna(0)
y = game_history["Result"]

# ----------------------------
# Train Model
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)
acc = accuracy_score(y_test, model.predict(X_test))

# ----------------------------
# Predict Future Schedule
# ----------------------------
def predict_schedule(schedule_df):
    schedule_df = attach_team_stats(schedule_df, "Home", "Home")
    schedule_df = attach_team_stats(schedule_df, "Away", "Away")

    X_future = schedule_df[[f"Home_{f}" for f in features] + [f"Away_{f}" for f in features]].fillna(0)
    preds = model.predict_proba(X_future)[:, 1]  # probability Home wins
    schedule_df["Home_Win_Prob"] = preds
    schedule_df["Predicted_Winner"] = np.where(preds >= 0.5, schedule_df["Home"], schedule_df["Away"])
    return schedule_df

predicted_schedule = predict_schedule(schedule)

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("🏀 Schedule Predictor")
st.write(f"Model accuracy on test set: **{acc:.2%}**")

# Selection type
option = st.radio("Select by:", ["Day", "Team", "Conference"])

if option == "Day":
    days = sorted(predicted_schedule["Day"].unique())
    selected_day = st.selectbox("Select Day", days)
    st.dataframe(predicted_schedule[predicted_schedule["Day"] == selected_day][
        ["Day", "Home", "Away", "Conference_Game", "Home_Win_Prob", "Predicted_Winner"]
    ])

elif option == "Team":
    teams = sorted(all_stats["Teams"].dropna().unique())
    selected_team = st.selectbox("Select Team", teams)
    team_games = predicted_schedule[(predicted_schedule["Home"] == selected_team) | 
                                    (predicted_schedule["Away"] == selected_team)]
    st.dataframe(team_games[["Day", "Home", "Away", "Conference_Game", "Home_Win_Prob", "Predicted_Winner"]])

elif option == "Conference":
    conferences = sorted(all_stats["Conference"].dropna().unique())
    selected_conf = st.selectbox("Select Conference", conferences)
    teams_in_conf = all_stats[all_stats["Conference"] == selected_conf]["Teams"].unique()
    conf_games = predicted_schedule[(predicted_schedule["Home"].isin(teams_in_conf)) | 
                                    (predicted_schedule["Away"].isin(teams_in_conf))]
    st.dataframe(conf_games[["Day", "Home", "Away", "Conference_Game", "Home_Win_Prob", "Predicted_Winner"]])
