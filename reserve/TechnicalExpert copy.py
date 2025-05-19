import streamlit as st
st.set_page_config(
    page_icon=":busts_in_silhouette:",
    layout="wide"
)

import pandas as pd
import os, json
#from sympy import N
from utility.utils import *
from utility.topsis import *
from ontology.loadOntology import OntologyManager
from utility.patternManager import update_functional_patterns_with_variants

current_dir = os.path.dirname(__file__)
ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/TeX.css"))
patternVariantPath = os.getenv('PATTERN_VARIANTS')
PATTERN_VARIANTS = json.loads(patternVariantPath)
ontoManager = OntologyManager(ONTOLOGY_PATH)
ontoManager.loadOntology()

st.sidebar.markdown("""
<div style="
    background: #f0f5ff;
    border-radius: 10px;
    padding: 1.2rem;
    border-left: 4px solid #3a86ff;
    margin-bottom: 1.5rem;
">
<h4 style="color: #1a365d; margin-top: 0; font-weight: 600;">🔧 Core Responsibilities</h4>

<ul style="padding-left: 1.2rem; margin-bottom: 0.5rem;">
    <li style="margin-bottom: 0.7rem;">
        <strong style="color: #2c5282;">Validate</strong> generated Softgoal Maps for technical coherence
    </li>
    <li style="margin-bottom: 0.7rem;">
        <strong style="color: #2c5282;">Resolve trade-offs</strong> by prioritizing architectural patterns
    </li>
    <li style="margin-bottom: 0.7rem;">
        <strong style="color: #2c5282;">Escalate conflicts</strong> to Business Expert when needed (Bottom-up traceability)
    </li>
</ul>

<h4 style="color: #1a365d; margin: 1rem 0 0.5rem 0; font-weight: 600;">🔄 Final Validation Phase</h4>

<ul style="padding-left: 1.2rem; margin-bottom: 0;">
    <li style="margin-bottom: 0.5rem;">
        <strong style="color: #2c5282;">Quality-check</strong> final solution
    </li>
    <li>
        <strong style="color: #2c5282;">Enhance</strong> with MDCN-recommended Non-Functional Patterns
    </li>
</ul>
</div>
""", unsafe_allow_html=True)

def load_css(fichier):
    with open(fichier) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css(cssPaths)
pd.set_option('future.no_silent_downcasting', True)

if "selectedPatterns" not in st.session_state:
    st.session_state.selectedPatterns = {}
######### Module pour les recommandations basées sur les décisions #########
  ######### #########   ######### ######### ######### ######### #########
def findBestVariants(variants, decision):
    bestScore1, bestScore2 = -float('inf'), -float('inf')
    bestVariant1, bestVariant2 = None, None

    for variant in variants:
        scorePattern = st.session_state.matriceA_dict.get(variant, {})
        scoreVariantPattern = st.session_state.matriceB_dict.get(variant, {})

        if decision in scorePattern:
            orgScore = getScoreValue(scorePattern[decision])
            if orgScore > bestScore1:
                bestScore1 = orgScore
                bestVariant1 = variant

        if decision in scoreVariantPattern:
            varScore = getScoreValue(scoreVariantPattern[decision])
            if varScore > bestScore2:
                bestScore2 = varScore
                bestVariant2 = variant

    return bestVariant1, bestScore1, bestVariant2, bestScore2

def decisionWithVariants(bestVariant1, bestScore1, bestVariant2, bestScore2):
    recommendations = {}
    if bestScore1 > bestScore2:
        recommendations[bestVariant1] = {"recommendation": f"{bestVariant1}", "scores": st.session_state.matriceA_dict.get(bestVariant1, {})}
    elif bestScore2 > bestScore1:
        recommendations[bestVariant2] = {"recommendation": f"{bestVariant2}", "scores": st.session_state.matriceB_dict.get(bestVariant2, {})}
    return recommendations

def decisionWithOutVarianrts(pattern, decision, patternScore, variantpatternScore):
    recommendations = {}
    if decision in patternScore:
        original_score = getScoreValue(patternScore[decision])
        if original_score >= 1:
            recommendations[pattern] = {"recommendation": f"{pattern}", "scores": patternScore}

    if decision in variantpatternScore:
        variant_score = getScoreValue(variantpatternScore[decision])
        if variant_score >= 1:
            recommendations[pattern] = {"recommendation": f"{pattern}", "scores": variantpatternScore}

    if not recommendations.get(pattern):
        recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    return recommendations

