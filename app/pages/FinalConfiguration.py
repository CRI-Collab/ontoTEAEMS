from topsis import *
import streamlit as st
from utils import likertValue
from ontology.loadOntology import OntologyManager
from pages.TechnicalExpert import displayAlternatives
from dotenv import load_dotenv 
import os, json
from patternManager import update_functional_patterns_with_variants

load_dotenv()
patternVariantPath = os.getenv('PATTERN_VARIANTS')
PATTERN_VARIANTS = json.loads(patternVariantPath)

current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
ontoManager = OntologyManager(ONTOLOGY_PATH)

st.sidebar.info(
    "The Result Comes From Topsis Algorithm RANKED by Softgoals Preference.\n\n"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/finalX.css"))

def calculate_topsis():
    load_css(cssPaths)
    functional_patterns = st.session_state.get("functional_patterns", [])
    
    #Mettre à jour functional_patterns avec les variants
    functional_patterns = update_functional_patterns_with_variants(functional_patterns, PATTERN_VARIANTS)
    temp_matrix = {}
    
    for pattern in functional_patterns:
        if st.session_state.get(f"choix_original_{pattern}", False):
            temp_matrix[pattern] = st.session_state.matriceA_dict.get(pattern, {})
        elif st.session_state.get(f"choix_variant_{pattern}", False):
            temp_matrix[pattern] = st.session_state.matriceB_dict.get(pattern, {})
        else:
            temp_matrix[pattern] = st.session_state.matriceA_dict.get(pattern, {})
    
    data = []
    for pattern in functional_patterns:
        row = [likertValue(temp_matrix[pattern].get(softgoal, 0)) for softgoal in st.session_state.selectedSoftgoals]
        data.append(row)

    decisionMatrix = pd.DataFrame(data, index=functional_patterns, columns=st.session_state.selectedSoftgoals)
    ####st.write("Matrix Decision", decisionMatrix)
    
    softgoal_preferences = st.session_state.get("softpreferences", {})
    weights = calculate_weights(softgoal_preferences)
    
    criteria = {
        softgoal: "max" if preference == 1 else "min"
        for softgoal, preference in softgoal_preferences.items()
    }
    try:
        rang = topsisAlgorithm(decisionMatrix, weights=list(weights.values()), criteria_directions=criteria)
        topsisAffichage(rang, ontoManager, st.session_state.selectedSoftgoals)

    except Exception as e:
        st.error(f"Erreur lors de l'application de TOPSIS: {e}")


def affichageABC():
    calculate_topsis()
    softgoal_preferences = st.session_state.get("softpreferences", {})
    non_functional_patterns = st.session_state.get("non_functional_patterns", [])
    
    variants_to_exclude = set()
    for variants in PATTERN_VARIANTS.values():
        variants_to_exclude.update(variants)

    nonfunctionalpatterns = [pattern for pattern in non_functional_patterns if pattern not in variants_to_exclude]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back To Configuration Validation"):
            st.session_state.step = "comparer"
            st.switch_page("pages/TechnicalExpert.py")
    with col2:
        if st.button("📌 Show Non Functional Patterns"):
            st.session_state.show_alternatives = True
    
    if st.session_state.get("show_alternatives", False):
        displayAlternatives(nonfunctionalpatterns, softgoal_preferences)

affichageABC()
#calculate_topsis()