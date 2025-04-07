import os
import pandas as pd
import streamlit as st
from owlready2 import get_ontology
from ontology.loadOntology import OntologyManager

current_dir = os.path.dirname(__file__)
onto_path = os.path.normpath(os.path.join(current_dir, "./ontology/TestMine.owl"))
onto_manager = OntologyManager(onto_path)

def loadMatrix():
    current_dir = os.path.dirname(__file__)
    matA_path = os.path.normpath(os.path.join(current_dir, "./data/XXuPatterns.csv"))
    matB_path = os.path.normpath(os.path.join(current_dir, "./data/XXuPatterns2.csv"))
    
    matriceA = pd.read_csv(matA_path)
    matriceB = pd.read_csv(matB_path)

    if matriceA.empty or matriceB.empty:
        st.error("Erreur lors du chargement des fichiers CSV. Veuillez vérifier les fichiers.")
        st.stop()
    st.session_state.matriceA_dict = matriceA.set_index("Design Patterns").to_dict(orient="index")
    st.session_state.matriceB_dict = matriceB.set_index("Design Patterns").to_dict(orient="index")

def LoadPatterns():
    if 'matriceA_dict' not in st.session_state or 'matriceB_dict' not in st.session_state:
        st.error("Les matrices n'ont pas été chargées. Veuillez d'abord charger les matrices.")
        return
    patterns_from_matA = set(st.session_state.matriceA_dict.keys())
    patterns_from_matB = set(st.session_state.matriceB_dict.keys())

    combined_patterns = patterns_from_matA.union(patterns_from_matB)

    if not combined_patterns:
        st.warning("Aucun pattern trouvé dans les matrices.")
        return

    return list(combined_patterns)

def LoadPatternsZ():
    patterns = onto_manager.getAllPatternss()
    if not patterns:
        st.warning("Aucun pattern trouvé dans l'ontologie.")
        return

    pattern_names = [pattern.name for pattern in patterns]
    #print(pattern_names)
    st.session_state.patterns_to_compare = pattern_names