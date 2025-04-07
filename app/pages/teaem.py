import streamlit as st
import os
import pandas as pd
from matrix import loadMatrix, LoadPatterns
from kbase.dbManager import DatabaseManager
from kbase.loadkbase import loadKnowledgebase

#st.set_page_config(page_title="Configuration of Apps", layout="wide")
#st.title("Configuration of Apps 🛠️")
#st.sidebar.title("BC-TEAEM DEV Apps")

if "DISPLAY" in os.environ or "STREAMLIT_ENV" not in os.environ:
    try:
        from tkinter import W
    except ImportError:
        print("Tkinter is not available in this environment.")

def load_css(fichier):
    with open(fichier) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
current_dir = os.path.dirname(__file__)
ontoPaths = os.path.normpath(os.path.join(current_dir, "../ontology/TestMine.owl"))
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/DeX.css"))
db_manager = DatabaseManager()

if "refresh" not in st.session_state:
    st.session_state["refresh"] = False
if 'final_matrix' not in st.session_state:
    st.session_state.final_matrix = pd.DataFrame()
if 'patterns_to_compare' not in st.session_state:
    st.session_state.patterns_to_compare = []
    
if 'step' not in st.session_state:
    st.session_state.step = "domainExpert" 
    #Etapes : soft, comparer, decide, calculate, final

if "recommendations" not in st.session_state:
    st.session_state.recommendations = {}
    
if "user_choices" not in st.session_state:
    st.session_state.user_choices = {}

def execution():
    loadMatrix()
    
    if st.session_state.step == "domainExpert":
        load_css(cssPaths)
        loadKnowledgebase(db_manager, ontoPaths)
        st.session_state.patterns_to_compare = LoadPatterns()
        #print(st.session_state.patterns_to_compare)
        st.switch_page("pages/DomainExpert.py")

    if st.session_state.step == "technicalExpert":
        st.switch_page("pages/TechnicalExpert.py")

    if st.session_state.step == "final":
        st.switch_page("pages/FinalConfiguration.py")
        #st.session_state.show_alternatives = False

if __name__ == "__main__":
    execution()