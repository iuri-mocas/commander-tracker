import streamlit as st
from supabase import create_client
import base64
import os

def is_admin():
    return st.session_state.get("user") == st.secrets.get("ADMIN_NAME")

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

    background_css = ""
    if bg:
        background_css = f'''
        background-image:
            linear-gradient(rgba(0,0,0,.65), rgba(0,0,0,.85)),
            url("data:image/jpg;base64,{bg}");
        '''

    css = f'''
    <style>
    .stApp {{
        {background_css}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0b1d2a 0%, #0f2f3a 50%, #1a3d45 100%);
        border-right: 1px solid rgba(255,180,80,0.4);
        box-shadow: inset 0 0 30px rgba(255,140,60,0.15);
    }}
    
    [data-testid="stSidebar"] * {{
        color: #F6E8C7 !important;
        font-family: Georgia, serif;
    }}

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{
        color: #F6E8C7 !important;
    }}

    h1, h2, h3, p, label {{
        color: #F6E8C7 !important;
        font-family: Georgia, serif;
    }}

    .home-title {{
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        color: #F6E8C7;
        font-family: Georgia, serif;
        text-shadow: 0 0 25px rgba(0,0,0,.9);
        margin-top: 4rem;
    }}

    .home-subtitle {{
        text-align: center;
        color: #D4AF37;
        font-size: 1.3rem;
        margin-bottom: 3rem;
    }}

    div.stButton > button {{
        border-radius: 18px !important;
        border: 1px solid rgba(212,175,55,.9) !important;
        background: linear-gradient(145deg, rgba(16,35,52,.95), rgba(8,12,22,.98)) !important;
        color: #F6E8C7 !important;
        font-weight: 900 !important;
        font-family: Georgia, serif !important;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, rgba(90,65,22,.98), rgba(12,18,32,.98)) !important;
        border: 2px solid gold !important;
    }}
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)


def init_page():
    check_login()
    apply_theme()

    with st.sidebar:
        st.markdown("---")

        st.markdown(f"""
        <div style="text-align:center; padding:1rem;">
            <div style="color:#D4AF37;">Planeswalker</div>
            <div style="font-size:1.6rem; font-weight:900; color:#F6E8C7;">
                {st.session_state["user"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("Main.py")