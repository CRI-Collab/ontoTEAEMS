from matplotlib.colorbar import ColorbarBase
import streamlit as st
import pandas as pd
import numpy as np
import os
from utils import *
from topsis import *
from ontology.loadOntology import OntologyManager

st.sidebar.info(
    "As Technical Expert , you need to VALDIATE one or more configuration.\n\n"
)
current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
ontoManager = OntologyManager(ONTOLOGY_PATH)
ontoManager.loadOntology()

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
current_dir = os.path.dirname(__file__)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/TeX.css"))
pd.set_option('future.no_silent_downcasting', True)

PATTERN_VARIANTS = {
    "Oracle": ["Centralized_Oracle", "Decentralized_Oracle"],
    "Reverse_Oracle": ["Centralized_Reverse_Oracle", "Decentralized_Reverse_Oracle"],
    "Encrypting_On-Chain_Data": ["Encrypting_On-Chain_Data_Secure_Multi-Party_Computation", "Encrypting_On-Chain_Data_Zero-Knowledge_Proof"],
    "Off-Chain_Data_Storage": ["Off-Chain_Data_Storage_Cloud_Storage", "Off-Chain_Data_Storage_Distributed_Cryptographic_Proof"]
}

from matplotlib.colorbar import ColorbarBase
import streamlit as st
import pandas as pd
import numpy as np
import os
from utils import *
from topsis import *
from ontology.loadOntology import OntologyManager

st.sidebar.info(
    "As Technical Expert , you need to VALDIATE one or more configuration.\n\n"
)
current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
ontoManager = OntologyManager(ONTOLOGY_PATH)
ontoManager.loadOntology()

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
current_dir = os.path.dirname(__file__)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/TeX.css"))
pd.set_option('future.no_silent_downcasting', True)

# Dictionnaire des variantes pour les patterns fonctionnels
PATTERN_VARIANTS = {
    # Patterns fonctionnels
    "Oracle": ["Centralized_Oracle", "Decentralized_Oracle"],
    "Reverse_Oracle": ["Centralized_Reverse_Oracle", "Decentralized_Reverse_Oracle"],
    "Encrypting_On-Chain_Data": ["Encrypting_On-Chain_Data_Secure_Multi-Party_Computation", "Encrypting_On-Chain_Data_Zero-Knowledge_Proof"],
    "Off-Chain_Data_Storage": ["Off-Chain_Data_Storage_Cloud_Storage", "Off-Chain_Data_Storage_Cryptograhic_Proof"]
}

def PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences):
    sgmap0 = mapStyles(patternScore)
    recommendations = {}
    decision = st.session_state.get("decisions", {}).get(pattern, None)

    # Si une décision existe, prioriser le variant correspondant
    if decision:
        if decision in patternScore:
            original_score = getScoreValue(patternScore[decision])
            if original_score >= 1:
                recommendations[pattern] = {"recommendation": "Original", "scores": patternScore}
        
        if decision in variantpatternScore:
            variant_score = getScoreValue(variantpatternScore[decision])
            if variant_score >= 1:
                recommendations[pattern] = {"recommendation": "Variant", "scores": variantpatternScore}
        
        if not recommendations.get(pattern):
            recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    # Si le pattern a des variantes, les traiter
    if pattern in PATTERN_VARIANTS:
        variants = PATTERN_VARIANTS[pattern]
        best_variant = None

        for variant in variants:
            scores_A = st.session_state.matriceA_dict.get(variant, {})
            scores_B = st.session_state.matriceB_dict.get(variant, {})

            # Vérifier si la variante respecte les préférences de l'utilisateur
            isOKvariant_A = all(
                (preference == 0 and getScoreValue(scores_A.get(softgoal, "")) >= 0) or  # Maintain: 0 ou plus
                (preference == 1 and getScoreValue(scores_A.get(softgoal, "")) >= 1)     # Improves: 1 ou plus
                for softgoal, preference in softgoal_preferences.items()
            )
            isOKvariant_B = all(
                (preference == 0 and getScoreValue(scores_B.get(softgoal, "")) >= 0) or  # Maintain: 0 ou plus
                (preference == 1 and getScoreValue(scores_B.get(softgoal, "")) >= 1)     # Improves: 1 ou plus
                for softgoal, preference in softgoal_preferences.items()
            )

            if isOKvariant_A or isOKvariant_B:
                best_variant = variant
                break  # On prend la première variante valide

        if best_variant:
            recommendations[pattern] = {"recommendation": best_variant, "scores": st.session_state.matriceA_dict.get(best_variant, {})}
        else:
            recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}
    else:
        # Traitement normal pour les autres patterns
        original_valid = all(
            (preference == 0 and getScoreValue(patternScore.get(softgoal, "")) >= 0) or  # Maintain: 0 ou plus
            (preference == 1 and getScoreValue(patternScore.get(softgoal, "")) >= 1)     # Improves: 1 ou plus
            for softgoal, preference in softgoal_preferences.items()
        )

        variant_valid = all(
            (preference == 0 and getScoreValue(variantpatternScore.get(softgoal, "")) >= 0) or  # Maintain: 0 ou plus
            (preference == 1 and getScoreValue(variantpatternScore.get(softgoal, "")) >= 1)     # Improves: 1 ou plus
            for softgoal, preference in softgoal_preferences.items()
        )

        if original_valid:
            recommendations[pattern] = {"recommendation": "Original", "scores": patternScore}
        elif variant_valid:
            recommendations[pattern] = {"recommendation": "Variant", "scores": variantpatternScore}
        else:
            recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    st.session_state.recommendations = recommendations

    for pattern, data in recommendations.items():
        if data["recommendation"] == "Aucune variante ne correspond aux préférences":
            with st.container(border=True):
                patterns = pattern.replace("_", " ")
                st.markdown(f"""
                <div class="pattern-container">
                    <span class="pattern-title">{patterns}</span>
                    <span class="pattern-message">No variant exactly matches your softgoal preferences</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""<p style="color: gray;">
                        Improved Softgoals : {", ".join(sgmap0["improved"])} </p>
                        <p style="color: gray;">  Harmed Softgoals : {", ".join(sgmap0["harmed"])} </p> """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if pattern in PATTERN_VARIANTS:
                        for variant in PATTERN_VARIANTS[pattern]:
                            scores = st.session_state.matriceA_dict.get(variant, {})
                            for softgoal, score in scores.items():
                                if softgoal in softgoal_preferences:
                                    displayBar(
                                        f"{softgoal}", 
                                        likertValue(score),
                                    ) 
                            st.checkbox(
                                f"{variant}",
                                key=f"choix_{variant}",
                                value=st.session_state.get(f"choix_{variant}", False),
                                on_change=update_choice,
                                args=(pattern, variant),
                            )
                    else:
                        for softgoal, score in patternScore.items():
                            if softgoal in softgoal_preferences:
                                displayBar(
                                    f"{softgoal}", 
                                    likertValue(score),
                                ) 
                        st.checkbox(
                            f"{patterns}_Org",
                            key=f"choix_original_{pattern}",
                            value=st.session_state.get(f"choix_original_{pattern}", False),
                            on_change=update_choice,
                            args=(pattern, "original"),
                        )
                with col2:
                    if pattern in PATTERN_VARIANTS:
                        for variant2 in PATTERN_VARIANTS[pattern]:
                            scores = st.session_state.matriceB_dict.get(variant2, {})
                            for softgoal, score in scores.items():
                                if softgoal in softgoal_preferences:
                                    displayBar(
                                        f"{softgoal}", 
                                        likertValue(score),
                                    )   
                            st.checkbox(
                                f"{variant2}",
                                key=f"choix_{variant2}",
                                value=st.session_state.get(f"choix_{variant2}", False),
                                on_change=update_choice,
                                args=(pattern, variant2),
                            )
                    else:
                        for softgoal, score in variantpatternScore.items():
                            if softgoal in softgoal_preferences:
                                displayBar(
                                    f"{softgoal}", 
                                    likertValue(score),
                                )   
                        st.checkbox(
                            f"{patterns}_Var",
                            key=f"choix_variant_{pattern}",
                            value=st.session_state.get(f"choix_variant_{pattern}", False),
                            on_change=update_choice,
                            args=(pattern, "variant"),
                        )

                        st.checkbox(
                            f"Trancher {patterns} ",
                            key=f"choix_none_{pattern}",
                            value=st.session_state.get(f"choix_none_{pattern}", False),
                            on_change=update_choice,
                            args=(pattern, "none"),
                        )
        else:
            with st.container(border=True):
                formatted_pattern = pattern.replace("_", " ")
                st.markdown(f"""
                <div class="pattern-container">
                    <span class="pattern-title">{formatted_pattern}</span>
                </div>
                """, unsafe_allow_html=True)
                st.write(f"**Recommandation :** {data['recommendation']}") 
                st.markdown(f"""<p style="color: gray;">
                        Improved Softgoals : {", ".join(sgmap0["improved"])} </p>
                        <p style="color: gray;">  Harmed Softgoals : {", ".join(sgmap0["harmed"])} </p>
                """, unsafe_allow_html=True)
                for softgoal, score in data["scores"].items():
                    if softgoal in softgoal_preferences:
                        displayBar(
                            f"{softgoal}", 
                            likertValue(score),
                        )



def displayFunctionalPatterns(functional_patterns, softgoal_preferences):
    st.markdown("""
        <div style="background-color: #f9f9f9; border-left: 6px solid #ffcc00; padding: 15px; border-radius: 5px;">
            <h3 style="color: green;">🛠️ Configuration Requise</h3>
            <p style="color: #555; font-size: 1.1em;">
                Pour configurer votre application, vous avez besoin des <strong>Functional Patterns</strong> suivants :
            </p>
        </div>
    """, unsafe_allow_html=True)

    half = len(functional_patterns) // 2
    firstPart = functional_patterns[:half]
    secondPart = functional_patterns[half:]

    col1, col2 = st.columns(2)
    with col1:
        for pattern in firstPart:
            patternScore = st.session_state.matriceA_dict.get(pattern, {})
            variantpatternScore = st.session_state.matriceB_dict.get(pattern, {})
            PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences)
    with col2:
        for pattern in secondPart:
            patternScore = st.session_state.matriceA_dict.get(pattern, {})
            variantpatternScore = st.session_state.matriceB_dict.get(pattern, {})
            PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences)

