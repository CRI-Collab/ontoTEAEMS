import streamlit as st
import Explore.exploreOntoScore
import Explore.exploreMatrix
from kbase import dbManager

page = st.sidebar.radio("Ontology Exploration", [ "Explore Ontology", "Matrix Quantification"], key="page_selectbox")

if page == "Explore Ontology":
    Explore.exploreOntoScore.ExploreWithScore(dbManager)

elif page == "Matrix Quantification":
    Explore.exploreMatrix.ExploreMatrixQuantification(dbManager)

if st.sidebar.button("Back To Configuration"):
    st.switch_page("pages/configuration.py")

button_style = """
    <style>
    .stButton>button {
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 10px 24px;
        background-color: white;
        color: black;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFFACD;
        color: black;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)