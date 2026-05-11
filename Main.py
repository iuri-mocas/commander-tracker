import streamlit as st
from config import apply_theme
from datetime import datetime, timedelta

st.set_page_config(page_title="Commander Tracker", layout="wide")

apply_theme()

# ---------- KEEP SUPABASE ACTIVE ----------
if "last_ping" not in st.session_state:
    st.session_state["last_ping"] = datetime.now()

if datetime.now() - st.session_state["last_ping"] > timedelta(days=6):
    try:
        from config import supabase
        supabase.table("players").select("id").limit(1).execute()
        st.session_state["last_ping"] = datetime.now()
    except Exception:
        pass


def normalize_user(name: str):
    known_names = {
        "iuri": "Iuri",
        "goncalo": "Gonçalo",
        "gonçalo": "Gonçalo",
        "ze": "Zé",
        "zé": "Zé",
    }

    clean = name.strip().lower()
    return known_names.get(clean, name.strip().title())


st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


if "user" not in st.session_state:
    st.markdown("""
    <div class="home-title">🎮 Commander Tracker</div>
    <div class="home-subtitle">Enter the battlefield.</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            name = st.text_input(
                "Planeswalker name",
                placeholder="Planeswalker name",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "Enter",
                use_container_width=True
            )

            if submitted and name.strip():
                st.session_state["user"] = normalize_user(name)
                st.rerun()

    st.stop()


user = st.session_state["user"]

st.markdown(f"""
<div class="home-title">Welcome, {user} ⚔️</div>
<div class="home-subtitle">Choose your destination, Planeswalker.</div>
""", unsafe_allow_html=True)

cards = [
    ("🏠\nDashboard", "pages/Dashboard.py"),
    ("🎴\nDecks", "pages/Decks.py"),
    ("🎮\nRecord Game", "pages/Record_Game.py"),
    ("📊\nStats", "pages/Stats.py"),
    ("🏆\nELO", "pages/Elo.py"),
]

try:
    from config import is_admin
    if is_admin():
        cards.append(("👑\nAdmin", "pages/Admin.py"))
except Exception:
    pass

cols = st.columns(3, gap="large")

for i, (label, path) in enumerate(cards):
    with cols[i % 3]:
        if st.button(label, key=path, use_container_width=True):
            st.switch_page(path)