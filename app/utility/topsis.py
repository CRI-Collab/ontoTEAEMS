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
    #st.markdown("""### :orange[Recommendation Results]""")
    col_rec, col_patterns = st.columns([2, 8])

    with col_rec:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; height: 100%;'>
            <h4 style='color: #4a5568rr;'>🔍 Recommendation</h4>
            <hr style='margin: 10px 0;'>
            <p>Based on your softgoals preferences, here are the most suitable patterns:</p>
        </div>
        """, unsafe_allow_html=True)

    with col_patterns:
        # Trier les patterns par score décroissant
        sorted_patterns = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        
        for pattern, score in sorted_patterns:
            fpatterns = pattern.replace("_", " ")
            # Définir le style en fonction du score
            if score >= 0.6:
                color = "#2ecc71"  # Vert
                icon = "✅"
                label = "STRONGLY RECOMMENDED"
            elif 0.5 <= score < 0.6:
                color = "#3498db"  # Bleu
                icon = "ℹ️"
                label = "MODERATELY RECOMMENDED"
            else:
                color = "#e74c3c"  # Rouge
                icon = "⚠️"
                label = "NOT RECOMMENDED"

            # Carte pour chaque pattern
            st.markdown(f"""
            <div style='
                background-color: #f8f9fa; 
                border-left: 5px solid {color};
                padding: 12px;
                border-radius: 5px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <div style='display: flex; justify-content: space-between;'>
                    <b>{icon} {fpatterns}</b>
                    <span style='color: {color}; font-weight: bold;'>{label}</span>
                </div>
                <div style='margin-top: 8px; font-size: 0.9em; color:r #555;'>
                    Score: <b>{score:.2f}</b> | Matching softgoals: <i>{", ".join(selectedSoftgoals)}</i>
                </div>
            </div>
            """, unsafe_allow_html=True)