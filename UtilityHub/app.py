import streamlit as st
from utils.registry import TOOLS, CATEGORIES
from utils.ui import inject_css, sidebar, tool_card
from pages.tools import run_tool

st.set_page_config(page_title="UtilityHub — Everyday tools",page_icon="assets/logo.svg",layout="wide",initial_sidebar_state="expanded")
inject_css()
st.session_state.setdefault("page","Home")
st.session_state.setdefault("active_tool","")
sidebar()
page=st.session_state["page"]

def _open_category(category):
    st.session_state["page"] = category
    st.session_state["nav_radio"] = category

def _browse_all():
    st.session_state["page"] = "All Tools"
    st.session_state["nav_radio"] = "All Tools"

def directory(tools):
    if not tools:
        st.info("No tools match your search. Try another keyword or category.")
        return
    for start in range(0,len(tools),3):
        cols=st.columns(3)
        for col,tool in zip(cols,tools[start:start+3]):
            with col: tool_card(tool,TOOLS.index(tool))

if page=="Home":
    st.markdown('<div class="uh-hero"><div class="uh-kicker">Simple tools. One workspace.</div><h1>Everyday utilities, without the clutter.</h1><p>Work with files, text, data, calculations, and developer helpers in one practical workspace.</p></div>',unsafe_allow_html=True)
    query=st.text_input("Search tools...",placeholder="Try “JSON”, “resize image”, “PDF”, or “CSV”",key="home_search")
    featured_names={"Text workbench","JSON formatter / validator","Image resize","CSV workbench","QR code generator","Unit converter"}
    filtered=[t for t in TOOLS if (not query or query.lower() in " ".join(t).lower())]
    if query:
        st.subheader("Search results"); directory(filtered)
    else:
        st.subheader("Explore categories")
        cats=st.columns(3)
        for i,cat in enumerate(CATEGORIES[1:]):
            with cats[i%3]:
                st.button(cat, key=f"home_cat_{i}", use_container_width=True,
                          on_click=_open_category, args=(cat,))
        st.subheader("Featured tools")
        directory([t for t in TOOLS if t[1] in featured_names])
        st.subheader("Privacy-focused workflow")
        st.write("Tools run in the app process and do not need paid APIs. Avoid uploading confidential data to a public deployment; hosting providers and deployment settings can affect privacy.")
        st.button("Browse all tools", type="primary", on_click=_browse_all)
elif page=="All Tools":
    st.title("All tools")
    q=st.text_input("Search tools...",placeholder="Search names, descriptions, or keywords")
    cats=st.multiselect("Filter categories",CATEGORIES[1:])
    results=[t for t in TOOLS if (not q or q.lower() in " ".join(t).lower()) and (not cats or t[0] in cats)]
    st.caption(f"{len(results)} tool(s)")
    directory(results)
elif page=="About & Help":
    st.title("About & Help"); run_tool("About UtilityHub")
else:
    st.title(page)
    available=[t for t in TOOLS if t[0]==page]
    if available:
        selected_names=[t[1] for t in available]
        preferred = st.session_state.get("active_tool", "")
        default_index = selected_names.index(preferred) if preferred in selected_names else 0
        chosen=st.selectbox("Choose a tool",selected_names,index=default_index,key=f"category_tool_{page}")
        st.session_state["active_tool"] = chosen
        run_tool(chosen)
    else:
        st.info("Choose a category from the sidebar.")
st.markdown('<div class="uh-foot">UtilityHub · Version 1.0.0 · Local-first processing · Results are only available for download when you choose to save them.</div>',unsafe_allow_html=True)
