import streamlit as st
from utils.registry import TOOLS, CATEGORIES

def inject_css():
    st.markdown("""<style>
    .block-container{max-width:1180px;padding-top:1.6rem;padding-bottom:3rem}
    h1,h2,h3{letter-spacing:-.025em}
    .uh-hero{padding:1.7rem 1.8rem;border:1px solid #e4e7ef;border-radius:18px;background:linear-gradient(120deg,#f7f8ff,#fff);margin-bottom:1.2rem}
    .uh-kicker{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#4f46e5}
    .uh-card{height:150px;padding:1rem 1.05rem;border:1px solid #e5e7eb;border-radius:14px;background:#fff;margin-bottom:.4rem}
    .uh-card h4{margin:.35rem 0 .4rem;font-size:1.02rem}
    .uh-card p{color:#596273;font-size:.88rem;line-height:1.4}
    div[data-testid="stButton"] button{border-radius:9px;font-weight:600}
    .uh-foot{color:#697386;font-size:.8rem;border-top:1px solid #e5e7eb;padding-top:1rem;margin-top:2rem}
    @media(max-width:700px){.block-container{padding-left:1rem;padding-right:1rem}.uh-hero{padding:1.2rem}}
    </style>""", unsafe_allow_html=True)

def _open_tool(name, category):
    st.session_state["active_tool"] = name
    st.session_state["page"] = category
    st.session_state["nav_radio"] = category

def tool_card(tool, idx):
    category,name,desc,keywords=tool
    with st.container(border=True):
        st.caption(category)
        st.markdown(f"**{name}**")
        st.write(desc)
        st.button("Open tool", key=f"open_{idx}", use_container_width=True,
                  on_click=_open_tool, args=(name, category))

def sidebar():
    with st.sidebar:
        st.image("assets/logo.svg", width=48)
        st.markdown("## UtilityHub")
        st.caption("Everyday tools, in one place")
        pages=["Home","All Tools"] + CATEGORIES[1:] + ["About & Help"]
        current=st.session_state.get("page","Home")
        chosen=st.radio("Navigate", pages, index=pages.index(current) if current in pages else 0, key="nav_radio")
        st.session_state["page"]=chosen
        st.divider()
        st.caption("Privacy-first by design")
        st.caption("Files are processed in-session; hosting environments may have their own logs and limits.")
