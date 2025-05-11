from utility.topsis import *
import streamlit as st
from utility.utils import likertValue
from ontology.loadOntology import OntologyManager
from pages.TechnicalExpert import displayAlternatives, build_decision_matrix_for_topsis
from dotenv import load_dotenv 
import os, json

load_dotenv()
patternVariantPath = os.getenv('PATTERN_VARIANTS')
PATTERN_VARIANTS = json.loads(patternVariantPath)

current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
ontoManager = OntologyManager(ONTOLOGY_PATH)

st.sidebar.markdown("""
<div style="
    background: linear-gradient(145deg, #f8f9fa, #e9ecef);
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #4e73df;
    margin-bottom: 20px;
">
    <h4 style="
        color: #2e3a4d;
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.1em;
    ">
        <i class="fas fa-chart-line" style="margin-right: 8px;"></i>
        Recommendations
    </h4>
    <p style="
        color: #4a5568;
        font-size: 0.9em;
        line-height: 1.5;
        margin-bottom: 5px;
    ">
        Results are computed using the <strong>TOPSIS</strong> (Technique for Order Preference by Similarity to Ideal Solution) multi-criteria decision analysis method.
    </p>
    <p style="
        color: #4a5568;
        font-size: 0.85em;
        line-height: 1.4;
        margin-bottom: 0;
    ">
        <i class="fas fa-info-circle" style="margin-right: 5px;"></i>
        Patterns are ranked based on their alignment with your prioritized softgoals.
    </p>
</div>
""", unsafe_allow_html=True)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/finalX.css"))

def calculate_topsis():
    load_css(cssPaths)
    selectedPattern = st.session_state.get("selectedPatterns", {})
    selectedSoftgoals = st.session_state.get("selectedSoftgoals", [])
    
    decision_matrix = build_decision_matrix_for_topsis()
    data = []
    for pattern, scores in zip(selectedPattern, decision_matrix):
        row = [likertValue(scores.get(softgoal, 0)) for softgoal in selectedSoftgoals]
        data.append(row)

    decisionMatrix = pd.DataFrame(data, index=selectedPattern.keys(), columns=selectedSoftgoals)
    
    softgoal_preferences = st.session_state.get("softpreferences", {})
    weights = calculate_weightsBack(softgoal_preferences)
    
    criteria = {
        softgoal: "max" if preference == 1 else "min"
        for softgoal, preference in softgoal_preferences.items()
    }

    try:
        ranking = topsisAlgorithm(
            decisionMatrix,
            weights=list(weights.values()),
            criteria_directions=criteria
        )
        topsisAffichage(ranking, ontoManager, selectedSoftgoals)
    except Exception as e:
        st.error(f"Erreur lors de l'application de TOPSIS: {e}")

def calculate_topsis2():
    load_css(cssPaths)
    #functional_patterns = st.session_state.get("functional_patterns", [])
    selectedPattern = st.session_state.get("selectedPatterns", {})
    selectedSofgoals = st.session_state.get("selectedSoftgoals", [])
    
    temp_matrix = {}
    for pattern in selectedPattern:
        if st.session_state.get(f"choix_original_{pattern}", False):
            temp_matrix[pattern] = st.session_state.matriceA_dict.get(pattern, {})
        elif st.session_state.get(f"choix_variant_{pattern}", False):
            temp_matrix[pattern] = st.session_state.matriceB_dict.get(pattern, {})
        else:
            temp_matrix[pattern] = st.session_state.matriceA_dict.get(pattern, {})
    
    data = []
    for pattern in selectedPattern:
        row = [likertValue(temp_matrix[pattern].get(softgoal, 0)) for softgoal in selectedSofgoals]
        data.append(row)

    decisionMatrix = pd.DataFrame(data, index=selectedPattern, columns=st.session_state.selectedSoftgoals)
    st.write("Matrix Decision", decisionMatrix)
    
    softgoal_preferences = st.session_state.get("softpreferences", {})
    weights = calculate_weights(softgoal_preferences)
    
    criteria = {
        softgoal: "max" if preference == 1 else "min"
        for softgoal, preference in softgoal_preferences.items()
    }
    try:
        rang = topsisAlgorithm(decisionMatrix, weights=list(weights.values()), criteria_directions=criteria)
        topsisAffichage(rang, ontoManager, selectedSofgoals)

    except Exception as e:
        st.error(f"Erreur lors de l'application de TOPSIS: {e}")

def execute():
    calculate_topsis()
    softgoal_preferences = st.session_state.get("softpreferences", {})
    non_functional_patterns = st.session_state.get("non_functional_patterns", [])
    
    variants_to_exclude = set()
    for variants in PATTERN_VARIANTS.values():
        variants_to_exclude.update(variants)

    nonfunctionalpatterns = [pattern for pattern in non_functional_patterns if pattern not in variants_to_exclude]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Back To Configuration Validation"):
            st.session_state.step = "comparer"
            st.switch_page("pages/TechnicalExpert.py")
    with col2:
        if st.button("📌 Show Non Functional Patterns"):
            st.session_state.show_alternatives = True
    
    if st.session_state.get("show_alternatives", False):
        displayAlternatives(nonfunctionalpatterns, softgoal_preferences)

execute()