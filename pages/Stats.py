import streamlit as st
from config import supabase, init_page
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Commander Tracker",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_page()

st.title("📊 My Stats")

user = st.session_state["user"]

players = supabase.table("players").select("*").execute().data
games = supabase.table("games").select("*").execute().data
game_players = supabase.table("game_players").select("*").execute().data
decks = supabase.table("Deck").select("*").execute().data

df_players = pd.DataFrame(players)
df_games = pd.DataFrame(games)
df_gp = pd.DataFrame(game_players)
df_decks = pd.DataFrame(decks)

if df_players.empty or user not in df_players["name"].values:
    st.info("You do not have player data yet.")
    st.stop()

player_id = int(df_players[df_players["name"] == user]["id"].values[0])

if df_games.empty or df_gp.empty:
    st.info("No games yet.")
    st.stop()

# Games where logged player participated
my_game_rows = df_gp[
    (df_gp["player"] == player_id) |
    (df_gp["player_name"] == user)
]

my_game_ids = my_game_rows["game_id"].tolist()

my_games = df_games[
    df_games["id"].isin(my_game_ids)
]

if my_games.empty:
    st.info("You have not played any games yet.")
    st.stop()

wins = my_games[
    (my_games["winner"] == player_id) |
    (my_games["winner_name"] == user)
]

games_played = len(my_games)
wins_count = len(wins)

winrate = round((wins_count / games_played) * 100, 2)

# ---------- TOP METRICS ----------
col1, col2 = st.columns(2)

with col1:
    st.metric("Games Played", games_played)

with col2:
    st.metric("Winrate", f"{winrate}%")

# ---------- STATIC GENERAL CHART ----------
st.subheader("🏆 Overall Winrate")

fig1, ax1 = plt.subplots(figsize=(3, 2))

ax1.bar(["Winrate"], [winrate])

ax1.set_ylim(0, 100)
ax1.set_ylabel("Winrate %")
ax1.set_title("Overall Performance")

plt.tight_layout()

st.pyplot(fig1, clear_figure=True)

st.write(f"🏆 {wins_count} wins in {games_played} games")

# ---------- DECK STATS ----------
st.subheader("🎴 My Deck Stats")

if df_decks.empty or df_gp.empty:
    st.info("No deck stats available.")
    st.stop()

# normalize IDs safely
df_decks["id_str"] = df_decks["id"].astype(str)
df_gp["deck_str"] = df_gp["deck"].apply(lambda x: str(int(x)) if pd.notna(x) else None)

deck_id_to_name = dict(zip(df_decks["id_str"], df_decks["name"]))

# only rows where current user played AND has a deck
my_deck_games = df_gp[
    (
        (df_gp["player"] == player_id) |
        (df_gp["player_name"] == user)
    ) &
    (df_gp["deck"].notna())
].copy()

if my_deck_games.empty:
    st.info("You have not used any decks yet.")
    st.stop()

my_deck_games["deck_name"] = my_deck_games["deck_str"].map(deck_id_to_name)

# remove rows where deck id did not map
my_deck_games = my_deck_games[my_deck_games["deck_name"].notna()]

if my_deck_games.empty:
    st.info("Your games have deck IDs, but they do not match the Deck table.")
    st.stop()

merged = my_deck_games.merge(
    df_games,
    left_on="game_id",
    right_on="id",
    suffixes=("_gp", "_game")
)

merged["won"] = (
    (merged["winner"] == player_id) |
    (merged["winner_name"] == user)
)

stats = merged.groupby("deck_name").agg(
    games_played=("game_id", "count"),
    wins=("won", "sum")
).reset_index()

stats["losses"] = stats["games_played"] - stats["wins"]
stats["winrate %"] = (
    stats["wins"] / stats["games_played"] * 100
).round(2)

stats = stats.sort_values("winrate %", ascending=False)

st.dataframe(stats, use_container_width=True)

st.subheader("📈 Deck Winrate")

deck_options = stats["deck_name"].dropna().unique().tolist()

if not deck_options:
    st.info("No deck stats available.")
    st.stop()

selected_deck = st.selectbox(
    "Choose deck",
    deck_options,
    key="stats_deck_select"
)

selected_stats = stats[stats["deck_name"] == selected_deck].iloc[0]

deck_winrate = float(selected_stats["winrate %"])
deck_wins = int(selected_stats["wins"])
deck_losses = int(selected_stats["losses"])
deck_games = int(selected_stats["games_played"])

st.write(
    f"🎴 **{selected_deck}** · "
    f"{deck_wins} wins · "
    f"{deck_losses} losses · "
    f"{deck_games} games"
)

fig2, ax2 = plt.subplots(figsize=(3, 2))
ax2.bar([selected_deck], [deck_winrate])
ax2.set_ylim(0, 100)
ax2.set_ylabel("Winrate %")
ax2.set_title(f"{selected_deck} Winrate")

plt.tight_layout()
st.pyplot(fig2, clear_figure=True)