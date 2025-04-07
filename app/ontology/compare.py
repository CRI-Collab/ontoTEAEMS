import streamlit as st
import pandas as pd
import os
from utils import display_slider, update_checkboxes, likertValue
from ontology.loadOntology import OntologyManager
from topsis import *
from kbase.dbManager import DatabaseManager

# Chargement de l'ontologie
current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
ontoManager = OntologyManager(ONTOLOGY_PATH)
loadStatus = ontoManager.loadOntology()
st.info(loadStatus)

pd.set_option('future.no_silent_downcasting', True)

def generate_sg_map(pscores):
    """Génère une carte des softgoals améliorés et dégradés."""
    sg_map = {"improved": [], "harmed": []}
    for softgoal, score in pscores.items():
        if score in ["+", "++"]:
            sg_map["improved"].append(softgoal)
        elif score in ["-", "--"]:
            sg_map["harmed"].append(softgoal)
    return sg_map

def compare_patterns():
    if "current_pattern_index" not in st.session_state:
        st.session_state.current_pattern_index = 0
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    patterns_to_compare = st.session_state.get("patterns_to_compare", [])
    if not patterns_to_compare:
        st.warning("Aucun pattern à comparer.")
        return

    softgoal_preferences = st.session_state.get("softpreferences", {})
    softgoal_weights = st.session_state.get("softweights", {})

    ######
    ##### CONTRADICTION ANALYSIS BEFORE EXECUTING TOPSIS ALGO FOR RECOMMENDETION
    if st.session_state.current_pattern_index >= len(patterns_to_compare):
        contradictoryPattern = check_contradictions(st.session_state.final_matrix)

        if contradictoryPattern:
            st.error("### Patterns contradictoires détectés")
            st.write("Les paires de patterns suivantes ont des valeurs opposées pour un ou plusieurs critères :")
            
            for pair in contradictoryPattern:
                st.write(
                    f"- **{pair['pattern_1']}** ({pair['value_1']}) et **{pair['pattern_2']}** ({pair['value_2']}) "
                    f"sont contradictoire pour le softgoal **{pair['criteria']}**."
                )
            st.write("### Veuillez Reselectionner les patterns en supprimant les Patterns contradictoires :")
            all_patterns = list(st.session_state.final_matrix.index)
            patterns_to_remove = st.multiselect(
                "Sélectionnez les patterns à supprimer",
                options=all_patterns,
                key="patterns_to_remove"
            )

            if st.button("Supprimer et réexécuter TOPSIS"):
                st.session_state.final_matrix = st.session_state.final_matrix.drop(patterns_to_remove)
                st.session_state.current_pattern_index = 0
                st.rerun()
            else:
                st.write("### Tous les patterns ont été validés. Voici la matrice finale :")
                st.dataframe(st.session_state.final_matrix)

                value_mapping = {"+": 1, "++": 2, "-": -1, "--": -2, " ": 0}
                numeric_matrix = st.session_state.final_matrix.replace(value_mapping).fillna(0)
                selected_softgoals = numeric_matrix.columns       
                decision_matrix = numeric_matrix
            
                st.write("### Matrice de Décision")
                st.dataframe(decision_matrix)
                weights = np.ones(decision_matrix.shape[1])

                try:
                    rang = topsisAlgorithm(decision_matrix, weights)
                    topsisAffichage(rang, ontoManager, selected_softgoals)
                except:
                    st.error(f"Erreur lors de l'application de TOPSIS")
            return 

    #####
    #### END CONTRADICTION ANALYSIS
        #st.session_state.step = "execute_topsis"
        #st.rerun()

    pattern = patterns_to_compare[st.session_state.current_pattern_index]
    original_scores = st.session_state.matriceA_dict.get(pattern, {})
    variant_scores = st.session_state.matriceB_dict.get(pattern, {})

    sgmap0 = generate_sg_map(original_scores)
    sgmapV = generate_sg_map(variant_scores)
    
    st.success(f"#### Pattern: {pattern}")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.success(f"{pattern} (Centralized)")
            with st.expander("Softgoals Improved and Harmed"):
                st.write("Softgoals améliorés :", ", ".join(sgmap0["improved"]))
                st.write("Softgoals dégradés :", ", ".join(sgmap0["harmed"]))
            for softgoal, score in original_scores.items():
                if softgoal in softgoal_preferences:
                    display_slider(
                        f"{softgoal}", 
                        likertValue(score), 
                        key=f"{pattern}_{softgoal}_original", 
                        container_class="slider-container-original" )
            st.checkbox(
                "Choisir Original (Centralized)",
                key=f"choix_original_{pattern}",
                value=st.session_state.get(f"choix_original_{pattern}", False),
                on_change=update_choice,
                args=(pattern, "original"),
            )

    with col2:
        with st.container(border=True):
            st.warning(f"{pattern} (Decentralized)")
            with st.expander("Softgoals Improved and Harmed"):
                st.write("Softgoals améliorés :", ", ".join(sgmapV["improved"]))
                st.write("Softgoals dégradés :", ", ".join(sgmapV["harmed"]))
            for softgoal, score in variant_scores.items():
                if softgoal in softgoal_preferences:
                    display_slider(
                        f"{softgoal}", 
                        likertValue(score), 
                        key=f"{pattern}_{softgoal}_variant", 
                        container_class="slider-container-variant"
                    )
            st.checkbox(
                "Choisir Variant (Decentralized)",
                key=f"choix_variant_{pattern}",
                value=st.session_state.get(f"choix_variant_{pattern}", False),
                on_change=update_choice,
                args=(pattern, "variant"),
            )

    if st.button("Next"):
        st.session_state.current_pattern_index += 1
        st.rerun()

    #if st.session_state.current_pattern_index == len(patterns_to_compare):
        #if st.button("Valider et Exécuter TOPSIS"):
            #execute_topsis()

def update_choice(pattern, choice):
    if choice == "original":
        st.session_state[f"choix_original_{pattern}"] = True
        st.session_state[f"choix_variant_{pattern}"] = False
        st.session_state.user_choices[pattern] = "Original (Centralized)"
    elif choice == "variant":
        st.session_state[f"choix_original_{pattern}"] = False
        st.session_state[f"choix_variant_{pattern}"] = True
        st.session_state.user_choices[pattern] = "Variant (Decentralized)"

def check_contradictions(final_matrix):
    contradictory_pairs = []
    for col in final_matrix.columns:
        positive_patterns = final_matrix.index[final_matrix[col].isin(["+", "++"])].tolist()
        negative_patterns = final_matrix.index[final_matrix[col].isin(["-", "--"])].tolist()

        for pos_pattern in positive_patterns:
            for neg_pattern in negative_patterns:
                contradictory_pairs.append({
                    "pattern_1": pos_pattern,
                    "pattern_2": neg_pattern,
                    "criteria": col,
                    "value_1": final_matrix.loc[pos_pattern, col],
                    "value_2": final_matrix.loc[neg_pattern, col]
                })
    return contradictory_pairs