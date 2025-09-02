import pandas as pd
import numpy as np
import random

# Load teams & conference info
df = pd.read_csv("Data/All_stats.csv", encoding="latin1")
teams = df[["Teams", "Conference"]].drop_duplicates().reset_index(drop=True)

# Parameters
num_days = 160
max_games_per_day = 50

# Create schedule container
schedule = []
day_game_counts = {d: 0 for d in range(1, num_days+1)}
team_games = {team: [] for team in teams["Teams"]}

# Helper function to assign day
def assign_day(team1, team2):
    for _ in range(1000):  # safety loop
        day = random.randint(1, num_days)
        if (
            day_game_counts[day] < max_games_per_day and
            day not in team_games[team1] and
            day not in team_games[team2]
        ):
            day_game_counts[day] += 1
            team_games[team1].append(day)
            team_games[team2].append(day)
            return day
    return None  # failsafe

# Generate schedule
for _, row in teams.iterrows():
    team = row["Teams"]
    conf = row["Conference"]

    # Opponents
    conf_opponents = teams[teams["Conference"] == conf]["Teams"].tolist()
    conf_opponents = [t for t in conf_opponents if t != team]

    non_conf_opponents = teams[teams["Conference"] != conf]["Teams"].tolist()

    # Pick opponents
    chosen_conf = random.sample(conf_opponents, min(20, len(conf_opponents)))
    num_non_conf = random.randint(8, 12)
    chosen_non_conf = random.sample(non_conf_opponents, min(num_non_conf, len(non_conf_opponents)))

    opponents = chosen_conf + chosen_non_conf
    home_games = 0

    for opp in opponents:
        # Random home/away but enforce 15+ home games
        if home_games < 15:
            home = True
        else:
            home = random.choice([True, False])

        home_team = team if home else opp
        away_team = opp if home else team

        # Assign day
        day = assign_day(home_team, away_team)
        if day:
            schedule.append({
                "Day": day,
                "Home": home_team,
                "Away": away_team,
                "Conference_Game": int(row["Conference"] == teams.loc[teams["Teams"] == opp, "Conference"].values[0])
            })
            if home:
                home_games += 1

# Save CSV
schedule_df = pd.DataFrame(schedule)
schedule_df.sort_values(by=["Day"], inplace=True)
schedule_df.to_csv("Data/Randomized_Schedule.csv", index=False)

print("✅ Randomized schedule saved to Data/Randomized_Schedule.csv")

import streamlit as st
import pandas as pd
import io

# After generating schedule_df
schedule_df = pd.DataFrame(schedule)
schedule_df.sort_values(by=["Day"], inplace=True)

# Save to CSV buffer
csv_buffer = io.StringIO()
schedule_df.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode("utf-8")

# Add download button in Streamlit
st.download_button(
    label="📥 Download Randomized Schedule CSV",
    data=csv_bytes,
    file_name="Randomized_Schedule.csv",
    mime="text/csv"
)
