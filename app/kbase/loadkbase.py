import os
import pandas as pd
import streamlit as st
from owlready2 import get_ontology

def loadKnowledgebase(db_manager, ontoPath):
    db_manager.clear_tables()
    if not os.path.exists(ontoPath):
        raise FileNotFoundError(f"L'ontologie n'existe pas : {ontoPath}")

    ontology = get_ontology(ontoPath).load()

    for cls in ontology.classes():
        for instance in cls.instances():
            comment = instance.comment[0] if instance.comment else ""
            if "Pattern" in cls.name:
                db_manager.insertPatterns(instance.name, comment)
            elif "Softgoal" in cls.name:
                db_manager.insertSoftgoals(instance.name, comment)

    for relation in ontology.classes():
        for instance in relation.instances():
            pattern = instance.hasSource[0].name if instance.hasSource else None
            softgoal = instance.hasTarget[0].name if instance.hasTarget else None
            influenceType = instance.hasInfluenceType[0].name if instance.hasInfluenceType else None
            reason = instance.hasReason[0] if isinstance(instance.hasReason, list) and instance.hasReason else "BISUMBA"

            if pattern and softgoal:
                db_manager.insertRelations(pattern, softgoal, influenceType, reason)

                data_for_pattern = st.session_state.matriceA_dict.get(pattern)

                score = 0
                if data_for_pattern is not None and softgoal in data_for_pattern:
                    scoreValue = data_for_pattern[softgoal]
                    scoreValue = str(scoreValue).strip() if pd.notna(scoreValue) else ""
                    score = scoreValue.count('+') - scoreValue.count('-')
                    
                db_manager.insertScore(pattern, softgoal, influenceType, reason, score)