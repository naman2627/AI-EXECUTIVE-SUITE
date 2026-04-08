import streamlit as st


def safe_rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()


def render_step(title, content):
    st.markdown(f""" <div style="
        background: rgba(255,255,255,0.03);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.08);
    "> <h3>{title}</h3> <p>{content}</p> </div>
""", unsafe_allow_html=True)
