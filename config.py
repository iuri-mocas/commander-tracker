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


def check_login():
    if "user" not in st.session_state:
        st.switch_page("Main.py")


def img_to_base64(path):
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def apply_theme():
    bg = img_to_base64("assets/mtg_bg.jpg")

    css = """
    <style>

    h1, h2, h3, p, label {
        color: #F6E8C7 !important;
        font-family: Georgia, serif;
    }

    [data-testid="stSidebar"] {
        display: none;
        background: linear-gradient(180deg, #0b1d2a 0%, #0f2f3a 50%, #1a3d45 100%);
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

    .login-button button {
        height: 60px !important;
    }

    .stApp {
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    </style>
    """

    if bg:
        css += f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0,0,0,.65), rgba(0,0,0,.85)),
                url("data:image/jpg;base64,{bg}");
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