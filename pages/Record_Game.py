import streamlit as st
from config import supabase, init_page
from datetime import datetime

init_page()

st.title("🎮 Record Game")

players_data = supabase.table("players").select("*").execute().data
decks_data = supabase.table("Deck").select("*").execute().data

name_to_id = {p["name"]: p["id"] for p in players_data}
player_names = list(name_to_id.keys())

deck_name_to_id = {d["name"]: d["id"] for d in decks_data}

game_date = st.date_input("Game date")

st.subheader("Players")

selected_players = st.multiselect(
    "Select existing players",
    options=player_names
)

new_players_text = st.text_input("Add players that do not have login/player account yet (comma separated)")

if new_players_text:
    new_players = [p.strip() for p in new_players_text.split(",") if p.strip()]
    selected_players.extend(new_players)

selected_players = list(dict.fromkeys(selected_players))

player_decks = {}
loan_decks = {}

if selected_players:
    st.subheader("Assign Decks")

    for player_name in selected_players:
        player_id = name_to_id.get(player_name)
        player_exists = player_id is not None

        if not player_exists:
            loan_decks[player_name] = True
            st.warning(f"{player_name} is not a created player, so they must use a borrowed deck.")
        else:
            loan_decks[player_name] = st.checkbox(
                f"{player_name} is using a borrowed deck",
                key=f"loan_{player_name}"
            )

        if player_exists and not loan_decks[player_name]:
            allowed_decks = [
                d for d in decks_data
                if d.get("owner") == player_id
            ]
        else:
            allowed_decks = decks_data

        if allowed_decks:
            deck_options = [d["name"] for d in allowed_decks]

            chosen_deck = st.selectbox(
                f"{player_name}'s deck",
                deck_options,
                key=f"deck_{player_name}"
            )

            player_decks[player_name] = deck_name_to_id.get(chosen_deck)
        else:
            st.warning(f"No decks available for {player_name}.")
            player_decks[player_name] = None

    winner_name = st.selectbox("Winner", selected_players)
    starter_name = st.selectbox("Starting Player", selected_players)

    if st.button("Save Game"):
        winner_id = name_to_id.get(winner_name)
        starter_id = name_to_id.get(starter_name)

        game = supabase.table("games").insert({
            "date": str(game_date),
            "winner": winner_id,
            "winner_name": winner_name,
            "starting_player": starter_id,
            "starting_player_name": starter_name
        }).execute()

        game_id = game.data[0]["id"]

        for player_name in selected_players:
            supabase.table("game_players").insert({
                "game_id": game_id,
                "player": name_to_id.get(player_name),
                "player_name": player_name,
                "deck": player_decks.get(player_name),
                "loan_deck": loan_decks.get(player_name, False)
            }).execute()

        st.success("Game saved!")