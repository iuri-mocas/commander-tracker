import streamlit as st
from config import supabase, init_page
from datetime import datetime

init_page()

# ---------- MY RECORDED / PLAYED GAMES ----------
st.markdown("---")
st.subheader("📜 My Games")

current_user = st.session_state["user"]

players = supabase.table("players").select("*").execute().data
games = supabase.table("games").select("*").order("id", desc=True).execute().data
game_players = supabase.table("game_players").select("*").execute().data
decks = supabase.table("Deck").select("*").execute().data

player_map = {p["name"]: p["id"] for p in players}
deck_map = {d["id"]: d["name"] for d in decks}

current_user_id = player_map.get(current_user)

if not current_user_id:
    st.info("You are not linked to a player yet.")
else:
    my_rows = [
        gp for gp in game_players
        if gp.get("player") == current_user_id
    ]

    my_game_ids = [r["game_id"] for r in my_rows]

    my_games = [
        g for g in games
        if g["id"] in my_game_ids
    ]

    if not my_games:
        st.info("You have no games yet.")
    else:
        for game in my_games:
            game_id = game["id"]

            participants = [
                gp for gp in game_players
                if gp["game_id"] == game_id
            ]

            names = []
            for p in participants:
                deck_name = deck_map.get(p.get("deck"), "No deck")
                loan = " 🔁 loan" if p.get("loan_deck") else ""
                names.append(f"{p.get('player_name')} — {deck_name}{loan}")

            winner = game.get("winner_name", "Unknown")
            starter = game.get("starting_player_name", "Unknown")

            with st.expander(f"Game #{game_id} — {game.get('date')}"):
                st.write(f"🏆 Winner: **{winner}**")
                st.write(f"🚀 Starting player: **{starter}**")
                st.write("Players:")
                for n in names:
                    st.write(f"- {n}")