import streamlit as st
from admin_panel import render_admin_panel
from core.data_utils import load_rotas, save_rotas, delete_rota

st.set_page_config(page_title="Admin Panel", layout="wide")

st.session_state.setdefault("is_admin", False)


def admin_login():
    if st.session_state.get("is_admin"):
        return
    st.info("🔐 Enter the access code below to unlock admin tools.")
    code_input = st.text_input("Access Code:", type="password")
    if code_input == "17500#":
        st.session_state["is_admin"] = True
        st.success("Access granted. Admin tools unlocked.")
    elif code_input:
        st.session_state["is_admin"] = False
        st.error("Incorrect code.")


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

