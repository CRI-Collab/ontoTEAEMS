import streamlit as st

def display_slider(label, value, key, container_class):
    st.markdown(f'<div class="slider-container-original {container_class}">', unsafe_allow_html=True)
    container = st.container(border=False)
    with container:
        st.slider(label, -2, 2, value, key=key, disabled=True)

def generateMap(sgmap, title):
    content = []
    if sgmap["improved"]:
        content.append(f'<p style="color: gray;">{title} Improves: {", ".join(sgmap["improved"])}</p>')
    if sgmap["harmed"]:
        content.append(f'<p style="color: gray;">{title} Harmed: {", ".join(sgmap["harmed"])}</p>')
    return "\n".join(content)

def getScoreValue(value):
    scale = {"": 0, "+": 1, "++": 2 }
    return scale.get(value, 0)

def likertValue(value):
    scale = { "--": -2, "-": -1, "": 0, "+": 1, "++": 2 }
    return scale.get(value, 0)

def displayBar(label, value):
    width = "0%" if value == 0 else "50%" if value == 1 else "100%"
    color = "lightgray" if value == 0 else ("red" if value < 0 else ("green" if value > 0 else "gray"))
    
    interpretation = {
        0: "Neutral",
        1: "Partially Improved",
        2: "Improved"}.get(value, "Worsens")
    
    st.markdown(
        f"""
        <div style="margin: 10px 0;">
            <strong>{label} ( {interpretation} )</strong>
            <div style="background: lightgray; width: 100%; height: 20px; border-radius: 10px; position: relative;">
                <div style="background: {color}; width: {width}; height: 20px; border-radius: 10px;"></div>
            </div>  
        </div>
        """,
        unsafe_allow_html=True,
    )

def update_choice(pattern, choice):
    if choice == "original":
        st.session_state[f"choix_original_{pattern}"] = True
        st.session_state[f"choix_variant_{pattern}"] = False
        st.session_state.user_choices[pattern] = "Original (Centralized)"
    elif choice == "variant":
        st.session_state[f"choix_original_{pattern}"] = False
        st.session_state[f"choix_variant_{pattern}"] = True
        st.session_state.user_choices[pattern] = "Variant (Decentralized)"

def mapStyles(pscores):
    sgMap = {"improved": [], "harmed": [], "neutral": []}
    for softgoal, score in pscores.items():
        if score in ["+", "++"]:
            sgMap["improved"].append(softgoal)
        elif score in ["-", "--"]:
            sgMap["harmed"].append(softgoal)
        else:
            sgMap["neutral"].append(softgoal)
    return sgMap

st.markdown(
    """
    <style>
    .slider-container {
        border: 1px solid #4CAF50; /* Bordure verte */
        border-radius: 20px; /* Coins arrondis */
        padding: 1px;
        margin: 0px 0;  
        background-color: #2196F3; /* Fond légèrement gris */
    }
    .slider-container-original {
        border-color: #2196F3; /* Bordure bleue pour l'original */
    }
    .slider-container-variant {
        border-color: #FF5722; /* Bordure orange pour la variante */
       
    }
    </style>
    """,
    unsafe_allow_html=True
)