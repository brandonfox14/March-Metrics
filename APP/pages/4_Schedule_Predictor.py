# generate_random_schedule.py
import pandas as pd
import numpy as np
import random
import os

# ---------- CONFIG ----------
ALL_STATS_PATH = "Data/All_stats.csv"   # adjust if needed
OUT_CSV = "random_schedule.csv"
NUM_DAYS = 160
NONCONF_DAYS = range(1, 21)   # non-conference games: days 1..20
CONF_DAYS = range(21, NUM_DAYS + 1)
MAX_GAMES_PER_DAY = 50
MAX_GAMES_PER_TEAM = 40
MIN_HOME_GAMES = 15
CONF_GAMES_PER_TEAM = 20
NONCONF_MIN = 8
NONCONF_MAX = 12
SEED = 42
# ----------------------------

random.seed(SEED)
np.random.seed(SEED)

# Load
if not os.path.exists(ALL_STATS_PATH):
    raise FileNotFoundError(f"{ALL_STATS_PATH} not found. Put All_stats.csv at this path or change ALL_STATS_PATH.")

df = pd.read_csv(ALL_STATS_PATH, encoding="latin1")

# Normalize column names
if "Teams" not in df.columns and "Team" in df.columns:
    df.rename(columns={"Team": "Teams"}, inplace=True)
if "Conference" not in df.columns:
    df["Conference"] = "UnknownConference"

teams = df["Teams"].dropna().unique().tolist()
conf_map = df.set_index("Teams")["Conference"].to_dict()
conferences = sorted(df["Conference"].dropna().unique().tolist())

# Desired per-team counts
desired_conf = {t: CONF_GAMES_PER_TEAM for t in teams}
desired_nonconf = {t: random.randint(NONCONF_MIN, NONCONF_MAX) for t in teams}
# Cap totals at MAX_GAMES_PER_TEAM
for t in teams:
    if desired_conf[t] + desired_nonconf[t] > MAX_GAMES_PER_TEAM:
        desired_nonconf[t] = max(0, MAX_GAMES_PER_TEAM - desired_conf[t])

# Trackers
games = []  # each entry: dict(Home, Away, Conference_Game)
current_conf = {t: 0 for t in teams}
current_nonconf = {t: 0 for t in teams}
current_total = {t: 0 for t in teams}
home_count = {t: 0 for t in teams}

def schedule_match(a, b, is_conf):
    """Schedule one match between a and b (counts for both). Returns True if scheduled."""
    # ensure capacity
    if current_total[a] >= MAX_GAMES_PER_TEAM or current_total[b] >= MAX_GAMES_PER_TEAM:
        return False
    # choose home team to help meet MIN_HOME_GAMES
    if home_count[a] < MIN_HOME_GAMES and home_count[b] >= MIN_HOME_GAMES:
        home, away = a, b
    elif home_count[b] < MIN_HOME_GAMES and home_count[a] >= MIN_HOME_GAMES:
        home, away = b, a
    else:
        # prefer giving home to the team with fewer home games
        if home_count[a] < home_count[b]:
            home, away = a, b
        elif home_count[b] < home_count[a]:
            home, away = b, a
        else:
            home = random.choice([a,b]); away = b if home==a else a
    games.append({"Home": home, "Away": away, "Conference_Game": bool(is_conf)})
    current_total[a] += 1
    current_total[b] += 1
    if is_conf:
        current_conf[a] += 1; current_conf[b] += 1
    else:
        current_nonconf[a] += 1; current_nonconf[b] += 1
    home_count[home] += 1
    return True

# 1) Conference games - pair inside each conference
for conf in conferences:
    group = [t for t in teams if conf_map.get(t) == conf]
    if len(group) < 2:
        continue
    attempts = 0
    max_attempts = 20000
    while attempts < max_attempts:
        attempts += 1
        needers = [t for t in group if current_conf[t] < desired_conf[t] and current_total[t] < MAX_GAMES_PER_TEAM]
        if not needers:
            break
        a = random.choice(needers)
        candidates = [t for t in group if t != a and current_conf[t] < desired_conf[t] and current_total[t] < MAX_GAMES_PER_TEAM]
        if not candidates:
            candidates = [t for t in group if t != a and current_total[t] < MAX_GAMES_PER_TEAM]
            if not candidates:
                break
        b = random.choice(candidates)
        schedule_match(a, b, is_conf=True)

# 2) Non-conference games - pair across conferences
attempts = 0
max_attempts = 50000
while attempts < max_attempts:
    attempts += 1
    needers = [t for t in teams if current_nonconf[t] < desired_nonconf[t] and current_total[t] < MAX_GAMES_PER_TEAM]
    if not needers:
        break
    a = random.choice(needers)
    others = [t for t in teams if conf_map.get(t) != conf_map.get(a) and t != a and current_total[t] < MAX_GAMES_PER_TEAM]
    if not others:
        break
    candidates = [t for t in others if current_nonconf[t] < desired_nonconf[t]]
    if not candidates:
        candidates = others
    b = random.choice(candidates)
    schedule_match(a, b, is_conf=False)

