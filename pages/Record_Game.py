import streamlit as st
from config import supabase, init_page
from datetime import datetime

init_page()

st.title("🎮 Record Game")

# ---------- LOAD DATA ----------
players_data = supabase.table("players").select("*").execute().data
decks_data = supabase.table("Deck").select("*").execute().data

name_to_id = {p["name"]: p["id"] for p in players_data}
player_names = list(name_to_id.keys())

deck_name_to_id = {d["name"]: d["id"] for d in decks_data}

# ---------- RECORD GAME ----------
st.subheader("⚔️ New Game")

game_date = st.date_input("Game date")

selected_players = st.multiselect(
    "Select existing players",
    options=player_names
)

new_players_text = st.text_input(
    "Add players that do not have an account yet (comma separated)"
)

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
            st.warning(f"{player_name} is not created yet, so they must use a borrowed deck.")
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

    if st.button("💾 Save Game"):
        winner_id = name_to_id.get(winner_name)

        game = supabase.table("games").insert({
            "date": str(game_date),
            "winner": winner_id,
            "winner_name": winner_name
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
        st.rerun()
else:
    st.info("Select or add players to record a game.")

# ---------- MY GAMES ----------
st.markdown("---")
st.subheader("📜 My Games")

current_user = st.session_state["user"]

games = supabase.table("games").select("*").order("id", desc=True).execute().data
game_players = supabase.table("game_players").select("*").execute().data
decks = supabase.table("Deck").select("*").execute().data

deck_map = {d["id"]: d["name"] for d in decks}
current_user_id = name_to_id.get(current_user)

my_rows = [
    gp for gp in game_players
    if gp.get("player") == current_user_id or gp.get("player_name") == current_user
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

        with st.expander(f"Game #{game_id} — {game.get('date')}"):
            st.write(f"🏆 Winner: **{winner}**")
            st.write("Players:")
            for n in names:
                st.write(f"- {n}")