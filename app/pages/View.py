import streamlit as st

st.set_page_config(
    page_title="BC-ONTOTEAM - Workflow Process",
    initial_sidebar_state="expanded",
    page_icon=":busts_in_silhouette:",
    layout="wide"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("css/home.css")

st.sidebar.title("🏭 Architecture Decision Workflow")

st.sidebar.markdown("""
<div style="
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
">
<h4 style="color: #2c3e50; margin-top: 0;">🔍 End-to-End Process Flow</h4>

<ol style="padding-left: 1.2rem; margin-bottom: 0;">
    <li style="margin-bottom: 0.5rem;">
        <strong>Business Expert</strong> selects softgoals and assigns priority weights, then validates
    </li>
    <li style="margin-bottom: 0.5rem;">
        Generated <strong>Softgoal Map</strong> is sent to Technical Expert for review
    </li>
    <li style="margin-bottom: 0.5rem;">
        <strong>Technical Expert</strong> verifies solution:
        <ul style="padding-left: 1.2rem; margin: 0.3rem 0;">
            <li>Resolves trade-offs by prioritizing domain-relevant patterns</li>
            <li>Escalates to Business Expert for decisions on conflicting softgoals (Bottom-up traceability)</li>
        </ul>
    </li>
    <li style="margin-bottom: 0.5rem;">
        <strong>Business Expert</strong> finalizes softgoal prioritization and approves solution
    </li>
    <li style="margin-bottom: 0;">
        <strong>Final Softgoal Map</strong> is:
        <ul style="padding-left: 1.2rem; margin: 0.3rem 0 0;">
            <li>Quality-checked</li>
            <li>Enhanced with MDCN algorithm-recommended Non-Functional Patterns</li>
            <li>Validated by Technical Expert</li>
        </ul>
    </li>
</ol>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <h2>🔑 Workflow Process</h2>
    <p>This application consists of two fundamental roles: <em><strong style="color:red;">Business Users and Technical Users.</strong></em></p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
    <div class="timeline">
        <div class="timeline-item">
            <div class="timeline-icon">1</div>
            <div class="timeline-content">
                <div class="expert-tag"><h4> 🧑‍💼 Business Expert</h4> </div>
                <p><strong>Softgoals Prioritization:</strong> Define your business objectives and express your softgoals preferences<p>
                <p><strong>Decision Authority:</strong><em> In case of trade-offs between softgoals</em>, resolves these trade-offs by making final prioritization</p>
                <p><em>Your input guides the architecture generation process</em></p>
            </div>
        </div>
        <div class="timeline-connector"></div>
        <div class="timeline-item">
            <div class="timeline-icon">2</div>
            <div class="timeline-content">
                <div class="expert-tag"> <h4>👨‍💻 Technical Expert</h4> </div>
                <p>Review the softgoal maps and make technical decisions by selecting the appropriate architectural patterns.</p>
                <p><em> In case of ambiguity, you can always ask the Business Expert to arbitrate.</em></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="button-container2">', unsafe_allow_html=True)
    btn_business = st.button(
        "🧑‍💼 Business Expert View", 
        key="business",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    btn_technical = st.button(
        "👨‍💻 Technical Expert View", 
        key="technical",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

if btn_business:
    st.balloons()
    st.session_state.role = "business"
    st.switch_page("pages/TeamManager.py")

if btn_technical:
    st.balloons()
    st.warning("Please Start Session as Domain Expert")