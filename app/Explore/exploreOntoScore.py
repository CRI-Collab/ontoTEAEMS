import streamlit as st
from kbase.dbManager import DatabaseManager

def ExploreWithScore(dbManager):
    dbManager = DatabaseManager()
    st.title("Ontology Management")

    patterns = dbManager.getAllPatterns()
    pattern_names = [pattern[0] for pattern in patterns]

    selected_pattern = st.selectbox("Select Pattern", pattern_names)

    if selected_pattern:
        st.subheader(f"Informations pour : {selected_pattern}")
        userScores = dbManager.getScoresForPattern(selected_pattern)

        st.subheader("Relations et Scores")
        if userScores:
            data = [{"Pattern": us[0], "Relation": us[2], "Softgoal": us[1], "Score": us[4]} 
                    for us in userScores]
            st.table(data)
        else:
            st.warning("No relation found.")