# 3) Fill shortfalls (try to meet desired totals)
for t in teams:
    target = min(MAX_GAMES_PER_TEAM, desired_conf[t] + desired_nonconf[t])
    fill_attempts = 0
    while current_total[t] < target and fill_attempts < 500:
        fill_attempts += 1
        candidates = [o for o in teams if o != t and current_total[o] < MAX_GAMES_PER_TEAM]
        if not candidates:
            break
        o = random.choice(candidates)
        is_conf = (conf_map.get(t) == conf_map.get(o))
        schedule_match(t, o, is_conf)

# 4) Try to improve home counts by flipping away->home where possible
def build_index(games_list):
    idx = {t: [] for t in teams}
    for i,g in enumerate(games_list):
        idx[g["Home"]].append(("H", i))
        idx[g["Away"]].append(("A", i))
    return idx

team_game_index = build_index(games)
for t in teams:
    tries = 0
    while home_count[t] < MIN_HOME_GAMES and tries < 200:
        tries += 1
        # find an away game for t where opponent has > MIN_HOME_GAMES
        away_games_idx = [i for typ,i in team_game_index[t] if typ == "A"]
        random.shuffle(away_games_idx)
        flipped = False
        for gi in away_games_idx:
            g = games[gi]
            opp = g["Home"]
            if home_count[opp] > MIN_HOME_GAMES:
                # flip home/away
                games[gi]["Home"], games[gi]["Away"] = games[gi]["Away"], games[gi]["Home"]
                home_count[t] += 1
                home_count[opp] -= 1
                team_game_index = build_index(games)
                flipped = True
                break
        if not flipped:
            break

# 5) Assign days (non-conf to days 1..20, conf to 21..NUM_DAYS)
day_games = {d: [] for d in range(1, NUM_DAYS+1)}
team_days = {t: set() for t in teams}
random.shuffle(games)
nonconf_games = [g for g in games if not g["Conference_Game"]]
conf_games = [g for g in games if g["Conference_Game"]]

def assign_days(game_list, day_range):
    for g in game_list:
        assigned = False
        days = list(day_range)
        random.shuffle(days)
        for d in days:
            if len(day_games[d]) >= MAX_GAMES_PER_DAY:
                continue
            if d in team_days[g["Home"]] or d in team_days[g["Away"]]:
                continue
            day_games[d].append(g)
            team_days[g["Home"]].add(d)
            team_days[g["Away"]].add(d)
            g["Day"] = d
            assigned = True
            break
        if not assigned:
            # fallback to any day
            for d in range(1, NUM_DAYS+1):
                if len(day_games[d]) >= MAX_GAMES_PER_DAY:
                    continue
                if d in team_days[g["Home"]] or d in team_days[g["Away"]]:
                    continue
                day_games[d].append(g)
                team_days[g["Home"]].add(d)
                team_days[g["Away"]].add(d)
                g["Day"] = d
                assigned = True
                break
        if not assigned:
            g["Day"] = None

assign_days(nonconf_games, NONCONF_DAYS)
assign_days(conf_games, CONF_DAYS)

# Build final dataframe and clean
schedule_df = pd.DataFrame([{"Day": g.get("Day"), "Home": g["Home"], "Away": g["Away"], "Conference_Game": g["Conference_Game"]} for g in games])
# try to place any None days
unscheduled = schedule_df[schedule_df["Day"].isna()].index.tolist()
for idx in unscheduled:
    placed = False
    for d in range(1, NUM_DAYS+1):
        if len(day_games[d]) < MAX_GAMES_PER_DAY:
            h = schedule_df.at[idx, "Home"]; a = schedule_df.at[idx, "Away"]
            if d not in team_days[h] and d not in team_days[a]:
                schedule_df.at[idx, "Day"] = d
                day_games[d].append(schedule_df.loc[idx].to_dict())
                team_days[h].add(d); team_days[a].add(d)
                placed = True
                break
    if not placed:
        schedule_df.at[idx, "Day"] = -1

schedule_df = schedule_df[schedule_df["Day"].notna()].copy()
schedule_df["Day"] = schedule_df["Day"].astype(int)
schedule_df.drop_duplicates(subset=["Day","Home","Away"], inplace=True)
schedule_df.reset_index(drop=True, inplace=True)

# Save CSV
schedule_df.to_csv(OUT_CSV, index=False)

# Summary report
per_team_games = schedule_df.apply(lambda r: [r["Home"], r["Away"]], axis=1).explode().value_counts()
home_counts = schedule_df["Home"].value_counts()
summary = {
    "total_games": len(schedule_df),
    "teams_generated": len(teams),
    "min_games_per_team": int(per_team_games.min()) if not per_team_games.empty else 0,
    "max_games_per_team": int(per_team_games.max()) if not per_team_games.empty else 0,
    "teams_with_home_lt_MIN_HOME_GAMES": int((home_counts < MIN_HOME_GAMES).sum())
}

print("Saved randomized schedule to:", OUT_CSV)
print("Summary:", summary)
print(schedule_df.head(40).to_string(index=False))
