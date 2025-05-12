import streamlit as st
st.set_page_config(
    page_icon=":busts_in_silhouette:",
    layout="wide"
)

import os, json
import pandas as pd
from itertools import combinations
from dotenv import load_dotenv 
from kbase.dbManager import DatabaseManager
from utility.patternManager import reclassifyHybridPatterns

load_dotenv()
patternVariantPath = os.getenv('PATTERN_VARIANTS')
PATTERN_VARIANTS = json.loads(patternVariantPath)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
current_dir = os.path.dirname(__file__)
cssPaths = os.path.normpath(os.path.join(current_dir, "../css/DeX.css"))
cssPaths2 = os.path.normpath(os.path.join(current_dir, "../css/DexX.css"))

def load_patterns():
    df1 = pd.read_csv(os.path.normpath(os.path.join(current_dir, "../data/XXuPatterns.csv")))
    df2 = pd.read_csv(os.path.normpath(os.path.join(current_dir, "../data/XXuPatterns2.csv")))
    return pd.concat([df1, df2]).drop_duplicates()

if 'dbManager' not in st.session_state:
    st.session_state.dbManager = DatabaseManager()
dbManager = st.session_state.dbManager

patterns_to_compare = st.session_state.get("patterns_to_compare", [])

if 'allpatterns' not in st.session_state:
    st.session_state.allpatterns = load_patterns()

def fetchSoftgoals(dbManager):
    return dbManager.getSoftgoalsByName()

def showsideBar():
    with st.sidebar:
        st.markdown("""
        ### 🧑‍💼 Business Expert Guide
        **Your Role**: Select softgoals and assign their priorities.
        
        For each criterion:
        - ◎ **Best Effort**: Try to improve, if faill, take the rest (default)
        - ▶ **Improve**: Enhance this aspect
                    
        **Conflict Analysis**:
        When conflicts appear, they reveal implicit softgoals trade-offs that need explicit decisions later.
        """)

