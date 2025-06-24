import streamlit as st
from admin_panel import render_admin_panel
from core.data_utils import load_rotas, save_rotas, delete_rota, archive_deleted_rota
from app_texts import ADMIN_PANEL_HELP

st.set_page_config(page_title="Admin Panel", layout="wide")


def render_sidebar():
    with st.sidebar.expander("📘 Admin Panel Guide", expanded=True):
        st.markdown(ADMIN_PANEL_HELP)


render_sidebar()

st.session_state.setdefault("is_admin", False)
ADMIN_CREDENTIALS = {
    "admin": "17500#",
    "Marco": "429327",
}


def admin_login():
    if st.session_state.get("is_admin"):
        return

    st.info("🔐 Enter your username and password below to unlock admin tools.")
    username = st.text_input("Username", key="admin_username")
    password = st.text_input("Password", type="password", key="admin_password")

    if st.button("Login"):
        if username in ADMIN_CREDENTIALS and password == ADMIN_CREDENTIALS[username]:
            st.session_state["is_admin"] = True
            st.session_state["admin_user"] = username
            st.success("Access granted. Admin tools unlocked.")
        else:
            st.session_state["is_admin"] = False
            st.error("Incorrect username or password.")


admin_login()

if not st.session_state.get("is_admin", False):
    st.stop()


@st.cache_data
def cached_load_rotas():
    return load_rotas()


@st.cache_data
def cached_load_deleted_rotas():
    from core.data_utils import load_deleted_rotas
    return load_deleted_rotas()


rotas = cached_load_rotas()
deleted_rotas = cached_load_deleted_rotas()

render_admin_panel(rotas, deleted_rotas, save_rotas, delete_rota, archive_deleted_rota)

if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

