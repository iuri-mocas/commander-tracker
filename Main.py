import streamlit as st
from config import apply_theme

st.set_page_config(page_title="Commander Tracker", layout="wide")

apply_theme()

# ---------- NORMALIZE USER ----------
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


# ---------- ALWAYS HIDE SIDEBAR ON MAIN PAGE ----------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="collapsedControl"] {
    display: none;
}

.home-title {
    text-align: center;
    font-size: 4rem;
    font-weight: 900;
    color: #F6E8C7;
    font-family: Georgia, serif;
    text-shadow: 0 0 25px rgba(0,0,0,.9);
    margin-top: 4rem;
}

.home-subtitle {
    text-align: center;
    color: #D4AF37;
    font-size: 1.3rem;
    margin-bottom: 3rem;
}

div.stButton > button {
    height: 155px;
    border-radius: 24px !important;
    border: 1px solid rgba(212,175,55,.9) !important;
    background: linear-gradient(145deg, rgba(16,35,52,.95), rgba(8,12,22,.98)) !important;
    color: #F6E8C7 !important;
    font-size: 1.25rem !important;
    font-weight: 900 !important;
    font-family: Georgia, serif !important;
    box-shadow: 0 0 24px rgba(0,0,0,.8);
    transition: all .2s ease-in-out;
}

div.stButton > button:hover {
    transform: translateY(-6px) scale(1.03);
    background: linear-gradient(145deg, rgba(90,65,22,.98), rgba(12,18,32,.98)) !important;
    border: 2px solid gold !important;
}

.logout-small button {
    height: 46px !important;
    border-radius: 14px !important;
    background: linear-gradient(145deg, #0b1d2a, #1a3d45) !important;
    border: 1px solid rgba(212,175,55,.65) !important;
    font-size: .95rem !important;
}
</style>
""", unsafe_allow_html=True)


# ---------- LOGIN ----------
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
            submitted = st.form_submit_button("Enter", use_container_width=True)

            if submitted and name.strip():
                st.session_state["user"] = normalize_user(name)
                st.rerun()

    st.stop()


# ---------- HOME ----------
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

if user == "Iuri":
    cards.append(("👑\nAdmin", "pages/Admin.py"))

cols = st.columns(3, gap="large")

for i, (label, path) in enumerate(cards):
    with cols[i % 3]:
        if st.button(label, key=path, use_container_width=True):
            st.switch_page(path)

st.write("")

_, mid, _ = st.columns([2.3, 1, 2.3])
with mid:
    st.markdown('<div class="logout-small">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)