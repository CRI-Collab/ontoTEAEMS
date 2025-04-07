from matplotlib.colorbar import ColorbarBase
import streamlit as st
import pandas as pd
import numpy as np
import os
from utils import *
from topsis import *
from ontology.loadOntology import OntologyManager

def PatternRecommendationsss(pattern, patternScore, variantpatternScore, softgoal_preferences):
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
    else:
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

                #st.error("No variant exactly matches your softgoal preferences..")
                st.markdown(f"""<p style="color: gray;">
                        Improved Softgoals : {", ".join(sgmap0["improved"])} </p>
                        <p style="color: gray;">  Harmed Softgoals : {", ".join(sgmap0["harmed"])} </p> """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
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