from math import inf
from owlready2 import *

class OntologyManager:
    def __init__(self, path):
        self.path = path
        self.ontology = get_ontology(path)

    def loadOntology(self):
        try:
            self.ontology.load()
            return "Ontologie chargée avec succès !"
        except Exception as e:
            return f"Erreur : {e}"

    def getClasses(self):
        if self.ontology:
            return list(self.ontology.classes())
        return []

    def getProperties(self):
        if self.ontology:
            return list(self.ontology.properties())
        return []

    def getIndividuals(self):
        if self.ontology:
            return list(self.ontology.individuals())
        return []

    def getIndividualByName(self, name):
        if self.ontology:
            for ind in self.ontology.individuals():
                if ind.name == name:
                    return ind
        return None
    
    def get_relations(self):
        if not self.ontology:
            return {}
        relations = {}
        for prop in self.ontology.properties():
            if hasattr(prop, "get_relations"):
                for sub, obj in prop.get_relations():
                    sub_name = getattr(sub, 'name', str(sub))
                    obj_name = getattr(obj, 'name', str(obj))

                    if prop.name not in relations:
                        relations[prop.name] = []
                    relations[prop.name].append((sub_name, obj_name))

        return relations
    
    def getAllPatterns(self):
        if self.ontology:
            return [ind for ind in self.ontology.Pattern.instances()]
        return []
    
    def getAllPatternss(self):
        if not self.ontology:
            print("Error: Ontology not loaded!")
            return []
        classes = list(self.ontology.classes())
        for cls in classes:
            if cls.__name__ == "Pattern":
                return list(cls.instances())
        print("Error: Influence class not found in ontology!")
        return []
        
    def AllSoftgoals(self):
        if self.ontology:
            return [ind for ind in self.ontology.Softgoal.instances()]
        return []
    
    def getIndividuals(self):
        if self.ontology:
            return list(self.ontology.individuals())
        return []
    
    def getInfluences(self):
        if not self.ontology:
            print("Error: Ontology not loaded!")
            return []
        classes = list(self.ontology.classes())
        for cls in classes:
            if cls.__name__ == "Influence":
                return list(cls.instances())
        print("Error: Influence class not found in ontology!")
        return []


    def getInfluenceTypes(self):
        """Retourne tous les individus de la classe InfluenceType"""
        if self.ontology:
            return [ind for ind in self.ontology.InfluenceType.instances()]
        return []
    
    def get_explanation(self, pattern, softgoal):
        if not self.ontology:
            return "Ontology not loaded."

        for influence in self.getInfluences():
            source = influence.hasSource[0] if hasattr(influence, 'hasSource') and influence.hasSource else None
            target = influence.hasTarget[0] if hasattr(influence, 'hasTarget') and influence.hasTarget else None

            if source and target and source.name == pattern and target.name == softgoal:
                res = influence.hasReason[0] if hasattr(influence, 'hasReason') and influence.hasReason else "No reason provided"
                return res

        return "No explanation found."

def get_alternative_explanation(self, pattern, alt, softgoal):
        for influence in self.getInfluences():
            if hasattr(influence, 'hasSource') and influence.hasSource:
                source = influence.hasSource[0]
                if source.name.lower() == alt.lower():
                    # Vérifier que l'influence possède une cible correspondant au softgoal
                    if hasattr(influence, 'hasTarget') and influence.hasTarget:
                        target = influence.hasTarget[0]
                        if target.name.lower() == softgoal.lower():
                            # Vérifier que le type d'influence est positif
                            if hasattr(influence, 'hasInfluenceType') and influence.hasInfluenceType:
                                influence_type = influence.hasInfluenceType[0]
                                if "positive" in influence_type.name.lower():
                                    # Retourner l'explication associée à l'influence
                                    if hasattr(influence, 'hasReason') and influence.hasReason:
                                        return influence.hasReason[0]
        return f"Aucune explication positive trouvée pour l'alternative '{alt}' concernant le softgoal '{softgoal}'."
