import streamlit as st
from config import supabase, init_page, is_admin
import pandas as pd
import requests
import re
import time

init_page()

st.title("🎴 Decks")

user = st.session_state["user"]
admin = is_admin()

# ---------- HELPERS ----------
def get_deck_id_from_url(url):
    match = re.search(r"/decks/(\d+)", url)
    return match.group(1) if match else None


def get_scryfall_card(card_name):
    r = requests.get(
        "https://api.scryfall.com/cards/named",
        params={"exact": card_name},
        timeout=10
    )

    if r.status_code != 200:
        return None

    data = r.json()

    image_url = None
    if "image_uris" in data:
        image_url = data["image_uris"].get("normal")
    elif "card_faces" in data:
        image_url = data["card_faces"][0]["image_uris"].get("normal")

    return {
        "scryfall_id": data.get("id"),
        "name": data.get("name"),
        "image_url": image_url,
        "mana_cost": data.get("mana_cost"),
        "type_line": data.get("type_line"),
        "colors": ",".join(data.get("colors", []))
    }


def get_or_create_card(card_name):
    existing = supabase.table("cards").select("*").eq("name", card_name).execute().data

    if existing:
        return existing[0]["id"]

    card = get_scryfall_card(card_name)

    time.sleep(0.08)

    if not card:
        return None

    inserted = supabase.table("cards").insert(card).execute().data

    return inserted[0]["id"]


def fetch_archidekt_card_names(deck_url):
    deck_id = get_deck_id_from_url(deck_url)

    if not deck_id:
        return []

    api_url = f"https://archidekt.com/api/decks/{deck_id}/"
    r = requests.get(api_url, timeout=20)

    if r.status_code != 200:
        return []

    data = r.json()
    cards = data.get("cards", [])

    parsed = []

    for item in cards:
        quantity = item.get("quantity", 1)
        categories = item.get("categories", ["Other"])

        card = item.get("card", {})
        oracle = card.get("oracleCard", {})

        name = (
            oracle.get("name")
            or card.get("name")
            or item.get("name")
        )

        if not name:
            continue

        if not categories:
            categories = ["Other"]

        for category in categories:
            parsed.append({
                "name": name,
                "quantity": quantity,
                "category": category
            })

    return parsed


def import_deck_cards(deck_id, archidekt_url):
    cards = fetch_archidekt_card_names(archidekt_url)

    if not cards:
        return 0

    try:
        supabase.table("deck_cards").delete().eq("deck_id", deck_id).execute()

        total_cards = len(cards)
        imported_count = 0
        deck_card_rows = []

        progress_bar = st.progress(0)
        progress_text = st.empty()

        for index, card in enumerate(cards, start=1):
            card_id = get_or_create_card(card["name"])

            if card_id:
                deck_card_rows.append({
                    "deck_id": deck_id,
                    "card_id": card_id,
                    "quantity": card["quantity"],
                    "category": card["category"]
                })

                imported_count += 1

            percent = int(index / total_cards * 100)
            progress_bar.progress(percent)
            progress_text.write(
                f"Importing cards... {percent}% ({index}/{total_cards})"
            )

        chunk_size = 25

        for i in range(0, len(deck_card_rows), chunk_size):
            chunk = deck_card_rows[i:i + chunk_size]
            supabase.table("deck_cards").insert(chunk).execute()

        progress_bar.progress(100)
        progress_text.success(f"Import complete: {imported_count}/{total_cards} cards imported.")

        return imported_count

    except Exception as e:
        st.error(f"Import failed: {e}")
        return 0

# ---------- LOAD DATA ----------
players = supabase.table("players").select("*").execute().data
decks = supabase.table("Deck").select("*").execute().data

df_players = pd.DataFrame(players)
df_decks = pd.DataFrame(decks)

if df_players.empty or user not in df_players["name"].values:
    supabase.table("players").insert({
        "name": user,
        "elo": 1200
    }).execute()
    st.rerun()

