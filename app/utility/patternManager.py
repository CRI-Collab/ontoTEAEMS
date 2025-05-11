import streamlit as st
import os
import json
from utility.utils import getScoreValue

from dotenv import load_dotenv 
load_dotenv()
patternVariantPath = os.getenv('PATTERN_VARIANTS')
functPatterns = os.getenv('FUNCTIONAL_PATTERNS')
hybPatterns = os.getenv('HYBRID_PATTERNS')

PATTERN_VARIANTS = json.loads(patternVariantPath)
FUNCTIONAL_PATTERNS = json.loads(functPatterns)
HYBRID_PATTERNS = json.loads(hybPatterns)

def categorizePatterns(patterns):
    patternCategories = {"Functional": [], "Hybrid": []}
    for pattern in patterns:
        if pattern in FUNCTIONAL_PATTERNS:
            patternCategories["Functional"].append(pattern)
        elif pattern in HYBRID_PATTERNS:
            patternCategories["Hybrid"].append(pattern)
    return patternCategories

def checkSoftgoalPreferences(scores, softgoalChoice):
    for softgoal, expectedValue in softgoalChoice.items():
        score = scores.get(softgoal, None)
        value = getScoreValue(score) if score is not None else None

        if expectedValue == 0:  # Maintain → >= 0
            if value is None or value < 0:
                return False
        
        elif expectedValue == 1:  # Improves → > 0
            if value is None or value <= 0:
                return False
    return True

def getBestVariant(pattern, softgoalChoice):
    if pattern not in PATTERN_VARIANTS:
        return pattern

    variants = PATTERN_VARIANTS[pattern]
    bestVariant = None
    
    for variant in variants:
        scores_A = st.session_state.matriceA_dict.get(variant, {})
        scores_B = st.session_state.matriceB_dict.get(variant, {})

        isOKPattern = checkSoftgoalPreferences(scores_A, softgoalChoice)
        isOKVariant = checkSoftgoalPreferences(scores_B, softgoalChoice)

        if isOKPattern or isOKVariant:
            bestVariant = variant
            break 

    return bestVariant if bestVariant else pattern 

def update_functional_patterns_with_variants(functional_patterns, PATTERN_VARIANTS):
    updated_functional_patterns = []
    for pattern in functional_patterns:
        if pattern in PATTERN_VARIANTS:
            best_variant = getBestVariant(pattern, st.session_state.get("softpreferences", {}))
            if best_variant:
                updated_functional_patterns.append(best_variant)
            else:
                updated_functional_patterns.append(pattern)
        else:
            updated_functional_patterns.append(pattern)
    return updated_functional_patterns

def reclassifyHybridPatterns(patterns, softgoalChoice):
    funcPatterns = []
    noFuncPatterns = []

    for pattern in patterns:
        if pattern in HYBRID_PATTERNS:
            best_variant = getBestVariant(pattern, softgoalChoice)
            if best_variant:
                funcPatterns.append(best_variant)
            else:
                noFuncPatterns.append(pattern)
        
        elif pattern in FUNCTIONAL_PATTERNS:
            best_variant = getBestVariant(pattern, softgoalChoice)
            funcPatterns.append(best_variant)
            #funcPatterns.append(pattern)
        
        else:
            noFuncPatterns.append(pattern)

    return funcPatterns, noFuncPatterns