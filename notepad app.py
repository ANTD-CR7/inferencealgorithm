"""
BAYESIAN NETWORK INFERENCE LAB
🚀 FUTURISTIC AI RESEARCH INTERFACE 🚀
"""

import streamlit as st
from alarm_network import create_alarm_network
from student_network import create_student_network
from synthetic_network import create_synthetic_network
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

# ============================================================================
# FUTURISTIC PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Inference Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# FUTURISTIC CSS STYLING - DARK MODE + NEON
# ============================================================================

st.markdown("""
<style>
    /* ===== GLOBAL DARK THEME ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%);
        color: #e0e7ff;
    }
    
    /* ===== ANIMATED BACKGROUND ===== */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
        animation: gradientShift 15s ease infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px 0 rgba(99, 102, 241, 0.2),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    }
    
    /* ===== NEON TEXT ===== */
    .neon-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 
            0 0 20px rgba(99, 102, 241, 0.5),
            0 0 40px rgba(168, 85, 247, 0.3);
        animation: pulse 3s ease-in-out infinite;
        margin-bottom: 0;
        letter-spacing: 2px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .subtitle {
        font-size: 1.3rem;
        text-align: center;
        color: #a5b4fc;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* ===== CYBER BORDERS ===== */
    .cyber-border {
        position: relative;
        border: 2px solid transparent;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .cyber-border::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899, #6366f1);
        border-radius: 15px;
        z-index: -1;
        animation: borderGlow 3s linear infinite;
        background-size: 300% 300%;
    }
    
    @keyframes borderGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.6);
        background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%);
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a5b4fc;
        font-size: 1rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #a5b4fc;
        font-weight: 600;
    }
    
    /* ===== SELECT BOXES ===== */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        color: #e0e7ff;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 10px 10px 0 0;
        color: #a5b4fc;
        font-weight: 600;
        padding: 1rem 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(168, 85, 247, 0.3) 100%);
        border: 1px solid rgba(99, 102, 241, 0.5);
        color: #e0e7ff;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        color: #a5b4fc;
        font-weight: 600;
    }
    
    /* ===== DATAFRAME ===== */
    .dataframe {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
    }
    
    /* ===== CHECKBOX/RADIO ===== */
    .stCheckbox label, .stRadio label {
        color: #e0e7ff;
    }
    
    /* ===== INFO/SUCCESS/WARNING BOXES ===== */
    .stAlert {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #6366f1;
        border-radius: 10px;
        color: #e0e7ff;
    }
    
    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-top-color: #6366f1;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c3aed, #c026d3);
    }
    
    /* ===== PARTICLE EFFECT ===== */
    .particle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: rgba(99, 102, 241, 0.6);
        border-radius: 50%;
        pointer-events: none;
        animation: float 20s infinite;
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0) translateX(0);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) translateX(50px);
            opacity: 0;
        }
    }
</style>

<!-- Particle Effect -->
<div class="particle" style="left: 10%; animation-delay: 0s;"></div>
<div class="particle" style="left: 30%; animation-delay: 3s;"></div>
<div class="particle" style="left: 50%; animation-delay: 6s;"></div>
<div class="particle" style="left: 70%; animation-delay: 9s;"></div>
<div class="particle" style="left: 90%; animation-delay: 12s;"></div>
""", unsafe_allow_html=True)

# ============================================================================
# FUTURISTIC HEADER
# ============================================================================

st.markdown('<h1 class="neon-title">🧬 BAYESIAN INFERENCE LAB</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">⚡ Advanced AI Experimental Platform | Real-Time Probabilistic Reasoning ⚡</p>', unsafe_allow_html=True)

# Status bar
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**🟢 SYSTEM:** Online")
with col2:
    st.markdown("**🧠 ALGORITHMS:** 2 Active")
with col3:
    st.markdown("**📊 NETWORKS:** 3 Loaded")
with col4:
    st.markdown(f"**⏰ TIME:** {time.strftime('%H:%M:%S')}")

st.markdown("---")

# ============================================================================
# SIDEBAR - FUTURISTIC CONTROL PANEL
# ============================================================================