name_to_id = dict(zip(df_players["name"], df_players["id"]))
id_to_name = dict(zip(df_players["id"], df_players["name"]))

current_user_id = int(name_to_id[user])

tabs = st.tabs(["Add Deck", "Deck List", "Deck View", "Deck Stats"])

# ---------- ADD DECK ----------
with tabs[0]:
    st.subheader("Add Deck")

    deck_name = st.text_input("Deck name")
    archidekt_url = st.text_input("Archidekt URL")

    if admin:
        owner_name = st.selectbox("Owner", df_players["name"].tolist())
        owner_id = int(name_to_id[owner_name])
    else:
        owner_id = current_user_id
        st.info(f"Deck owner: {user}")

    if st.button("Add Deck"):
        if deck_name.strip():
            inserted = supabase.table("Deck").insert({
                "name": deck_name.strip(),
                "owner": owner_id,
                "archidekt_url": archidekt_url.strip()
            }).execute().data

            new_deck_id = inserted[0]["id"]

            if archidekt_url.strip():
                imported = import_deck_cards(new_deck_id, archidekt_url.strip())
                st.success(f"Deck added. Imported {imported} cards.")
            else:
                st.success("Deck added.")

            st.rerun()

# ---------- DECK LIST ----------
with tabs[1]:
    st.subheader("Deck List")

    decks = supabase.table("Deck").select("*").execute().data
    df_decks = pd.DataFrame(decks)

    if df_decks.empty:
        st.info("No decks yet.")
    else:
        df_decks["owner_name"] = df_decks["owner"].map(id_to_name)

        if admin:
            df_show = df_decks
        else:
            df_show = df_decks[df_decks["owner"] == current_user_id]

        st.dataframe(
            df_show[["id", "name", "owner_name", "archidekt_url"]],
            use_container_width=True
        )

        if not df_show.empty:
            selected_deck_id = st.selectbox(
                "Select deck",
                df_show["id"].tolist(),
                format_func=lambda x: df_show[df_show["id"] == x]["name"].values[0]
            )

            selected_deck = df_show[df_show["id"] == selected_deck_id].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Re-import Cards"):
                    imported = import_deck_cards(
                        int(selected_deck_id),
                        selected_deck["archidekt_url"]
                    )
                    st.success(f"Imported {imported} cards.")
                    st.rerun()

            with col2:
                confirm_delete = st.checkbox("Confirm delete deck")

                if st.button("Delete Deck"):
                    if not confirm_delete:
                        st.warning("Check confirmation first.")
                    else:
                        # Delete deck cards first
                        supabase.table("deck_cards").delete().eq("deck_id", int(selected_deck_id)).execute()

                        # Remove deck reference from games
                        supabase.table("game_players").update({
                            "deck": None
                        }).eq("deck", int(selected_deck_id)).execute()

                        # Delete deck
                        supabase.table("Deck").delete().eq("id", int(selected_deck_id)).execute()

                        st.warning("Deck deleted.")
                        st.rerun()

