from ast import Not
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import streamlit as st
import os
from ontology.loadOntology import OntologyManager

current_dir = os.path.dirname(__file__)
#ONTOLOGY_PATH = os.path.join(current_dir, "./ontology/TestMine.owl")
#ontoManager = OntologyManager(ONTOLOGY_PATH)

css_path = os.path.join(current_dir, "./css/styles.css")
if os.path.exists(css_path):
    with open(css_path, "r") as file:
        css = file.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def fetchRelations(dbManager):
    relations = dbManager.topsisScore()
    return pd.DataFrame(relations, columns=["Pattern", "Softgoal", "Score"])

def topsisMatrix(scores):
    patterns = scores['Pattern'].unique()
    softgoals = scores['Softgoal'].unique()
    decisionMatrix = pd.DataFrame(0, index=patterns, columns=softgoals)
    for _, row in scores.iterrows():
        decisionMatrix.loc[row['Pattern'], row['Softgoal']] = row['Score']
    return decisionMatrix

def calculate_weightsBack(softgoal_preferences):
    exp_values = np.exp([pref * 3 for pref in softgoal_preferences.values()])
    weights = exp_values / np.sum(exp_values)
    return dict(zip(softgoal_preferences.keys(), weights))

def calculate_weights(softgoal_preferences):
    exp_values = np.exp(list(softgoal_preferences.values()))
    weights = exp_values / np.sum(exp_values) 
    return dict(zip(softgoal_preferences.keys(), weights))

def topsisAlgorithm(decMatrix, weights, criteria_directions):
    if decMatrix.empty:
        raise ValueError("The decision matrix is empty, unable to perform TOPSIS.")

    scaler = MinMaxScaler()
    normaMatrix = scaler.fit_transform(decMatrix)
    w = normaMatrix * weights
    
    iplus = []
    imoins = []
    for i, col in enumerate(decMatrix.columns):
        if criteria_directions[col] == "max":
            iplus.append(np.max(w[:, i]))
            imoins.append(np.min(w[:, i]))
        else:
            iplus.append(np.min(w[:, i]))
            imoins.append(np.max(w[:, i]))
    
    s_plus = np.sqrt(np.sum((w - iplus) ** 2, axis=1))
    s_moins = np.sqrt(np.sum((w - imoins) ** 2, axis=1))
    
    C = s_moins / (s_plus + s_moins)
    rang =  pd.Series(C, index=decMatrix.index).sort_values(ascending=False)
    return rang

def topsisAffichage(rankings, ontoManager, selectedSoftgoals):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""### :orange[For the Implementation, You need the following Functionnal Patterns Recommended]""")
        for pattern, score in rankings.items():
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if score >= 0.7:
                    st.success(f"✅ {pattern}: High Importance with score {score:.2f}: RECOMMENDED")
                elif 0.5 <= score < 0.7:
                    st.info(f"⚖️ {pattern}: Medium Importance with score {score:.2f}")
                else:
                    st.error(f"❌ {pattern}: Low Importance with score {score:.2f}")
                
                #for softgoal in selectedSoftgoals:
                #    expl = ontoManager.get_explanation(pattern, softgoal)
                #    st.markdown(f"<p class='explanation'><strong>{softgoal}</strong> : {expl}</p>", unsafe_allow_html=True)
                #st.markdown("</div>", unsafe_allow_html=True)