def displayAlternatives(non_functional_patterns, softgoal_preferences):
    st.markdown("### Alternatives")
    st.markdown('''##### :orange[The following patterns, if chosen, could potentially help improve your app design:]''')
    st.divider()
    
    selected_softgoals = set(softgoal_preferences.keys())
    containers = [st.columns(2) for _ in range((len(non_functional_patterns) + 1) // 2)]
    containers = [col for row in containers for col in row]

    alternPattern = False 

    if "selected_alternatives" not in st.session_state:
        st.session_state.selected_alternatives = []

    data = []
    patterns_to_compare = []

    for idx, pattern in enumerate(non_functional_patterns):
        scores = st.session_state.matriceA_dict.get(pattern, None)
        if scores is None:
            scores = st.session_state.matriceB_dict.get(pattern, None)

        if scores is None:
            continue

        iSoftgoals = [softgoal for softgoal in selected_softgoals if likertValue(scores.get(softgoal, "")) > 0]
        wSoftgoals = [softgoal for softgoal in selected_softgoals if likertValue(scores.get(softgoal, "")) < 0]

        if iSoftgoals:
            alternPattern = True
            patterns_to_compare.append(pattern)
            row = [likertValue(scores.get(softgoal, 0)) for softgoal in selected_softgoals]
            data.append(row)

    if alternPattern:
        decisionMatrix = pd.DataFrame(data, index=patterns_to_compare, columns=list(selected_softgoals))
        weights = calculate_weights(softgoal_preferences)
        criteria = {
            softgoal: "max" if preference == 1 else "min"
            #softgoal: "min" if softgoal == "Cost" else "max" 
            for softgoal, preference in softgoal_preferences.items()
        }

        try:
            topsisScore = topsisAlgorithm(decisionMatrix, weights=list(weights.values()), criteria_directions=criteria)
        except Exception as e:
            st.error(f"Erreur lors de l'application de TOPSIS: {e}")
            topsisScore = {}

        # Display each alternative pattern with its TOPSIS score
        for idx, pattern in enumerate(patterns_to_compare):
            scores = st.session_state.matriceA_dict.get(pattern, {})
            iSoftgoals = [softgoal for softgoal in selected_softgoals if likertValue(scores.get(softgoal, "")) > 0]
            wSoftgoals = [softgoal for softgoal in selected_softgoals if likertValue(scores.get(softgoal, "")) < 0]

            with containers[idx].container(border=True):
                st.write(f"#### {pattern}")
                st.success("**Improves:** " + ", ".join(iSoftgoals))
                if wSoftgoals:
                    st.error("**Worsens:** " + ", ".join(wSoftgoals))
                
                if pattern in topsisScore:
                    st.write(f"**Potential Satisfaction Score:** {topsisScore[pattern] * 100:.2f}%")
                
                is_selected = st.checkbox(
                    f"{pattern}",
                    key=f"checkbox_{pattern}",
                    value=pattern in st.session_state.selected_alternatives
                )
                
                if is_selected and pattern not in st.session_state.selected_alternatives:
                    st.session_state.selected_alternatives.append(pattern)
                elif not is_selected and pattern in st.session_state.selected_alternatives:
                    st.session_state.selected_alternatives.remove(pattern)
    else:
        st.warning("Aucune alternative ne satisfait au moins un des softgoals sélectionnés.")

    if st.button("Valider choix"):
        for pattern in st.session_state.selected_alternatives:
            if pattern not in st.session_state.functional_patterns:
                st.session_state.functional_patterns.append(pattern)
    
        st.session_state.selected_alternatives = []
        st.session_state.non_functional_patterns = [
            pattern for pattern in st.session_state.non_functional_patterns
            if pattern not in st.session_state.functional_patterns ]

        st.rerun()

def comparaisonPatterns():
    load_css(cssPaths)
    st.markdown('<div class="technical-expert-title">Technical Expert Configuration</div>', 
                unsafe_allow_html=True)
    if "current_pattern_index" not in st.session_state:
        st.session_state.current_pattern_index = 0

    patterns_to_compare = st.session_state.get("patterns_to_compare", [])

    if not patterns_to_compare:
        st.warning("Aucun pattern à comparer.")
        return

    softgoal_preferences = st.session_state.get("softpreferences", {})
    functional_patterns = st.session_state.get("functional_patterns", [])
    displayFunctionalPatterns(functional_patterns, softgoal_preferences)
    
    col3, col4, col5 = st.columns([3, 3, 3])

    with col4:
        if st.button("🔄 Softgoals refinement"):
            if "selectedSoftgoals" in st.session_state:
                st.write("Softgoals sélectionnés :", st.session_state.selectedSoftgoals)
            else:
                st.write("Aucun softgoal sélectionné.")
            st.session_state.calculate = {}
            st.session_state.step = "domainExpert"
            st.switch_page("pages/DomainExpert.py")
            st.rerun()

    with col3:
        if st.button("Domain Expert Decision"):
            patterns_to_decide = [pattern for pattern in patterns_to_compare if st.session_state.get(f"choix_none_{pattern}", False)]
            st.session_state.patterns_to_decide = patterns_to_decide
            st.session_state.step = "decide"
            st.switch_page("pages/DomainExpert.py")
            st.rerun()

    with col5:
        if st.button("💡 Validate Confguration"):
            st.session_state.step = "final"
            st.session_state.show_alternatives = False
            st.switch_page("pages/finalConfiguration.py")
            st.rerun()

comparaisonPatterns()