# ---------- DECK VIEW ----------
with tabs[2]:
    st.subheader("Deck View")

    decks = supabase.table("Deck").select("*").execute().data
    df_decks = pd.DataFrame(decks)

    if df_decks.empty:
        st.info("No decks yet.")
    else:
        if admin:
            allowed_decks = df_decks
        else:
            allowed_decks = df_decks[df_decks["owner"] == current_user_id]

        if allowed_decks.empty:
            st.info("You have no decks.")
        else:
            selected_deck_id = st.selectbox(
                "Choose deck",
                allowed_decks["id"].tolist(),
                format_func=lambda x: allowed_decks[allowed_decks["id"] == x]["name"].values[0]
            )

            deck_cards = supabase.table("deck_cards").select("*").eq("deck_id", int(selected_deck_id)).execute().data

            if not deck_cards:
                st.warning("This deck has no imported cards.")
            else:
                df_deck_cards = pd.DataFrame(deck_cards)

                cards = supabase.table("cards").select("*").execute().data
                df_cards = pd.DataFrame(cards)

                df = df_deck_cards.merge(
                    df_cards,
                    left_on="card_id",
                    right_on="id",
                    suffixes=("_deck", "_card")
                )

                total_cards = int(df["quantity"].sum())

                type_counts = {
                    "Creatures": int(
                        df[df["type_line"].str.contains("Creature", case=False, na=False)]["quantity"].sum()),
                    "Instants": int(
                        df[df["type_line"].str.contains("Instant", case=False, na=False)]["quantity"].sum()),
                    "Sorceries": int(
                        df[df["type_line"].str.contains("Sorcery", case=False, na=False)]["quantity"].sum()),
                    "Artifacts": int(
                        df[df["type_line"].str.contains("Artifact", case=False, na=False)]["quantity"].sum()),
                    "Enchantments": int(
                        df[df["type_line"].str.contains("Enchantment", case=False, na=False)]["quantity"].sum()),
                    "Lands": int(df[df["type_line"].str.contains("Land", case=False, na=False)]["quantity"].sum()),
                    "Planeswalkers": int(
                        df[df["type_line"].str.contains("Planeswalker", case=False, na=False)]["quantity"].sum()),
                }

                st.markdown(f"""
                <div style="
                    background: rgba(0,0,0,.55);
                    border: 1px solid rgba(212,175,55,.65);
                    border-radius: 18px;
                    padding: 1rem 1.25rem;
                    margin: 1rem 0 2rem 0;
                ">
                    <span style="font-size: 2rem; font-weight: 900; color: #F6E8C7;">
                        {total_cards} cards
                    </span>
                    <span style="font-size: 1rem; margin-left: 1.25rem; color: #D4AF37;">
                        {type_counts["Creatures"]} creatures ·
                        {type_counts["Instants"]} instants ·
                        {type_counts["Sorceries"]} sorceries ·
                        {type_counts["Artifacts"]} artifacts ·
                        {type_counts["Enchantments"]} enchantments ·
                        {type_counts["Lands"]} lands ·
                        {type_counts["Planeswalkers"]} planeswalkers
                    </span>
                </div>
                """, unsafe_allow_html=True)

                categories = sorted(df["category"].dropna().unique())

                for category in categories:
                    category_cards = df[df["category"] == category]

                    st.markdown(f"## {category}")
                    st.caption(f"Qty: {category_cards['quantity'].sum()}")

                    cols = st.columns(5)

                    for i, (_, card) in enumerate(category_cards.iterrows()):
                        with cols[i % 5]:
                            if card.get("image_url"):
                                st.image(card["image_url"], use_container_width=True)

                            st.markdown(f"**{card['quantity']}x {card['name']}**")
                            st.caption(card.get("type_line", ""))

# ---------- DECK STATS ----------
with tabs[3]:
    st.subheader("Deck Stats")

    decks = supabase.table("Deck").select("*").execute().data
    game_players = supabase.table("game_players").select("*").execute().data
    games = supabase.table("games").select("*").execute().data

    df_decks = pd.DataFrame(decks)
    df_gp = pd.DataFrame(game_players)
    df_games = pd.DataFrame(games)

    if df_decks.empty or df_gp.empty or df_games.empty:
        st.info("Not enough data yet.")
    else:
        deck_id_to_name = dict(zip(df_decks["id"], df_decks["name"]))

        df = df_gp.merge(
            df_games,
            left_on="game_id",
            right_on="id",
            suffixes=("_gp", "_game")
        )

        df["deck_name"] = df["deck"].map(deck_id_to_name)
        df["won"] = df["player"] == df["winner"]

        stats = df.groupby("deck_name").agg(
            games_played=("game_id", "count"),
            wins=("won", "sum")
        ).reset_index()

        stats["winrate %"] = (
            stats["wins"] / stats["games_played"] * 100
        ).round(2)

        stats = stats.sort_values("winrate %", ascending=False)

        st.dataframe(stats, use_container_width=True)
        st.bar_chart(stats.set_index("deck_name")["winrate %"])