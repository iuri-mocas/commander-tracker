import streamlit as st
from config import supabase, init_page, is_admin
import pandas as pd

st.set_page_config(
    page_title="Commander Tracker",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_page()

if not is_admin():
    st.error("Admin only.")
    st.stop()

st.title("👑 Admin Panel")

tab_players, tab_games, tab_database, tab_danger = st.tabs([
    "Players",
    "Games",
    "Database",
    "Danger Zone"
])

# ---------- PLAYERS ----------
with tab_players:
    st.subheader("Manage Players")

    players = supabase.table("players").select("*").order("id").execute().data
    df_players = pd.DataFrame(players)

    if df_players.empty:
        st.info("No players yet.")
    else:
        st.dataframe(df_players, use_container_width=True)

    st.markdown("---")

    new_player = st.text_input("Add new player")

    if st.button("Add Player"):
        if new_player.strip():
            inserted = supabase.table("players").insert({
                "name": new_player.strip(),
                "elo": 1200
            }).execute()

            new_id = inserted.data[0]["id"]

            # Link old guest game records to this player
            supabase.table("game_players").update({
                "player": new_id
            }).eq("player_name", new_player.strip()).is_("player", "null").execute()

            supabase.table("games").update({
                "winner": new_id
            }).eq("winner_name", new_player.strip()).is_("winner", "null").execute()

            supabase.table("games").update({
                "starting_player": new_id
            }).eq("starting_player_name", new_player.strip()).is_("starting_player", "null").execute()

            st.success("Player added and old games linked.")
            st.rerun()

    if not df_players.empty:
        st.markdown("---")

        selected_player = st.selectbox(
            "Select player",
            df_players["name"].tolist()
        )

        selected_row = df_players[df_players["name"] == selected_player].iloc[0]
        selected_id = int(selected_row["id"])

        new_name = st.text_input("New name", selected_row["name"])
        new_elo = st.number_input(
            "New ELO",
            min_value=0,
            max_value=5000,
            value=int(selected_row["elo"])
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Update Player"):
                supabase.table("players").update({
                    "name": new_name.strip(),
                    "elo": int(new_elo)
                }).eq("id", selected_id).execute()

                st.success("Player updated.")
                st.rerun()

        with col2:
            confirm_delete_player = st.checkbox("Confirm delete player")

            if st.button("Delete Player"):
                if not confirm_delete_player:
                    st.warning("Check confirmation first.")
                else:
                    supabase.table("players").delete().eq("id", selected_id).execute()
                    st.warning("Player deleted.")
                    st.rerun()


# ---------- GAMES ----------
with tab_games:
    st.subheader("Manage Games")

    games = supabase.table("games").select("*").order("id", desc=True).execute().data
    df_games = pd.DataFrame(games)

    if df_games.empty:
        st.info("No games recorded yet.")
    else:
        st.dataframe(df_games, use_container_width=True)

        game_ids = [int(x) for x in df_games["id"].tolist()]

        selected_game = st.selectbox(
            "Select game to delete",
            game_ids,
            format_func=lambda x: f"Game #{x}"
        )

        confirm_delete_game = st.checkbox(f"Confirm delete Game #{selected_game}")

        if st.button("Delete Selected Game"):
            if not confirm_delete_game:
                st.warning("Check the confirmation box first.")
            else:
                supabase.table("game_players").delete().eq("game_id", selected_game).execute()
                supabase.table("games").delete().eq("id", selected_game).execute()

                st.success(f"Game #{selected_game} deleted.")
                st.rerun()


# ---------- DATABASE ----------
with tab_database:
    st.subheader("View Database")

    table = st.selectbox(
        "Table",
        ["players", "games", "game_players", "Deck", "cards", "deck_cards"]
    )

    try:
        data = supabase.table(table).select("*").execute().data
        df = pd.DataFrame(data)

        if df.empty:
            st.info(f"{table} is empty.")
        else:
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Could not load table: {e}")


# ---------- DANGER ZONE ----------
with tab_danger:
    st.subheader("⚠️ Danger Zone")

    st.warning("These actions cannot be undone.")

    confirm_reset_elo = st.checkbox("Confirm reset all ELO")

    if st.button("Reset All ELO"):
        if not confirm_reset_elo:
            st.warning("Check confirmation first.")
        else:
            supabase.table("players").update({
                "elo": 1200
            }).gt("id", 0).execute()

            st.warning("All ELO reset.")
            st.rerun()

    st.markdown("---")

    confirm_delete_games = st.checkbox("Confirm delete ALL games")

    if st.button("Delete ALL Games"):
        if not confirm_delete_games:
            st.warning("Check confirmation first.")
        else:
            supabase.table("game_players").delete().gt("id", 0).execute()
            supabase.table("games").delete().gt("id", 0).execute()

            st.error("All games deleted.")
            st.rerun()