with st.sidebar:
    st.markdown("## 🎛️ CONTROL PANEL")
    st.markdown("---")
    
    st.markdown("### 🔬 NETWORK SELECT")
    network_choice = st.selectbox(
        "",
        ["Alarm Network", "Student Network", "Synthetic Network"],
        label_visibility="collapsed"
    )
    
    st.markdown("### 🤖 ALGORITHM MODE")
    algorithm_choice = st.selectbox(
        "",
        ["Variable Elimination", "Gibbs Sampling", "⚡ Compare Both"],
        label_visibility="collapsed"
    )
    
    with st.expander("⚙️ ADVANCED SETTINGS"):
        if algorithm_choice in ["Gibbs Sampling", "⚡ Compare Both"]:
            num_samples = st.slider("Samples", 1000, 50000, 10000, 1000)
            burn_in = st.slider("Burn-in", 0, 5000, 1000, 100)
        else:
            num_samples = 10000
            burn_in = 1000
    
    st.markdown("---")
    st.markdown("### 📡 PROJECT STATUS")
    progress = 85
    st.progress(progress / 100)
    st.markdown(f"**Completion:** {progress}%")
    st.markdown("**Deadline:** Feb 7, 2026")
    st.markdown("**Status:** 🟢 On Track")

# ============================================================================
# LOAD NETWORK
# ============================================================================

network_configs = {
    "Alarm Network": {
        'model': create_alarm_network(),
        'variables': ['Burglary', 'Earthquake', 'Alarm', 'PhoneCall'],
        'description': '🚨 Home security system detection',
        'icon': '🏠',
        'color': '#ef4444'
    },
    "Student Network": {
        'model': create_student_network(),
        'variables': ['Difficulty', 'Intelligence', 'Grade', 'SAT', 'Letter'],
        'description': '🎓 Academic performance modeling',
        'icon': '📚',
        'color': '#3b82f6'
    },
    "Synthetic Network": {
        'model': create_synthetic_network(),
        'variables': ['Rain', 'Traffic', 'Late'],
        'description': '🌧️ Simple causal chain demonstration',
        'icon': '🚗',
        'color': '#10b981'
    }
}

config = network_configs[network_choice]
model = config['model']

# ============================================================================
# NETWORK INFO PANEL
# ============================================================================

