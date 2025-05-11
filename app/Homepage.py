import streamlit as st

st.set_page_config(
    page_title="BC-ONTOTEAM - Welcome",
    page_icon=":busts_in_silhouette:",
    layout="wide"
)

with open('css/home.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.sidebar.title("Welcome to BC-TEAM DEV")
st.sidebar.info(
    "Explore the power of blockchain with BC-TEAM DEV"
)

col1, col2 = st.columns([1, 4])
with col1:
    st.image("data/blockchain_icon.png", width=100)
with col2:
    st.title("Welcome to BC-ONTOTEAM")

st.markdown("""
<div class="banner">
    <h2>BC-ONTOTEAM</h2>
    <p>Generate optimal blockchain architectures combining pattern ontologies and softgoals</p>
    <p>Guiding the process through user preferences</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
## 🏁 Get Started
Ready to test our application?
""")

if "config_done" not in st.session_state:
    st.session_state["config_done"] = False

col1, col2, col3 = st.columns(3)
with col2:
    if st.button("🚀 Launch BC-ONTOTEAM", use_container_width=True):
        st.switch_page("pages/View.py")

#
#st.markdown("""
#    <div class="footer">
#        © 2024 BC-TEAM DEV. All rights reserved.<br>
#    </div>
#""", unsafe_allow_html=True)