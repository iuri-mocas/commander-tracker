import streamlit as st
from supabase import create_client
import base64
import os

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_admin():
    local_admin = st.secrets.get("LOCAL_ADMIN", False)
    admin_name = st.secrets.get("ADMIN_NAME", "")

    return local_admin and st.session_state.get("user") == admin_name

def link_existing_guest_games(player_name, player_id):
    supabase.table("game_players").update({
        "player_id": player_id
    }).eq("player_name", player_name).is_("player_id", "null").execute()

    supabase.table("games").update({
        "winner_id": player_id
    }).eq("winner_name", player_name).is_("winner_id", "null").execute()

    supabase.table("games").update({
        "starting_player_id": player_id
    }).eq("starting_player_name", player_name).is_("starting_player_id", "null").execute()

def check_login():
    if "user" not in st.session_state:
        st.switch_page("Main.py")

def is_admin():
    return st.session_state["user"] in ADMIN_USERS

def img_to_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def apply_theme():
    bg = img_to_base64("assets/mtg_bg.jpg")

    css = f"""
    <style>

    /* MAIN BACKGROUND */
    .stApp {{
        background-image:
            linear-gradient(rgba(0,0,0,.65), rgba(0,0,0,.85)),
            url("data:image/jpg;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: linear-gradient(
            180deg,
            #0b1d2a 0%,
            #0f2f3a 50%,
            #1a3d45 100%
        );
        border-right: 1px solid rgba(255,180,80,0.4);
    }}

    /* TEXT */
    h1, h2, h3, p, label {{
        color: #F6E8C7 !important;
        font-family: Georgia, serif;
    }}

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

def init_page():
    check_login()
    apply_theme()

    with st.sidebar:
        st.markdown("---")

        st.markdown(f"""
        <div style="text-align:center; padding:1rem;">
            <div style="color:#D4AF37; font-size:1rem;">Planeswalker</div>
            <div style="font-size:1.6rem; font-weight:900; color:#F6E8C7;">
                {st.session_state["user"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("Main.py")