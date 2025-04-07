import streamlit as st
import pandas as pd
from kbase.dbManager import DatabaseManager
from kbase import dbManager

def ExploreMatrixQuantification(dbManager):
    dbManager = DatabaseManager()

    st.title("Knolwedge Base Management")
    rel = dbManager.getAllUserScores()
    df_ontoRel = pd.DataFrame(rel, columns=["Pattern", "Softgoal", "Relation", "Reason", "Score"])
    tUserScores = df_ontoRel.pivot(index="Pattern", columns="Softgoal", values="Score")

    st.subheader("Influences quantification")
    if not tUserScores.empty:
        st.dataframe(tUserScores.style.map(style))
    else:
        st.warning("Aucune relation trouvée avec scores.")

def style(value):
    if value in ["Improves", ">= 1", "positive"] or (isinstance(value, (int, float)) and value >= 1):
        return "background-color: lightgreen; color: black;"
    elif value in ["Worsens", "<= -1"] or (isinstance(value, (int, float)) and value <= -1):
        return "background-color: lightcoral; color: black;"
    else:
        return ""