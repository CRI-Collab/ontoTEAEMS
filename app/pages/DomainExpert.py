import streamlit as st
import os, json
from dotenv import load_dotenv 
from kbase.dbManager import DatabaseManager
from patternManager import reclassifyHybridPatterns, update_functional_patterns_with_variants
from utils import mapStyles


load_dotenv()
patternVariantPath = os.getenv('PATTERN_VARIANTS')
PATTERN_VARIANTS = json.loads(patternVariantPath)

if 'dbManager' not in st.session_state:
    st.session_state.dbManager = DatabaseManager()
dbManager = st.session_state.dbManager

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
current_dir = os.path.dirname(__file__)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/DeX.css"))

def fetchSoftgoals(dbManager):
    return dbManager.getSoftgoalsByName()

def selectSoftgoals():
    st.sidebar.info(
    "As Domain Expert To Configure your application, you need to select one or more softgoals that you want to improves.\n\n"
    )
    load_css(cssPaths)
    st.markdown('<div class="domain-expert-title"> 🧑‍💻 Domain Expert Configuration 🧑‍💻</div>', 
                unsafe_allow_html=True)

    if "softpreferences" not in st.session_state:
        st.session_state.softpreferences = {}
    if "selectedSoftgoals" not in st.session_state:
        st.session_state.selectedSoftgoals = []

    softgoals = fetchSoftgoals(st.session_state.dbManager)
    st.markdown('''### :orange[Softgoals Selection] ''')

    
    with st.expander("ℹ️ What do 'Maintain' and 'Improves' mean?"):
        st.write("""
        - **Maintain**: No strong preference; patterns may keep, worsen, or improve the softgoal.  
        - **Improves**: Only patterns that *positively impact* the softgoal are desired.  
        """)

    # Use columns for better layout
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''### :orange[Maintain]''')
        st.caption("Neutral/Worsens/Improves allowed")
    with col2:
        st.markdown('''### :green[Improves]''')
        st.caption("Only improves allowed")
    
    selectedSoftgoals = st.multiselect(
        "Select softgoals", 
        options=softgoals,
        default=st.session_state.selectedSoftgoals,
        key="softgoal-selector",
        placeholder="Select at least one Softgoal", 
        label_visibility="hidden"
    )

    for softgoal in list(st.session_state.softpreferences.keys()):
        if softgoal not in selectedSoftgoals:
            del st.session_state.softpreferences[softgoal]
    
    st.session_state.selectedSoftgoals = selectedSoftgoals

    for softgoal in selectedSoftgoals:
        st.markdown(f"**{softgoal}**")
        option = st.radio(
            "C",
            options=["🔒Maintain"," --> Improves"],
            key=f"radio_{softgoal}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if option == "🔒Maintain":
            st.session_state.softpreferences[softgoal] = 0
        else:
            st.session_state.softpreferences[softgoal] = 1

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Map Solutions"):
            patterns_to_compare = st.session_state.get("patterns_to_compare", [])
            #print("Pattern To Compare", patterns_to_compare)

            if len(st.session_state.selectedSoftgoals) == 0:
                softgoalChoice = {softgoal: 1 if softgoal != "Cost" else -1
                    for softgoal in softgoals }
            else:
                softgoalChoice = st.session_state.get("softpreferences", {})
            
            softgoalChoice = {k: softgoalChoice[k] for k in sorted(softgoalChoice.keys())}
            
            functional_patterns, non_functional_patterns = reclassifyHybridPatterns(patterns_to_compare, softgoalChoice)
            
            st.session_state.functional_patterns = functional_patterns
            st.session_state.non_functional_patterns = non_functional_patterns
            st.session_state.step = "technicalExpert"
            st.switch_page("pages/TechnicalExpert.py")
            st.rerun()
    with col2:
        if st.button("Clear Softgoal Likert"):  
            st.session_state.softpreferences = {} 
            st.session_state.selectedSoftgoals = []
            st.rerun()

def updateFunctionalPatterns(funcPatterns, decisions, PATTERN_VARIANTS):
    updatedFunctionalPatterns = set() 

    for pattern in funcPatterns:
        if pattern in decisions:
            decision = decisions[pattern]
            
            if pattern in PATTERN_VARIANTS:
                variants = PATTERN_VARIANTS[pattern]
                # Filtrer les variants en fonction de la décision
                for variant in variants:
                    # Vérifier si le variant est compatible avec la décision
                    # (Vous devez adapter cette logique en fonction de votre cas d'utilisation)
                    if isDecisionFavorable(variant, decision):
                        updatedFunctionalPatterns.add(variant)

    return list(updatedFunctionalPatterns) 

def isDecisionFavorable(variant, decision):
    score_pattern = st.session_state.matriceA_dict.get(variant, {})
    score_variant = st.session_state.matriceB_dict.get(variant, {})
    if decision in score_pattern or decision in score_variant:
        return True
    return False

def decideSoftgoals():
    st.sidebar.info(
    "As Domain Expert, You need To give Preference of Softgoals To Guide the configuration."
    )
    load_css(cssPaths)
    st.markdown('<div class="domain-expert-title">Domain Expert Decision</div>', 
                unsafe_allow_html=True)
    
    patterns_to_decide = st.session_state.get("patterns_to_decide", [])
    functional_patterns = st.session_state.get("functional_patterns", [])
    functional_patterns_to_decide = [pattern for pattern in patterns_to_decide if pattern in functional_patterns]
   
    #####********** DEBUG **********#####
    #print("Functional Patterns To Decide", functional_patterns_to_decide)

    if not functional_patterns_to_decide:
        st.warning("Aucun pattern à trancher.")
        
        if st.button("Back To Patterns"):
            st.session_state.step = "calculate"
            st.switch_page("pages/TechnicalExpert.py")
            st.rerun()
        return

    selected_softgoals = st.session_state.get("selectedSoftgoals", [])
    if len(selected_softgoals) < 2:
        st.error("You need to choose minimum Two Softgoals.")
        return
    
    mode = st.radio(
        " ",
        options=[":orange[Do you want to decide alone [Nicolas]]?", ":green[Do you want guidance[Irina]]"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == ":orange[Do you want to decide alone [Nicolas]]?":
        st.markdown(f'''##### :gray[Choose Between:] :green[{" and ".join(selected_softgoals)}]''')
        decisions = {}
        decision = st.radio(
            f"c",
            options=selected_softgoals,
            horizontal=True,
            label_visibility="collapsed"
        )

        for pattern in functional_patterns_to_decide:
            decisions[pattern] = decision
        
        #### DECISION : VALIDE EXISTING DECISIONS ####
        if st.button("Valider choix"):
            #updatedFPatterns = update_functional_patterns_with_variants(st.session_state.functional_patterns, PATTERN_VARIANTS)
            #updatedFPatterns = updateFunctionalPatterns(functional_patterns_to_decide, decisions, PATTERN_VARIANTS)
            #st.session_state.functional_patterns = updatedFPatterns
            #rint("Functional Patterns UPDATED", updatedFPatterns)
            st.session_state.decisions = decisions
            st.session_state.step = "calculate"
            st.switch_page("pages/TechnicalExpert.py")
            st.rerun()

    elif mode == ":green[Do you want guidance[Irina]]":
        functional_patterns = st.session_state.get("functional_patterns", [])
        functional_patterns_to_decide = [pattern for pattern in patterns_to_decide if pattern in functional_patterns]

        st.markdown(f"### **Notice For Patterns** ")
        for pattern in functional_patterns_to_decide: 
            
            with st.container(border=True):
                fpattern = pattern.replace("_", " ")
                st.markdown(f"#### **{fpattern}**")

                if pattern in PATTERN_VARIANTS:
                    variants = PATTERN_VARIANTS[pattern]
                    st.markdown("##### :orange[Pattern variants] ")
                    col1, col2 = st.columns(2)
                    for i, variant in enumerate(variants):
                        current_col = col1 if i % 2 == 0 else col2
                        with current_col:
                            firstVariant = st.session_state.matriceA_dict.get(variant, {})
                            secondVariant = st.session_state.matriceB_dict.get(variant, {})
                            sgmap_variant_A = mapStyles(firstVariant)
                            sgmap_variant_B = mapStyles(secondVariant)

                            iVariantFirst = [sg for sg in sgmap_variant_A.get("improved", []) if sg not in selected_softgoals]
                            iVariantSecond = [sg for sg in sgmap_variant_B.get("improved", []) if sg not in selected_softgoals]
                            var = variant.replace("_", " ")
                            st.write(f"- **{var}**:  improves {', '.join(iVariantFirst)} {', '.join(iVariantSecond)}")
        if st.button("Add New Softgoals"):
            #st.session_state.decisions = decisions
            st.session_state.step = "domainExpert"
            st.switch_page("pages/DomainExpert.py")
            st.rerun()

if 'step' not in st.session_state:
    st.session_state.step = "domainExpert"

if st.session_state.step == "domainExpert":
    selectSoftgoals()

elif st.session_state.step == "decide":
    decideSoftgoals()