def recommendationWithDecision(pattern, decision, patternScore, variantpatternScore):
    recommendations = {}
    bestScore1, bestScore2 = -float('inf'), -float('inf')
    bestVariant1, bestVariant2 = None, None

    if pattern in PATTERN_VARIANTS:
        variants = PATTERN_VARIANTS[pattern]
        bestVariant1, bestScore1, bestVariant2, bestScore2 = findBestVariants(variants, decision)

        recommendations = decisionWithVariants(bestVariant1, bestScore1, bestVariant2, bestScore2)
    else:
        recommendations = decisionWithOutVarianrts(pattern, decision, patternScore, variantpatternScore)

    st.session_state.selectedPatterns.update(recommendations)
   
    #st.session_state.selectedPatterns = recommendations
    #print("Recommendations with Decision:", st.session_state.selectedPatterns)
    return recommendations

######### Module pour les recommandations basées sur les préférences sans Decision #########
  ######### #########   ######### ######### ######### ######### #########

def checkPreferences(scores, softgoal_preferences):
    return all(
        (preference == 0 and getScoreValue(scores.get(softgoal, "")) >= 0) or
        (preference == 1 and getScoreValue(scores.get(softgoal, "")) >= 1)
        for softgoal, preference in softgoal_preferences.items()
    )

def noDecisionWithVariants(pattern, softgoal_preferences):
    recommendations = {}
    variants = PATTERN_VARIANTS[pattern]
    best_variant = None

    for variant in variants:
        scoresPat = st.session_state.matriceA_dict.get(variant, {})
        scoresVarPat = st.session_state.matriceB_dict.get(variant, {})

        isOKPattern = checkPreferences(scoresPat, softgoal_preferences)
        isOKPatternVariant = checkPreferences(scoresVarPat, softgoal_preferences)

        if isOKPattern or isOKPatternVariant:
            best_variant = variant
            break

    if isOKPattern:
        recommendations[pattern] = {"recommendation": f"{best_variant}_orgII", "scores": scoresPat}
    elif isOKPatternVariant:
        recommendations[pattern] = {"recommendation": f"{best_variant}_varII", "scores": scoresVarPat}
    else:
        recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    return recommendations

def noDecisionWithOutVariants(pattern, softgoal_preferences):
    recommendations = {}
    patternScore = st.session_state.matriceA_dict.get(pattern, {})
    variantpatternScore = st.session_state.matriceB_dict.get(pattern, {})

    original_valid = checkPreferences(patternScore, softgoal_preferences)
    variant_valid = checkPreferences(variantpatternScore, softgoal_preferences)

    if original_valid:
        recommendations[pattern] = {"recommendation": f"{pattern}", "scores": patternScore}
    elif variant_valid:
        recommendations[pattern] = {"recommendation": f"{pattern}", "scores": variantpatternScore}
    else:
        recommendations[pattern] = {"recommendation": "Aucune variante ne correspond aux préférences", "scores": {}}

    return recommendations

def recommendationWithOutDecision(pattern, softgoal_preferences):
    recommendations = {}
    if pattern in PATTERN_VARIANTS:
        recommendations = noDecisionWithVariants(pattern, softgoal_preferences)
    else:
        recommendations = noDecisionWithOutVariants(pattern, softgoal_preferences)
    
    st.session_state.selectedPatterns.update(recommendations)
    #st.session_state.selectedPatterns = recommendations
    #print("Recommendations without Decision:", st.session_state.selected_patterns_variants)
    return recommendations

######### Module pour les affichages de recommandations #########
  ######### #########   ######### ######### ######### ######### #########

