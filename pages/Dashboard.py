import streamlit as st
from config import supabase, init_page
import random

init_page()

st.title("🏠 Dashboard")

quotes = [
    "Turn 1 Sol Ring 👀",
    "Politics were involved.",
    "That was NOT fair 😭",
    "Skill issue or bad luck? You decide."
]

st.info(random.choice(quotes))

players = supabase.table("players").select("*").execute().data
games = supabase.table("games").select("*").execute().data

col1, col2 = st.columns(2)

with col1:
    st.metric("Players", len(players))

with col2:
    st.metric("Games", len(games))