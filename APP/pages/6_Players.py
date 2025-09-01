import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data
def load_data():
    return pd.read_csv("Data/All_stats.csv", encoding="latin1")

df = load_data()


# --- Team vs Conference Comparison (Top 7 Percentages) ---

# Select the Top 7 percentage columns
perc_cols = [
    "FGM-Top7-Perc", "FGA-Top7-Perc", "FG3sM-Top7-Perc", "FG3sA-Top7-Perc",
    "FTM-Top7-Perc", "FTA-Top7-Perc", "FG_PERC_Top7_per", "FG3_PERC_Top7_per",
    "FT_PERC_Top7_per", "OReb-Top7-Perc", "DReb-Top7-Perc", "Rebounds-Top7-Perc",
    "AST-Top7-Perc", "TO-Top7-Perc", "STL-Top7-Perc", "Points-Top7-Perc"
]

# Build team vs conf dataframe
team_vals = df.loc[df["Teams"] == team_choice, perc_cols].iloc[0]
conf_vals = df.loc[df["Conference"] == conf, perc_cols].mean()

compare_df = pd.DataFrame({
    "Stat": perc_cols,
    "Team Value": team_vals.values,
    "Conference Average": conf_vals.values
})

# Ensure numeric
compare_df["Team Value"] = pd.to_numeric(compare_df["Team Value"], errors="coerce")
compare_df["Conference Average"] = pd.to_numeric(compare_df["Conference Average"], errors="coerce")

# Reshape to long form for Plotly
compare_long = compare_df.melt(
    id_vars="Stat",
    value_vars=["Team Value", "Conference Average"],
    var_name="Category",
    value_name="Value"
)

# --- Plot 1: Bar Chart (Team vs Conference) ---
fig1 = px.bar(
    compare_long,
    x="Stat",
    y="Value",
    color="Category",
    barmode="group",
    title=f"{team_choice} vs {conf} – Top 7 Percentages"
)
st.plotly_chart(fig1)

# --- Standard Points with Rankings Overlay ---

# Grab Standard Points and Rank columns
team_points = df.loc[df["Teams"] == team_choice, "Standard_Points"].values[0]
team_rank = df.loc[df["Teams"] == team_choice, "Standard_Points_RANK"].values[0]

# Build dataframe for visualization
points_df = df[["Teams", "Standard_Points", "Standard_Points_RANK"]].copy()
points_df = points_df.sort_values("Standard_Points_RANK")

# Plot bar chart with line overlay
fig2 = go.Figure()

# Bars for Standard Points
fig2.add_trace(go.Bar(
    x=points_df["Teams"],
    y=points_df["Standard_Points"],
    name="Standard Points"
))

# Line for Rank (inverted so 1 is at the top)
fig2.add_trace(go.Scatter(
    x=points_df["Teams"],
    y=points_df["Standard_Points_RANK"].max() - points_df["Standard_Points_RANK"] + 1,
    name="Rank",
    mode="lines+markers",
    yaxis="y2"
))

# Layout
fig2.update_layout(
    title="Standard Points with Rankings Overlay",
    yaxis=dict(title="Standard Points"),
    yaxis2=dict(
        title="Rank (1=Top)",
        overlaying="y",
        side="right",
        autorange="reversed"
    ),
    xaxis=dict(showticklabels=False)  # hide x labels since it's all Teams
)

st.plotly_chart(fig2)