def findTypeOfRecommendations(recommendations, softgoal_preferences):
    st.session_state.recommendations = recommendations
    matchRecommandations = {}
    NoMatchRecommandations = {}

    for pattern, data in recommendations.items():
        if data["recommendation"] == "Aucune variante ne correspond aux préférences":
            NoMatchRecommandations[pattern] = data
        else:
            matchRecommandations[pattern] = data

    if matchRecommandations:
        st.markdown("""
        <div class="match-recommendation">
            <div class="match-recommendation-title">Match Patterns</div>
            <div class="match-recommendation-subtitle">
                Patterns that closely match your input criteria
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        nb_items = len(matchRecommandations)
        if nb_items == 1: ## Matched Pattern = 1
            cols = st.columns(1)
            for (col, (pattern, data)) in zip(cols, matchRecommandations.items()):
                with col:
                    fpatterns = pattern.replace("_", " ")
                    with st.container(border=True):
                        scoresPat = st.session_state.matriceA_dict.get(pattern, {})
                        scoresVarPat = st.session_state.matriceB_dict.get(pattern, {})
                        sgmapX = mapStyles(scoresPat)
                        sgmapY = mapStyles(scoresVarPat)

                        st.markdown(f"""
                        <div class="pattern-container">
                            <span class="pattern-title">{fpatterns} </span>
                        </div>""", unsafe_allow_html=True)

                        mapdisplay = [generateMap(sgmapX, ""), generateMap(sgmapY, "")]
                        st.markdown("\n".join(mapdisplay), unsafe_allow_html=True)

                        for softgoal, score in data["scores"].items():
                            if softgoal in softgoal_preferences:
                                displayBar(f"{softgoal}", likertValue(score))
        else:
            cols = st.columns(2)
            for idx, (pattern, data) in enumerate(matchRecommandations.items()):
                with cols[idx % 2]:
                    fpatterns = pattern.replace("_", " ")
                    with st.container(border=True):
                        scoresPat = st.session_state.matriceA_dict.get(pattern, {})
                        scoresVarPat = st.session_state.matriceB_dict.get(pattern, {})
                        sgmapX = mapStyles(scoresPat)
                        sgmapY = mapStyles(scoresVarPat)

                        st.markdown(f"""
                        <div class="pattern-container">
                            <span class="pattern-title">{fpatterns} </span>
                        </div>""", unsafe_allow_html=True)

                        mapdisplay = [generateMap(sgmapX, ""), generateMap(sgmapY, "")]
                        st.markdown("\n".join(mapdisplay), unsafe_allow_html=True)

                        for softgoal, score in data["scores"].items():
                            if softgoal in softgoal_preferences:
                                displayBar(f"{softgoal}", likertValue(score))

    if matchRecommandations and NoMatchRecommandations:
        st.markdown("""
            <div style='display: flex; align-items: center; margin: 20px 0;'>
                <div style='flex-grow: 1; height: 1px; background-color: #ccc;'></div>
                <span style='margin: 0 10px; color: #4a8fe7; font-size: 20px;'>✦</span>
                <div style='flex-grow: 1; height: 1px; background-color: #ccc;'></div>
            </div>
            """, unsafe_allow_html=True)

    if NoMatchRecommandations:
        st.markdown(
            """
            <div class='decision-alert'>
                <div class='decision-title'>
                    You Need to Take Decision for These Patterns
                </div>
                <div class='decision-subtitle'>
                    Unsure about your decision?<br>
                    Click on the <span class='decision-highlight'>Domain Expert Decision</span> button
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        cols = st.columns(2)
        for i, (pattern, data) in enumerate(NoMatchRecommandations.items()):
            col = cols[i % 2]
            with col:
                fpatterns = pattern.replace("_", " ")

                with st.container(border=True):
                    st.markdown(f"""
                    <div class="pattern-container">
                        <span class="pattern-title">{fpatterns}</span>
                        <span class="pattern-message">No variant exactly matches your softgoal preferences</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if pattern in PATTERN_VARIANTS and PATTERN_VARIANTS[pattern]:
                        displayVariants(pattern, softgoal_preferences)
                    else:
                        displaySinglePattern(pattern, softgoal_preferences)

def displayVariants(pattern, softgoal_preferences):
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
                    displayBar(f"{softgoal}", likertValue(score))

            for softgoal, score in scores_B.items():
                if softgoal in softgoal_preferences:
                    displayBar(f"{softgoal}", likertValue(score))

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

def displaySinglePattern(pattern, softgoal_preferences):
    with st.container(border=True):
        scoresPat = st.session_state.matriceA_dict.get(pattern, {})
        sgmapX = mapStyles(scoresPat)
        mapdisplay = [generateMap(sgmapX, "")]
        st.markdown("\n".join(mapdisplay), unsafe_allow_html=True)

        for softgoal, score in scoresPat.items():
            if softgoal in softgoal_preferences:
                displayBar(f"{softgoal}", likertValue(score))

def PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences):
    recommendations = {}
    decision = st.session_state.get("decisions", {}).get(pattern, None)

    if decision:
        recommendations = recommendationWithDecision(pattern, decision, patternScore, variantpatternScore)
    else:
        recommendations = recommendationWithOutDecision(pattern, softgoal_preferences)

    return recommendations
    #findTypeOfRecommendations(recommendations, softgoal_preferences)

def displayAlternatives2(noFuncPatterns, softgoal_preferences):
    
    st.divider()  # Ligne de séparation au début
    st.markdown("### Non-Functional Patterns")
    st.markdown('''<span style="color: #FFA500; font-weight: bold;">The following patterns, if chosen, could potentially help improve your app design:</span>''', 
                unsafe_allow_html=True)
    st.divider()
    
    selectedSoftgoals = set(softgoal_preferences.keys())
    containers = [st.columns(2) for _ in range((len(noFuncPatterns) + 1) // 2)]
    containers = [col for row in containers for col in row]

    alternPattern = False 
    if "selected_alternatives" not in st.session_state:
        st.session_state.selected_alternatives = []

    data = []
    patternsToCompare = []

    for idx, pattern in enumerate(noFuncPatterns):
        scores = st.session_state.matriceA_dict.get(pattern, None)
        if scores is None:
            scores = st.session_state.matriceB_dict.get(pattern, None)
        if scores is None:
            continue

        iSoftgoals = [softgoal for softgoal in selectedSoftgoals if likertValue(scores.get(softgoal, "")) > 0]
        wSoftgoals = [softgoal for softgoal in selectedSoftgoals if likertValue(scores.get(softgoal, "")) < 0]

        if iSoftgoals:
            alternPattern = True
            patternsToCompare.append(pattern)
            row = [likertValue(scores.get(softgoal, 0)) for softgoal in selectedSoftgoals]
            data.append(row)

    if alternPattern:
        decisionMatrix = pd.DataFrame(data, index=patternsToCompare, columns=list(selectedSoftgoals))
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

        for idx, pattern in enumerate(patternsToCompare):
            scores = st.session_state.matriceA_dict.get(pattern, {})
            iSoftgoals = [softgoal for softgoal in selectedSoftgoals if likertValue(scores.get(softgoal, "")) > 0]
            wSoftgoals = [softgoal for softgoal in selectedSoftgoals if likertValue(scores.get(softgoal, "")) < 0]

            with containers[idx].container(border=True):
                st.write(f"#### {pattern}")
                st.success("**Improve:** " + ", ".join(iSoftgoals))
                if wSoftgoals:
                    st.error("**Worsen:** " + ", ".join(wSoftgoals))
                
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

    if st.button("Validate"):
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

def displayAlternatives(noFuncPatterns, softgoal_preferences):
    # Section Header with Professional Styling
    st.divider()
    st.markdown("## 🏗 Non-Functional Architecture Patterns")
    st.markdown("""
    <div style='color: #FF8C00; font-size: 14px; margin-bottom: 20px;'>
    The following design patterns could enhance your application's quality attributes when implemented:
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Initialize session state and variables
    selectedSoftgoals = set(softgoal_preferences.keys())
    if "selected_alternatives" not in st.session_state:
        st.session_state.selected_alternatives = []

    # Create responsive grid layout
    cols = st.columns(2)
    containers = []
    for i in range(len(noFuncPatterns)):
        containers.append(cols[i % 2].container(border=True))

    # Data processing
    patternsToCompare = []
    data = []
    alternPattern = False

    for idx, pattern in enumerate(noFuncPatterns):
        scores = st.session_state.matriceA_dict.get(pattern) or st.session_state.matriceB_dict.get(pattern)
        if not scores:
            continue

        iSoftgoals = [sg for sg in selectedSoftgoals if likertValue(scores.get(sg, "")) > 0]
        wSoftgoals = [sg for sg in selectedSoftgoals if likertValue(scores.get(sg, "")) < 0]

        if iSoftgoals:
            alternPattern = True
            patternsToCompare.append(pattern)
            data.append([likertValue(scores.get(sg, 0)) for sg in selectedSoftgoals])

    # Display patterns
    if alternPattern:
        try:
            # TOPSIS Calculation
            decisionMatrix = pd.DataFrame(data, index=patternsToCompare, columns=list(selectedSoftgoals))
            weights = calculate_weights(softgoal_preferences)
            criteria = {sg: "max" if pref == 1 else "min" for sg, pref in softgoal_preferences.items()}
            topsisScore = topsisAlgorithm(decisionMatrix, weights=list(weights.values()), criteria_directions=criteria)
        except Exception as e:
            st.error(f"Decision matrix error: {str(e)}")
            topsisScore = {}

        # Pattern Cards Display
        for idx, pattern in enumerate(patternsToCompare):
            scores = st.session_state.matriceA_dict.get(pattern, {})
            iSoftgoals = [sg for sg in selectedSoftgoals if likertValue(scores.get(sg, "")) > 0]
            wSoftgoals = [sg for sg in selectedSoftgoals if likertValue(scores.get(sg, "")) < 0]

            fpatterns = pattern.replace("_", " ")
            with containers[idx]:
                # Header with score badge
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"##### {fpatterns}")
                with col2:
                    if pattern in topsisScore:
                        st.markdown(f"""
                        <div style='
                            background: #4CAF50;
                            color: white;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            text-align: center;
                        '>
                        {topsisScore[pattern] * 100:.1f}%
                        </div>
                        """, unsafe_allow_html=True)
                
                # Benefits section
                with st.expander("**Quality Improvements**", expanded=True):
                    for sg in iSoftgoals:
                        st.success(f"✓ {sg}")
                
                # Trade-offs section
                if wSoftgoals:
                    with st.expander("**Potential Trade-offs**", expanded=False):
                        for sg in wSoftgoals:
                            st.error(f"⚠ {sg}")
                
                is_selected = st.checkbox(
                    "Select this pattern",
                    key=f"cb_{hash(pattern)}",
                    value=pattern in st.session_state.selected_alternatives,
                    help=f"Select {pattern} for implementation"
                )
                
                if is_selected:
                    if pattern not in st.session_state.selected_alternatives:
                        st.session_state.selected_alternatives.append(pattern)
                elif pattern in st.session_state.selected_alternatives:
                    st.session_state.selected_alternatives.remove(pattern)

    else:
        st.warning("""
        No alternative patterns found that satisfy your selected quality attributes.
        Consider adjusting your softgoal preferences.
        """)

    if st.button("✅ Validate Selection", type="primary", use_container_width=True):
        if not st.session_state.selected_alternatives:
            st.warning("Please select at least one pattern before validating")
            st.stop()
            
        functional_patterns = update_functional_patterns_with_variants(
            st.session_state.functional_patterns, 
            PATTERN_VARIANTS
        )
        
        # Update patterns
        st.session_state.functional_patterns = list(
            set(functional_patterns + st.session_state.selected_alternatives)
        )
        st.session_state.selected_alternatives = []
        st.session_state.non_functional_patterns = [
            p for p in st.session_state.non_functional_patterns
            if p not in st.session_state.functional_patterns
        ]
        
        st.success("Pattern selection updated successfully!")
        st.rerun()

def build_decision_matrix_for_topsis():
    selected_patterns_variants = st.session_state.get("selectedPatterns", {})
    st.session_state.selectedPatterns = {
        pattern: info for pattern, info in st.session_state.selectedPatterns.items()
        if info["recommendation"] != "Aucune variante ne correspond aux préférences"
    }
    selected_patterns_variants = st.session_state.selectedPatterns
    matrice_combined = {**st.session_state.matriceB_dict, **st.session_state.matriceA_dict}


    decision_matrix = []
    for pattern, variant_info in selected_patterns_variants.items():
        variant = variant_info["recommendation"]
        scores = matrice_combined.get(variant, {})
        
        #scores = st.session_state.matriceA_dict.get(variant, {})
        #if not scores:
        #    scores = st.session_state.matriceB_dict.get(variant, {})
        decision_matrix.append(scores)
    return decision_matrix

def comparaisonPatterns():
    load_css(cssPaths)    
    st.markdown("""
    <div class="technical-expert-title">⚙️ Technical Expert Configuration</div>
    """, unsafe_allow_html=True)
    if "current_pattern_index" not in st.session_state:
        st.session_state.current_pattern_index = 0

    patterns_to_compare = st.session_state.get("patterns_to_compare", [])

    if not patterns_to_compare:
        st.warning("Aucun pattern à comparer.")
        return

    softgoal_preferences = st.session_state.get("softpreferences", {})
    functional_patterns = st.session_state.get("functional_patterns", [])
    functional_patterns = update_functional_patterns_with_variants(functional_patterns, PATTERN_VARIANTS)

    recommendations = {}
    for pattern in functional_patterns:
        patternScore = st.session_state.matriceA_dict.get(pattern, {})
        variantpatternScore = st.session_state.matriceB_dict.get(pattern, {})
        pattern_recommendations = PatternRecommendations(pattern, patternScore, variantpatternScore, softgoal_preferences)

        if pattern_recommendations is not None:
            recommendations.update(pattern_recommendations)
    findTypeOfRecommendations(recommendations, softgoal_preferences)

    col3, col5 = st.columns([4, 2])

    with col3:
        if st.button("🧑‍💻 Domain Expert Decision"):
            patterns_to_decide = [pattern for pattern in patterns_to_compare]
            st.session_state.patterns_to_decide = patterns_to_decide
            st.session_state.step = "decide"
            st.switch_page("pages/DomainExpert.py")

    with col5:
        if st.button("Validate Confguration"):
            st.session_state.step = "final"
            build_decision_matrix_for_topsis()
            #print("Decision Matrix for TOPSIS:", decision_matrix)
            st.switch_page("pages/FinalConfiguration.py")

comparaisonPatterns()