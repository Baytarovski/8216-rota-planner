import streamlit as st
from admin_panel import render_admin_panel
from core.data_utils import load_rotas, save_rotas, delete_rota

st.set_page_config(page_title="Admin Panel", layout="wide")

st.session_state.setdefault("is_admin", False)
ADMIN_CREDENTIALS = {"admin": "17500#"}


def admin_login():
    if st.session_state.get("is_admin"):
        return

    st.info("🔐 Enter your admin credentials below to unlock admin tools.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username in ADMIN_CREDENTIALS and password == ADMIN_CREDENTIALS[username]:
        st.session_state["is_admin"] = True
        st.session_state["admin_user"] = username
        st.success("Access granted. Admin tools unlocked.")
    elif username or password:
        st.session_state["is_admin"] = False
        st.error("Incorrect username or password.")


admin_login()

if not st.session_state.get("is_admin", False):
    st.stop()


@st.cache_data
def cached_load_rotas():
    return load_rotas()


rotas = cached_load_rotas()

render_admin_panel(rotas, save_rotas, delete_rota)

if "feedback" in st.session_state:
    st.success(st.session_state.pop("feedback"))

