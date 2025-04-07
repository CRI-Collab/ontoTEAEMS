import streamlit as st

st.set_page_config(
    page_title="BC-TEAEM DEV",
    page_icon=":shield:",
    layout="centered",
    initial_sidebar_state="expanded"
)

with open('css/welcome.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.sidebar.title("Welcome to BC-TEAEM DEV")
st.sidebar.info(
    "Explore the power of blockchain with BC-TEAEM DEV"
)

with st.container():
    st.markdown(
        """
        ## Welcome to BC-TEAEM DEV
        
        **BC-TEAEM DEV** is an advanced tool designed to help you explore and implement **Blockchain-TEAEM patterns**, 
        a framework for recommending blockchain-based patterns tailored to your application's needs.
        
        ### 🔍 Key Features:
        - **Softgoal Guidance** – Prioritize and align your design goals.
        - **Score Analysis** – Evaluate and compare patterns based on your selected Patterns and Score.
        - **Pattern Recommendations** – Get tailored recommendations for blockchain patterns. 
        """,
        unsafe_allow_html=True
    )

st.markdown("## 💊 Drugs Traceability Requirements with Blockchain")
st.markdown(
    """
    Below is a list of key requirements for implementing **Drugs traceability** using blockchain technology:
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown(
        """
        <div class="requirements-list">
            <ul>
                <li><strong>Integrity</strong> – Ensure that all transactions and data entries are tamper-proof and cannot be altered after being recorded.</li>
                <li><strong>Data Privacy</strong> – Protect sensitive patient and transaction data using encryption and access controls.</li>
                <li><strong>Interoperability</strong> – Ensure compatibility with existing healthcare systems and standards (e.g., HL7, FHIR).</li>
                <li><strong>Security</strong> Ensures data are protected against cyber attacks,unauthorized access, and malicious activities.</li>
                <li><strong>Performance</strong> – Support a high volume of transactions and data without compromising performance.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

if "config_done" not in st.session_state:
    st.session_state["config_done"] = False

st.markdown("#### Click the button to start")
if st.button("Validate Hardgoals and Proceed to TEAEM"):
    st.switch_page("pages/teaem.py")

st.markdown("---")
st.markdown("""
    <div class="footer">
        © 2024 BC-TEAEM DEV. All rights reserved.<br>
    </div>
""", unsafe_allow_html=True)