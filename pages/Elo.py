import streamlit as st
from config import supabase, init_page
import pandas as pd

init_page()

st.title("🏆 ELO Rankings")

players = supabase.table("players").select("*").execute().data
df = pd.DataFrame(players)

if df.empty:
    st.info("No players yet.")
    st.stop()

def rank_name(elo):
    if elo < 1000:
        return "Mana Screwed 😭"
    elif elo < 1200:
        return "Casual Chaos"
    elif elo < 1400:
        return "Table Menace 😈"
    elif elo < 1600:
        return "Archenemy 🔥"
    else:
        return "cEDH Overlord 💀"

df["rank"] = df["elo"].apply(rank_name)
df = df.sort_values("elo", ascending=False)

st.dataframe(df[["name", "elo", "rank"]], use_container_width=True)