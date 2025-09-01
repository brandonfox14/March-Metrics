import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_top7_section(team_data, conference_data):
    st.header("Top 7 Players Analysis")

    # --- Check if data exists ---
    if team_data["FGM_TOP7"].isna().any():
        st.write("*This team does not have a full top 7 rotation*")
        return

    # --- Stats & Ranks (side by side) ---
    stats_with_ranks = {
        "FGM": ("FGM_TOP7", "FGM_TOP7_RANK"),
        "FGA": ("FGA-Top7", "FGA-Top7_RANK"),
        "3PM": ("FG3sM-Top7", "FG3sM-Top7_RANK"),
        "3PA": ("FG3sA-Top7", "FG3sA-Top7_RANK"),
        "FTM": ("FTM-Top7", "FTM-Top7_RANK"),
        "FTA": ("FTA-Top7", "FTA-Top7_RANK"),
        "FG%": ("FG_PERC-Top7", "FG_PERC-Top7_RANK"),
        "3P%": ("FG3_PERC-Top7", "FG3_PERC-Top7_RANK"),
        "FT%": ("FT_PERC-Top7", "FT_PERC-Top7_RANK"),
        "OReb": ("OReb-Top7", "OReb-Top7_RANK"),
        "DReb": ("DReb-Top7", "DReb-Top7_RANK"),
        "Rebounds": ("Rebounds-Top7", "Rebounds-Top7_RANK"),
        "AST": ("AST-Top7", "AST-Top7_RANK"),
        "TO": ("TO-Top7", "TO-Top7_RANK"),
        "STL": ("STL-Top7", "STL-Top7_RANK"),
        "Points": ("Points per Game-Top7", "Points-Top7_RANK"),
        "Start %": ("Start Percentage top 7", "Start Percentage top 7_RANK")
    }

    summary_data = {}
    for stat, (val_col, rank_col) in stats_with_ranks.items():
        summary_data[stat] = [team_data[val_col], team_data[rank_col]]

    summary_df = pd.DataFrame(summary_data, index=["Value", "Rank"]).T
    st.subheader("Top 7 Player Stats Summary")
    st.dataframe(summary_df)

    # --- Percentage comparison (vs conference) ---
    perc_cols = [col for col in team_data.index if "-Perc" in col]
    team_perc = team_data[perc_cols].astype(float)
    conf_perc = conference_data[perc_cols].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(perc_cols))
    ax.bar(x, team_perc, width=0.4, label="Team")
    ax.bar([i+0.4 for i in x], conf_perc, width=0.4, label="Conference Avg")
    ax.set_xticks([i+0.2 for i in x])
    ax.set_xticklabels([col.replace("-Perc", "") for col in perc_cols], rotation=45)
    ax.set_ylabel("Proportion (decimal)")
    ax.set_title("Top 7 Contribution vs Conference")
    ax.legend()
    st.pyplot(fig)

    # --- Standard Points Visual ---
    points = float(team_data["Points per Game-Top7"])
    rank = int(team_data["Points-Top7_RANK"])

    fig, ax1 = plt.subplots(figsize=(6,4))
    ax1.bar(["Points per Game"], [points], color="blue", label="Points")
    ax2 = ax1.twinx()
    ax2.plot(["Points per Game"], [rank], color="red", marker="o", label="Rank")
    ax2.invert_yaxis()  # so rank 1 is top
    ax1.set_ylabel("Points")
    ax2.set_ylabel("Rank")
    plt.title("Top 7 Points and Rank")
    st.pyplot(fig)


