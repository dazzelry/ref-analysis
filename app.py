import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Referee Analytics", layout="wide")

@st.cache_data
def load_data():
    profiles = pd.read_csv("data/referee_profiles.csv")
    matrix = pd.read_csv("data/team_referee_matrix.csv", index_col=0)
    game_log = pd.read_csv("data/referee_game_log.csv", parse_dates=["date"])
    return profiles, matrix, game_log

profiles, matrix, game_log = load_data()

st.sidebar.title("Referee Analytics")
page = st.sidebar.radio("View", ["Leaderboard", "Team \u00d7 Referee Heatmap", "Career Trend"])

# ---------------- Leaderboard ----------------
if page == "Leaderboard":
    st.title("Referee Leaderboard")

    sort_col = st.selectbox(
        "Sort by:",
        ["strictness_pct", "consistency_pct", "avg_fouls", "avg_yellows", "games"]
    )
    ascending = st.checkbox("Ascending order", value=False)

    display_df = profiles.sort_values(sort_col, ascending=ascending)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    fig = px.bar(
        display_df.head(15), x="referee", y=sort_col,
        title=f"Top 15 Referees by {sort_col}"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Heatmap ----------------
elif page == "Team \u00d7 Referee Heatmap":
    st.title("Team \u00d7 Referee Card Heatmap")
    st.caption("Average yellow cards per team, per referee")

    fig = px.imshow(
        matrix,
        labels=dict(x="Referee", y="Team", color="Avg Yellows"),
        aspect="auto",
        color_continuous_scale="Reds"
    )
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Career Trend ----------------
elif page == "Career Trend":
    st.title("Referee Career Trends")

    referees = sorted(game_log["referee"].dropna().unique())
    ref_name = st.selectbox("Select a referee:", referees)

    ref_df = game_log[game_log["referee"] == ref_name].sort_values("date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ref_df["date"], y=ref_df["rolling_yellows"],
                              mode="lines+markers", name="Rolling Yellows (10-game)"))
    fig.add_trace(go.Scatter(x=ref_df["date"], y=ref_df["rolling_fouls"],
                              mode="lines+markers", name="Rolling Fouls (10-game)"))
    fig.update_layout(
        title=f"Career Trend: {ref_name} ({len(ref_df)} games)",
        xaxis_title="Date", yaxis_title="Rolling Average",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)