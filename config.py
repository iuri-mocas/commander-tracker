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
        background: linear-gradient(180deg, #0b1d2a 0%, #0f2f3a 50%, #1a3d45 100%);
        border-right: 1px solid rgba(255,180,80,0.4);
        box-shadow: inset 0 0 30px rgba(255,140,60,0.15);
    }

    [data-testid="stSidebar"] * {
        color: #F6E8C7 !important;
        font-family: Georgia, serif;
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