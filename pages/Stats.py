import streamlit as st
from config import supabase, init_page
import pandas as pd

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
my_games = df_games[df_games["id"].isin(my_game_ids)]

if my_games.empty:
    st.info("You have not played any games yet.")
    st.stop()

wins = my_games[
    (my_games["winner"] == player_id) |
    (my_games["winner_name"] == user)
]

losses = len(my_games) - len(wins)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Games Played", len(my_games))

with col2:
    st.metric("Wins", len(wins))

with col3:
    winrate = round(len(wins) / len(my_games) * 100, 2)
    st.metric("Winrate", f"{winrate}%")

st.subheader("Win / Loss")

wl_df = pd.DataFrame({
    "Result": ["Wins", "Losses"],
    "Games": [len(wins), losses]
})

st.bar_chart(wl_df.set_index("Result"))

st.subheader("My Deck Stats")

if df_decks.empty:
    st.info("No decks yet.")
else:
    my_decks = df_decks[df_decks["owner"] == player_id]

    if my_decks.empty:
        st.info("You do not own any decks yet.")
    else:
        deck_id_to_name = dict(zip(my_decks["id"], my_decks["name"]))

        my_deck_games = df_gp[
            (df_gp["deck"].isin(my_decks["id"])) &
            (
                (df_gp["player"] == player_id) |
                (df_gp["player_name"] == user)
            )
        ]

        if my_deck_games.empty:
            st.info("Your decks have not been used in games yet.")
        else:
            merged = my_deck_games.merge(
                df_games,
                left_on="game_id",
                right_on="id",
                suffixes=("_gp", "_game")
            )

            merged["deck_name"] = merged["deck"].map(deck_id_to_name)

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
            st.bar_chart(stats.set_index("deck_name")["winrate %"])