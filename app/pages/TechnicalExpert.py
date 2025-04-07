from requests import session
import streamlit as st
import pandas as pd
import os, json
from utils import *
from topsis import *
from ontology.loadOntology import OntologyManager
from patternManager import update_functional_patterns_with_variants

import streamlit as st

# Style CSS pour le sidebar
st.markdown("""
    <style>
    .sidebar-title {
        font-size: 32px;
        font-weight: bold;
        color: #2e86de;
        margin-bottom: 20px;
    }
    .sidebar-text {
        font-size: 16px;
        color: #333;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
 
# Contenu du sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-title">Technical Expert </div>', unsafe_allow_html=True)
    st.sidebar.info(
    "As Technical Expert , you need to VALDIATE one or more configuration.\n\n"
 )

current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/TeX.css"))
patternVariantPath = os.getenv('PATTERN_VARIANTS')

PATTERN_VARIANTS = json.loads(patternVariantPath)
ontoManager = OntologyManager(ONTOLOGY_PATH)
ontoManager.loadOntology()

def load_css(fichier):
    with open(fichier) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css(cssPaths)
pd.set_option('future.no_silent_downcasting', True)


def PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences):
    recommendations = {}
    decision = st.session_state.get("decisions", {}).get(pattern, None)   

    ######### TEST DECISION POUR VARIANT DES PATTERNS
    if decision:
        bestScore1 = -float('inf')
        bestScore2 = -float('inf')
        
        bestVariant1 = None
        bestVariant2 = None

        if pattern in PATTERN_VARIANTS:
            variants = PATTERN_VARIANTS[pattern]

            for variant in variants:
                scorePattern = st.session_state.matriceA_dict.get(variant, {})
                scoreVariantPattern = st.session_state.matriceB_dict.get(variant, {})

                if decision in scorePattern:
                    orgScore = getScoreValue(scorePattern[decision])
                    if orgScore > bestScore1:
                        bestScore1 = orgScore 
                        bestVariant1 = variant 
                    #if orgScore >= 1:
                        #recommendations[variant] = {"recommendation": f"{variant}", "scores": scorePattern}

                if decision in scoreVariantPattern:
                    varScore = getScoreValue(scoreVariantPattern[decision])
                    if varScore > bestScore2:
                        bestScore2 = varScore
                        bestVariant2 = variant
        
            if bestScore1 > bestScore2:
                recommendations[bestVariant1] = {"recommendation": f"{bestVariant1}", "scores": st.session_state.matriceA_dict.get(bestVariant1, {})}
                #print("recommandationA", recommendations[bestVariant1])
            
            elif bestScore2 > bestScore1:
                recommendations[bestVariant2] = {"recommendation": f"{bestVariant2}", "scores": st.session_state.matriceB_dict.get(bestVariant2, {})}
                #print("recommandationB", recommendations[bestVariant2])
                        
            ## TO DO FOR NEXT MEETING
        ###A TRAITE LE CAS OU DEUX VARIANTS SONT POSITIFS (RENVOYER LE MEILLEUR) - FAIT

            
        ######### TEST DECISION POUR DES PATTERNS SANS VARIANTS
        else:
            if decision in patternScore:
                original_score = getScoreValue(patternScore[decision])
                if original_score >= 1:
                    recommendations[pattern] = {"recommendation": f"{pattern}_org", "scores": patternScore}
            
            if decision in variantpatternScore:
                variant_score = getScoreValue(variantpatternScore[decision])
                if variant_score >= 1:
                    recommendations[pattern] = {"recommendation": f"{pattern}_var", "scores": variantpatternScore}
            
            if not recommendations.get(pattern):
                recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}
    
    ######### FIN TEST POUR DECISION PRIS PAR LE DOMAIN EXPERT *****
    else :  
        if pattern in PATTERN_VARIANTS:
            variants = PATTERN_VARIANTS[pattern]
            best_variant = None

            for variant in variants:
                scoresPat = st.session_state.matriceA_dict.get(variant, {})
                scoresVarPat = st.session_state.matriceB_dict.get(variant, {})
              
                isOKPattern = all(
                    (preference == 0 and getScoreValue(scoresPat.get(softgoal, "")) >= 0) or
                    (preference == 1 and getScoreValue(scoresPat.get(softgoal, "")) >= 1)
                    for softgoal, preference in softgoal_preferences.items()
                )
                isOKPatternVariant = all(
                    (preference == 0 and getScoreValue(scoresVarPat.get(softgoal, "")) >= 0) or
                    (preference == 1 and getScoreValue(scoresVarPat.get(softgoal, "")) >= 1)
                    for softgoal, preference in softgoal_preferences.items()
                )

                if isOKPattern or isOKPatternVariant:
                    best_variant = variant
                    break

                if isOKPattern:
                    recommendations[pattern] = {"recommendation": f"{best_variant}_orgII", "scores": scoresPat}
                elif isOKPatternVariant:
                    recommendations[pattern] = {"recommendation": f"{best_variant}_varII", "scores": scoresVarPat}
                else:
                    recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}
        else:       
            original_valid = all(
                (preference == 0 and getScoreValue(patternScore.get(softgoal, "")) >= 0) or
                (preference == 1 and getScoreValue(patternScore.get(softgoal, "")) >= 1)
                for softgoal, preference in softgoal_preferences.items()
            )

            variant_valid = all(
                (preference == 0 and getScoreValue(variantpatternScore.get(softgoal, "")) >= 0) or
                (preference == 1 and getScoreValue(variantpatternScore.get(softgoal, "")) >= 1)
                for softgoal, preference in softgoal_preferences.items()
            )

            if original_valid:
                recommendations[pattern] = {"recommendation": f"{pattern}_org", "scores": patternScore}
            elif variant_valid:
                recommendations[pattern] = {"recommendation": f"{pattern}_var", "scores": variantpatternScore}
            else:
                recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    st.session_state.recommendations = recommendations

    ### TO TEST
    #updated_functional_patterns = set(st.session_state.get("functional_patterns", []))
    #print("updated_functional_patterns1", updated_functional_patterns)

    #for pattern, data in recommendations.items():
    #    if pattern in PATTERN_VARIANTS:
    #        variants = PATTERN_VARIANTS[pattern]
            # Ajouter les variants recommandés
    #        for variant in variants:
    #            if variant in recommendations:
    #                updated_functional_patterns.add(variant)
    #    else:
            # Ajouter le pattern s'il n'a pas de variants
    #        updated_functional_patterns.add(pattern)

    # Mettre à jour les functional patterns dans st.session_state
    #st.session_state.functional_patterns = list(updated_functional_patterns)
    #print("updated_functional_patterns", updated_functional_patterns)

    #### C'EST ICI QUE LES VARIANTS DOIT ÊTRE PROPOSÉ A LA PLACE DU PATTERN
    for pattern, data in recommendations.items():
        if pattern in PATTERN_VARIANTS:
            variants = PATTERN_VARIANTS[pattern]  
        fpatterns = pattern.replace("_", " ")

        if data["recommendation"] == "Aucune variante ne correspond aux préférences":
            with st.container(border=True):
                st.markdown(f"""
                <div class="pattern-container">
                    <span class="pattern-title">{fpatterns}</span>
                    <span class="pattern-message">No variant exactly matches your softgoal preferences</span>
                </div>
                """, unsafe_allow_html=True)

                if pattern in PATTERN_VARIANTS and PATTERN_VARIANTS[pattern]:
                    variants = PATTERN_VARIANTS[pattern]
                    col1, col2 = st.columns(2)
                    for i, variant in enumerate(variants):
                        current_col = col1 if i % 2 == 0 else col2
                        with current_col:
                            scores_A = st.session_state.matriceA_dict.get(variant, {})
                            scores_B = st.session_state.matriceB_dict.get(variant, {})
                            sgmap2 = mapStyles(scores_A)
                            sgmap3 = mapStyles(scores_B)
                            content = [generateMap(sgmap2, ""), generateMap(sgmap3, "")]
                            st.markdown("\n".join(content), unsafe_allow_html=True)

                            for softgoal, score in scores_A.items():
                                if softgoal in softgoal_preferences:
                                    displayBar(
                                        f"{softgoal}", 
                                        likertValue(score),
                                    )

                            for softgoal, score in scores_B.items():
                                if softgoal in softgoal_preferences:
                                    displayBar(
                                        f"{softgoal}", 
                                        likertValue(score),
                                    )

                            def update_choice3(chosen_variant, type):
                                for variant in variants:
                                    key = f"choix_variant_{variant}"     
                                    st.session_state[key] = (variant == chosen_variant)
                                    
                            vari = variant.replace("_", " ")
                            st.checkbox(
                                f"{vari}",
                                key=f"choix_variant_{variant}",
                                value=st.session_state.get(f"choix_variant_{variant}"),
                                on_change=update_choice3,
                                args=(variant, "variant"),
                            )
                else:
                    with st.container(border=True):
                        scoresPat = st.session_state.matriceA_dict.get(pattern, {})
                        sgmapX = mapStyles(scoresPat)    
                        mapdisplay = [generateMap(sgmapX, "")]
                        st.markdown("\n".join(mapdisplay), unsafe_allow_html=True)

                        for softgoal, score in scoresPat.items():
                            if softgoal in softgoal_preferences:
                                displayBar( f"{softgoal}", likertValue(score))
                
        ### S'IL RETROUVE LA VALEUR DANS AU MOINS UN DES VARIANTS ******* 
        else:
            with st.container(border=True):
                scoresPat = st.session_state.matriceA_dict.get(pattern, {})
                scoresVarPat = st.session_state.matriceB_dict.get(pattern, {})
                sgmapX = mapStyles(scoresPat)
                sgmapY = mapStyles(scoresVarPat)
                
                st.markdown(f"""
                <div class="pattern-container">
                    <span class="pattern-title">{fpatterns} </span>
                </div>  """, unsafe_allow_html=True)

                mapdisplay = [generateMap(sgmapX, ""), generateMap(sgmapY, "")]
                st.markdown("\n".join(mapdisplay), unsafe_allow_html=True)

                for softgoal, score in data["scores"].items():
                    if softgoal in softgoal_preferences:
                        displayBar( f"{softgoal}", likertValue(score))

def displayFunctionalPatterns(functional_patterns, softgoal_preferences):
    st.markdown("""
        <div style="background-color: #f9f9f9; border-left: 6px solid #ffcc00; padding: 15px; border-radius: 5px;">
            <h3 style="color: green;">🛠️ Required Configuration</h3>
            <p style="color: #555; font-size: 1.1em;">
                Pour configurer votre application, vous avez besoin des <strong>Functional Patterns</strong> suivants :
            </p>
        </div>
    """, unsafe_allow_html=True)
    with st.expander("ℹ️ What you need to know for each button?", expanded=True):
        st.write("""
        - **Check the box**: patterns will be included in your solution  
        - **Contradictory patterns?**: Click → :orange[Domain Expert Decision] to refine preferences (Example: One pattern improves security, another worsens it).
        - **Wrong softgoals?**: Click → :orange[Softgoals Refinement] to modify your initial choices
        """)
    
    # Mettre à jour functional_patterns avec les variants
    #functional_patterns = update_functional_patterns_with_variants(functional_patterns, PATTERN_VARIANTS)

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
    st.markdown("### Non Functional Patterns")
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
            for softgoal, preference in softgoal_preferences.items()
        }

        try:
            topsisScore = topsisAlgorithm(decisionMatrix, weights=list(weights.values()), criteria_directions=criteria)
        except Exception as e:
            st.error(f"Erreur lors de l'application de TOPSIS: {e}")
            topsisScore = {}

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
        # Mettre à jour functional_patterns avec les variants
        functional_patterns = update_functional_patterns_with_variants(st.session_state.functional_patterns, PATTERN_VARIANTS)
        
        for pattern in st.session_state.selected_alternatives:
            if pattern not in functional_patterns:
                functional_patterns.append(pattern)
        
        st.session_state.functional_patterns = functional_patterns
        st.session_state.selected_alternatives = []
 
        st.session_state.non_functional_patterns = [
            pattern for pattern in st.session_state.non_functional_patterns
            if pattern not in functional_patterns ]

        st.rerun()

st.cache_data.clear()
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
    functional_patterns = update_functional_patterns_with_variants(functional_patterns, PATTERN_VARIANTS)
    
    displayFunctionalPatterns(functional_patterns, softgoal_preferences)
    #print("functionnal Patterns", functional_patterns)
    
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
            #st.rerun()

    with col3:
        if st.button("🧑‍💻 Domain Expert Decision"):
            #patterns_to_decide = [pattern for pattern in patterns_to_compare if st.session_state.get(f"choix_none_{pattern}", False)]
            patterns_to_decide = [pattern for pattern in patterns_to_compare]
            st.session_state.patterns_to_decide = patterns_to_decide
            st.session_state.step = "decide"
            st.switch_page("pages/DomainExpert.py")
            #st.rerun()

    with col5:
        if st.button("Validate Confguration"):
            st.session_state.step = "final"
            st.switch_page("pages/teaem.py")
            #st.session_state.show_alternatives = False
            #st.rerun()

comparaisonPatterns()