def showBar2():
    st.sidebar.title("👔 Business Expert Role")
    st.sidebar.markdown("""
    <div style="
        background: #fff0f3;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 4px solid #e63946;
        margin-bottom: 1.5rem;
    ">
    <h4 style="color: #5c0011; margin-top: 0; font-weight: 600;">🎯 Strategic Priorities</h4>

    <ul style="padding-left: 1.2rem; margin-bottom: 0.5rem;">
        <li style="margin-bottom: 0.7rem;">
            <strong style="color: #9d0208;">Define</strong> softgoals and assign priority weights
        </li>
        <li style="margin-bottom: 0.7rem;">
            <strong style="color: #9d0208;">Validate</strong> initial architecture direction
        </li>
        <li style="margin-bottom: 0.7rem;">
            <strong style="color: #9d0208;">Make final calls</strong> on conflicting priorities (Top-down governance)
        </li>
    </ul>

    <h4 style="color: #5c0011; margin: 1rem 0 0.5rem 0; font-weight: 600;">✅ Final Approval</h4>

    <ul style="padding-left: 1.2rem; margin-bottom: 0;">
        <li style="margin-bottom: 0.5rem;">
            <strong style="color: #9d0208;">Approve</strong> final validation for softgals priorities
        </li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def matchSoftgoal(softpreferences, allpatterns):
    #priorities = {k: v for k, v in softpreferences.items() if v != 0}
    priorities = {k: v for k, v in softpreferences.items() if v in [0, 1]}
    if not priorities:
        return None, None
    
    countMatch = []
    for _, row in allpatterns.iterrows():
        pattern = row['Design Patterns']
        match = True
        
        for softgoal, priority in priorities.items():
            if softgoal not in row:
                continue
                
            value = row[softgoal]
            if priority == 1 and value not in ['++', '+']: #Improves
                match = False
                break
            elif priority == 0 and value not in ['--', '-', '']: #Worsens, neutral, Best effort
                match = False
                break
        if match:
            countMatch.append(pattern)
    return countMatch

def conflictsSoftgoal(softpreferences, allpatterns):
    priorities = {k: v for k, v in softpreferences.items() if v in [0, 1]}
    #priorities = {k: v for k, v in softpreferences.items() if v != 0}
    if not priorities:
        return None, None
    softgoalsConflict = {}
    softgoals = list(priorities.keys())
    
    for i in range(len(softgoals)):
        for j in range(i+1, len(softgoals)):
            sg1, sg2 = softgoals[i], softgoals[j]
            conflictPatterns = []

            for _, row in allpatterns.iterrows():
                patternData = row['Design Patterns']

                if sg1 in row and sg2 in row:
                    valSg1, valSg2 = row[sg1], row[sg2]
                    # Detect strong conflicts (++ vs --)
                    if (valSg1 in ['++', '+'] and valSg2 == '--') or (valSg1 == '--' and valSg2 in ['++', '+']):
                        conflictPatterns.append({
                            'pattern': patternData,
                            'values': {sg1: valSg1, sg2: valSg2}
                        })
            if conflictPatterns:
                softgoalsConflict[(sg1, sg2)] = {
                    'patterns': conflictPatterns,
                    'priority_sg1': priorities[sg1],
                    'priority_sg2': priorities[sg2]
                }
    
    return softgoalsConflict

def showTradeOffNFRs(sg1, sg2, conflictData):
    st.warning(f"⚠️ Softgoals Trade-offs Detected: {sg1} vs {sg2}")
    with st.expander("🔍 Softgoals Trade-offs Analysis "):
        st.markdown(f"""
        **{sg1}** (Priority: {'High' if conflictData['priority_sg1'] == 1 else 'Low'}) 
        vs 
        **{sg2}** (Priority: {'High' if conflictData['priority_sg2'] == 1 else 'Low'})
        
        This tension reveals an implicit architectural decision about which non-functional 
        requirement should take precedence in your system.
        """)
        MAX_CONFLICT_PATTERNS_TO_SHOW = 1
        for item in conflictData['patterns'][:MAX_CONFLICT_PATTERNS_TO_SHOW]:
            sg1_impact = "improves" if item['values'][sg1] in ['++', '+'] else "worsens"
            sg2_impact = "improves" if item['values'][sg2] in ['++', '+'] else "worsens"

            st.markdown(f"""
            - For Example, Pattern **{item['pattern']}**:  
            ➤ {sg1_impact} **{sg1}** , but {sg2_impact} **{sg2}**
            """)

        if len(conflictData['patterns']) > MAX_CONFLICT_PATTERNS_TO_SHOW:
            remaining = len(conflictData['patterns']) - MAX_CONFLICT_PATTERNS_TO_SHOW
            st.caption(f"*+ {remaining} other patterns showing this conflict...*")
        
        st.markdown("""
        #### Architectural Decision Required:
        Please explicitly choose which quality attribute should be prioritized:
        """)

def selectSoftgoals():
    showsideBar()
    load_css(cssPaths)
    st.markdown('<div class="domain-expert-title"> 🧑‍💻 Domain Expert Configuration 🧑‍💻</div>', 
                unsafe_allow_html=True)
    
    if "selectedSoftgoals" not in st.session_state:
        st.session_state.selectedSoftgoals = [] 
    if "softpreferences" not in st.session_state:
        st.session_state.softpreferences = {}
    softgoals = fetchSoftgoals(st.session_state.dbManager)

    def OptimizationRetour():
        #priorities = {k: v for k, v in st.session_state.softpreferences.items() if v != 0}
        priorities = {k: v for k, v in st.session_state.softpreferences.items() if v in [0, 1]}
        if priorities:
            countMatch  = matchSoftgoal(st.session_state.softpreferences, st.session_state.allpatterns)
            softgoalsConflict = conflictsSoftgoal(st.session_state.softpreferences, st.session_state.allpatterns)
            col1, col2 = st.columns([1, 3])
            with col1:
                if countMatch:
                    total_patterns = len(st.session_state.allpatterns)/2 + 0.5
                    matched_count = len(countMatch)
                    percentage = (matched_count / total_patterns) * 100

                    if percentage > 60:
                        color = "green"
                    elif percentage > 40:
                        color = "orange"
                    else:
                        color = "red"

                    progress_value = min(max(matched_count / total_patterns, 0.0), 1.0)
                    st.progress(progress_value, f"Percentage: {percentage:.1f}%")
                    st.markdown(f"<span style='color:{color}'>🎯 Matching patterns: {matched_count}/{total_patterns} patterns</span>", 
                        unsafe_allow_html=True)
                    #with st.expander("View matching patterns"):
                    #    for pattern in countMatch:
                    #        st.write(f"- {pattern}")
                else:
                    st.warning("No patterns satisfy the current criteria. You may need to adjust constraints (Best Effort).")
        
            with col2:
                if softgoalsConflict:
                    for (sg1, sg2), conflictdata in softgoalsConflict.items():
                        showTradeOffNFRs(sg1, sg2, conflictdata)
    #####  #####  ##### ##### ##### ##### ##### #####
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### Business Preferences Configuration")
    with col2:
        OptimizationRetour()
    st.markdown("***")  

    #### BODY : SELECTION PREFERENCES OF SOFGTGOALS
    for softgoal in softgoals:
        if softgoal not in st.session_state.softpreferences:
            st.session_state.softpreferences[softgoal] = None

        current_value = st.session_state.softpreferences[softgoal]  
        colss = st.columns([1, 2, 2])

        with colss[0]:
            st.markdown(f"""
            <div class="preference-box">
                <div class="preference-title">{softgoal}</div>
            </div>
            """, unsafe_allow_html=True)

        with colss[1]:
            besteffort = "◎ Best Effort" if current_value != 0 else "✓ Best Effort"
            if st.button(besteffort, key=f"best_{softgoal}", help="Try to improve, if fail, take the rest"):
                st.session_state.softpreferences[softgoal] = 0 if current_value != 0 else None
                st.rerun()

        with colss[2]:
            improveLabel = "▶ Improve" if current_value != 1 else "✓ Improve"
            if st.button(improveLabel, key=f"improve_{softgoal}", help="Force improve this aspect"):
                st.session_state.softpreferences[softgoal] = 1 if current_value != 1 else None
                st.rerun()

    st.session_state.selectedSoftgoals = [
        sg for sg in softgoals 
        if st.session_state.softpreferences.get(sg) in [0, 1]
    ]
    st.markdown("***")

    ##### BUTTON
    cols = st.columns([1, 1, 1])
    with cols[0]:
        if st.button("🔄 Reset all", help="Reset all preferences to neutral"):
            st.session_state.softpreferences = {sg: None for sg in softgoals}
            st.rerun()

    with cols[2]:
        countMatch  = matchSoftgoal(st.session_state.softpreferences, st.session_state.allpatterns)
        disabled_state = not any(v in [0, 1] for v in st.session_state.softpreferences.values()) or not countMatch
        tooltip = ""
        if not any(v in [0, 1] for v in st.session_state.softpreferences.values()):
            tooltip = "Please select at least one softgoal preference"
        elif not countMatch:
            tooltip = "No patterns match your current criteria"

        if st.button("Generate Softgoal Maps", type="primary", use_container_width=True, 
                     disabled=disabled_state, help=tooltip):
            #if any(v in [0, 1] for v in st.session_state.softpreferences.values()):
            selected = {k: v for k, v in st.session_state.softpreferences.items() if v in [0, 1]}

            if selected:
                st.success("Preferences saved!")
                st.session_state.softpreferences = selected
                softgoalChoice = {k: v for k, v in st.session_state.softpreferences.items() 
                             if v in [0, 1]}
                
                functional_patterns, non_functional_patterns = reclassifyHybridPatterns(patterns_to_compare, softgoalChoice)
                
                st.session_state.functional_patterns = functional_patterns
                st.session_state.non_functional_patterns = non_functional_patterns
                st.session_state.step = "technicalExpert"
                st.switch_page("pages/TechnicalExpert.py")
            else:
                st.warning("Please set at least one preference")

def updateFunctionalPatterns(funcPatterns, decisions, PATTERN_VARIANTS):
    updatedFunctionalPatterns = set() 

    for pattern in funcPatterns:
        if pattern in decisions:
            decision = decisions[pattern]
            
            if pattern in PATTERN_VARIANTS:
                variants = PATTERN_VARIANTS[pattern]
                for variant in variants:
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
    load_css(cssPaths2)
    showBar2()
    
    st.markdown("""
    <div class='decision-header'>
        <div class='title'>Conflict Resolution Panel</div>
        <div class='subtitle'>Business User Decision Required</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='alert alert-info'>
        <b>Technical experts encounter difficulties</b> validating the configuration due to 
        <b>softgoal conflicts</b>. As a <b>Business User</b>, your role is to prioritize 
        between competing softgoals.
    </div>
    """, unsafe_allow_html=True)
    
    patterns_to_decide = st.session_state.get("patterns_to_decide", [])
    functional_patterns = st.session_state.get("functional_patterns", [])
    functional_patterns_to_decide = [p for p in patterns_to_decide if p in functional_patterns]
    selected_softgoals = st.session_state.get("selectedSoftgoals", [])

    if not functional_patterns_to_decide:
        st.markdown("""
        <div class='decision-card'>
            <h3>🔍 No Clear Patterns Found</h3>
            <p>The system couldn't identify clear patterns requiring your decision.</p>
            <div class='options'>
                <p>Possible actions:</p>
                <ol>
                    <li>Adjust your initial filters</li>
                    <li>Consult with technical experts</li>
                    <li>Review your softgoal selection</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Pattern Analysis", use_container_width=True):
            st.session_state.step = "calculate"
            st.switch_page("pages/TechnicalExpert.py")
        return
    
    if len(selected_softgoals) < 2:
        st.error("""
        ❗ Decision requires at least **two softgoals** in conflict.  
        Please select more softgoals to proceed.
        """)
        return

    st.markdown(f"""
    <div class='decision-card'>
        <h3>⚖️ Priority Decision Required</h3>
        <p>Please determine which softgoal should take precedence:</p>
        <div class='conflict-display'>
            <span class='vs-badge'>VS</span>
            <div class='softgoal-options'>
                <div class='softgoal-pill'>{selected_softgoals[0]}</div>
                <div class='softgoal-pill'>{selected_softgoals[1]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    decision = st.radio(
        "Select your preferred softgoal:",
        options=selected_softgoals,
        horizontal=True,
        index=None,
        label_visibility="visible",
        key="softgoal_decision"
    )

    if decision:
        decisions = {pattern: decision for pattern in functional_patterns_to_decide}
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = "calculate"
                st.switch_page("pages/TechnicalExpert.py")
                
        with col2:
            if st.button("✅ Validate Decision", 
                        type="primary", 
                        use_container_width=True,
                        disabled=not decision):
                st.session_state.decisions = decisions
                st.session_state.step = "calculate"
                st.switch_page("pages/TechnicalExpert.py")
                st.rerun()

if 'step' not in st.session_state:
    st.session_state.step = "domainExpert"

if st.session_state.step == "domainExpert":
    selectSoftgoals()

elif st.session_state.step == "decide":
    decideSoftgoals()