st.markdown(f"## {config['icon']} {network_choice}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("VARIABLES", len(config['variables']))
with col2:
    st.metric("EDGES", len(list(model.edges())))
with col3:
    st.metric("NODES", len(list(model.nodes())))

with st.expander("📖 NETWORK SPECIFICATIONS", expanded=False):
    st.markdown(f"**Description:** {config['description']}")
    st.markdown(f"**Variables:** `{', '.join(config['variables'])}`")
    st.markdown(f"**Structure:** Directed Acyclic Graph (DAG)")

st.markdown("---")

# ============================================================================
# QUERY CONFIGURATION
# ============================================================================

st.markdown("## 🎯 QUERY CONFIGURATION")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 TARGET VARIABLE")
    query_var = st.selectbox("", config['variables'], label_visibility="collapsed")
    st.info(f"**Computing:** P({query_var} | Evidence)")

with col2:
    st.markdown("### 📌 EVIDENCE INPUT")
    evidence = {}
    evidence_display = []
    
    for var in config['variables']:
        if var != query_var:
            if st.checkbox(f"**{var}**", key=f"obs_{var}"):
                val = st.radio(
                    "",
                    options=[0, 1],
                    format_func=lambda x: "🔴 FALSE" if x == 0 else "🟢 TRUE",
                    key=f"val_{var}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                evidence[var] = val
                evidence_display.append(f"{var}={'TRUE' if val==1 else 'FALSE'}")
    
    if evidence:
        st.success(f"**EVIDENCE:** {', '.join(evidence_display)}")
    else:
        st.warning("⚠️ NO EVIDENCE | Computing marginal probability")

st.markdown("---")

# ============================================================================
# RUN INFERENCE BUTTON
# ============================================================================

if st.button("🚀 EXECUTE INFERENCE", type="primary", use_container_width=True):
    
    st.markdown("## 📊 INFERENCE RESULTS")
    
    # Progress animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"Processing... {i+1}%")
        time.sleep(0.01)
    
    status_text.empty()
    progress_bar.empty()
    
    # VE
    if algorithm_choice in ["Variable Elimination", "⚡ Compare Both"]:
        st.markdown("### ⚡ VARIABLE ELIMINATION | EXACT MODE")
        
        with st.spinner("Computing exact probabilities..."):
            ve = VariableElimination(model)
            start_time = time.time()
            result_ve = ve.query([query_var], evidence=evidence)
            time_ve = time.time() - start_time
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"P({query_var}=0)", f"{result_ve.values[0]:.6f}")
        with col2:
            st.metric(f"P({query_var}=1)", f"{result_ve.values[1]:.6f}")
        with col3:
            st.metric("⏱️ TIME", f"{time_ve*1000:.2f} ms")
        
        # Futuristic bar chart
        fig_ve = go.Figure(data=[
            go.Bar(
                x=['FALSE', 'TRUE'],
                y=result_ve.values,
                marker=dict(
                    color=['#ef4444', '#10b981'],
                    line=dict(color='#6366f1', width=2)
                ),
                text=[f'{v:.4f}' for v in result_ve.values],
                textposition='outside',
                textfont=dict(size=14, color='white', family='Arial Black')
            )
        ])
        
        fig_ve.update_layout(
            title=dict(text=f'P({query_var} | Evidence)', font=dict(size=20, color='white')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            font=dict(color='white'),
            yaxis=dict(range=[0, 1], gridcolor='rgba(99, 102, 241, 0.2)'),
            xaxis=dict(gridcolor='rgba(99, 102, 241, 0.2)'),
            height=400
        )
        
        st.plotly_chart(fig_ve, use_container_width=True)
    
    # GIBBS
    if algorithm_choice in ["Gibbs Sampling", "⚡ Compare Both"]:
        st.markdown("---")
        st.markdown("### 🎲 GIBBS SAMPLING | APPROXIMATE MODE")
        
        with st.spinner(f"Generating {num_samples:,} samples..."):
            gibbs = GibbsSampling(model)
            start_time = time.time()
            samples = gibbs.sample(size=num_samples, evidence=evidence)
            time_gibbs = time.time() - start_time
        
        prob_1 = samples[query_var].mean()
        prob_0 = 1 - prob_1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"P({query_var}=0)", f"{prob_0:.6f}")
        with col2:
            st.metric(f"P({query_var}=1)", f"{prob_1:.6f}")
        with col3:
            st.metric("⏱️ TIME", f"{time_gibbs*1000:.2f} ms")
        with col4:
            st.metric("SAMPLES", f"{num_samples:,}")
        
        # Same futuristic visualization
        fig_gibbs = go.Figure(data=[
            go.Bar(
                x=['FALSE', 'TRUE'],
                y=[prob_0, prob_1],
                marker=dict(
                    color=['#ef4444', '#10b981'],
                    line=dict(color='#a855f7', width=2)
                ),
                text=[f'{prob_0:.4f}', f'{prob_1:.4f}'],
                textposition='outside',
                textfont=dict(size=14, color='white', family='Arial Black')
            )
        ])
        
        fig_gibbs.update_layout(
            title=dict(text=f'P({query_var} | Evidence) - Approximate', font=dict(size=20, color='white')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15, 23, 42, 0.6)',
            font=dict(color='white'),
            yaxis=dict(range=[0, 1], gridcolor='rgba(99, 102, 241, 0.2)'),
            xaxis=dict(gridcolor='rgba(99, 102, 241, 0.2)'),
            height=400
        )
        
        st.plotly_chart(fig_gibbs, use_container_width=True)
    
    # COMPARISON
    if algorithm_choice == "⚡ Compare Both":
        st.markdown("---")
        st.markdown("## ⚖️ ALGORITHM COMPARISON")
        
        diff = abs(result_ve.values[1] - prob_1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ACCURACY DIFF", f"{diff:.6f}")
        with col2:
            speedup = time_gibbs / time_ve if time_ve > 0 else 0
            st.metric("SPEEDUP", f"{speedup:.1f}x", delta="VE Faster")
        with col3:
            quality = "EXCELLENT" if diff < 0.001 else "GOOD" if diff < 0.01 else "FAIR"
            st.metric("QUALITY", quality)
        
        # Comparison table
        comparison_df = pd.DataFrame({
            'Algorithm': ['Variable Elimination', 'Gibbs Sampling'],
            f'P({query_var}=0)': [f'{result_ve.values[0]:.6f}', f'{prob_0:.6f}'],
            f'P({query_var}=1)': [f'{result_ve.values[1]:.6f}', f'{prob_1:.6f}'],
            'Time (ms)': [f'{time_ve*1000:.2f}', f'{time_gibbs*1000:.2f}'],
            'Type': ['⚡ Exact', '🎲 Approximate']
        })
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ============================================================================
# FUTURISTIC FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #64748b;'>
    <p style='font-size: 1.2rem; font-weight: 600; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🧬 BAYESIAN INFERENCE LABORATORY
    </p>
    <p style='font-size: 0.9rem;'>
        Advanced Probabilistic Reasoning System | Powered by pgmpy + Streamlit
    </p>
    <p style='font-size: 0.85rem; color: #475569;'>
        Submission Deadline: February 7, 2026 | Status: 85% Complete
    </p>
</div>
""", unsafe_allow_html=True)