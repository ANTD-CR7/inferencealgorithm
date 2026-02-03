"""
BAYESIAN NETWORK INFERENCE LAB
🚀 FUTURISTIC AI RESEARCH INTERFACE 🚀
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling

# Shared Utilities
from experiment_utils import get_all_networks

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Inference Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply shared styles or custom styles here
st.markdown("""
<style>
    /* ===== GLOBAL DARK THEME ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%);
        color: #e0e7ff;
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
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">🧬 BAYESIAN INFERENCE LAB</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">⚡ Advanced AI Experimental Platform | Real-Time Probabilistic Reasoning ⚡</p>', unsafe_allow_html=True)

# Status bar============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🎛️ CONTROL PANEL")
    
    valid_networks = get_all_networks()
    network_choice = st.selectbox("Select Network", list(valid_networks.keys()))
    
    algorithm_choice = st.selectbox(
        "Algorithm Mode",
        ["Variable Elimination", "Gibbs Sampling", "⚡ Compare Both"]
    )
    
    num_samples = 10000
    if algorithm_choice in ["Gibbs Sampling", "⚡ Compare Both"]:
        num_samples = st.slider("Gibbs Samples", 1000, 50000, 10000, 1000)

model = valid_networks[network_choice]
nodes = list(model.nodes())
edges = list(model.edges())

# ============================================================================
# NETWORK INFO
# ============================================================================

col1, col2, col3 = st.columns(3)
col1.metric("VARIABLES", len(nodes))
col2.metric("EDGES", len(edges))
col3.metric("NODES", len(nodes))

with st.expander("📖 NETWORK DETAILS"):
    st.write(f"**Variables:** {', '.join(nodes)}")
    st.write(f"**Edges:** {edges}")

st.markdown("---")

# ============================================================================
# QUERY CONFIGURATION
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 TARGET VARIABLE")
    query_var = st.selectbox("Query", nodes)

with col2:
    st.markdown("### 📌 EVIDENCE")
    evidence = {}
    evidence_text = []
    
    for var in nodes:
        if var != query_var:
            if st.checkbox(f"{var}", key=f"obs_{var}"):
                val = st.radio(f"{var} state", [0, 1], horizontal=True, key=f"val_{var}")
                evidence[var] = val
                evidence_text.append(f"{var}={val}")

if evidence:
    st.success(f"**Evidence:** {', '.join(evidence_text)}")
else:
    st.info("No evidence selected (Marginal Probability)")

st.markdown("---")

# ============================================================================
# INFERENCE
# ============================================================================

if st.button("🚀 EXECUTE INFERENCE", type="primary", use_container_width=True):
    
    # --- VARIABLE ELIMINATION ---
    if algorithm_choice in ["Variable Elimination", "⚡ Compare Both"]:
        with st.spinner("Computing Exact Inference (VE)..."):
            start = time.time()
            ve = VariableElimination(model)
            result_ve = ve.query([query_var], evidence=evidence, show_progress=False)
            time_ve = time.time() - start
        
        st.markdown("### ⚡ VARIABLE ELIMINATION (Exact)")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"P({query_var}=0)", f"{result_ve.values[0]:.4f}")
        c2.metric(f"P({query_var}=1)", f"{result_ve.values[1]:.4f}")
        c3.metric("Time", f"{time_ve*1000:.2f} ms")
        
        # Plot
        fig = go.Figure([go.Bar(
            x=['0 (False)', '1 (True)'], 
            y=result_ve.values,
            marker_color=['#ef4444', '#10b981']
        )])
        fig.update_layout(title=f"Exact Distribution: {query_var}", height=300)
        st.plotly_chart(fig, use_container_width=True)

    # --- GIBBS SAMPLING ---
    if algorithm_choice in ["Gibbs Sampling", "⚡ Compare Both"]:
        with st.spinner(f"Running Gibbs Sampling ({num_samples} samples)..."):
            start = time.time()
            gibbs = GibbsSampling(model)
            
            # FIX: Manual Rejection Sampling
            # 1. Generate samples without evidence
            samples = gibbs.sample(size=num_samples) # Removed show_progress=False just in case
            
            # 2. Filter by evidence
            for var, val in evidence.items():
                samples = samples[samples[var] == val]
            
            time_gibbs = time.time() - start
            
        st.markdown("### 🎲 GIBBS SAMPLING (Approximate)")
        
        if len(samples) == 0:
            st.error("❌ No samples matched the evidence! Try reducing evidence or increasing sample size.")
            prob_0 = prob_1 = 0.0
        else:
            prob_1 = samples[query_var].value_counts(normalize=True).get(1, 0.0)
            prob_0 = 1.0 - prob_1
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(f"P({query_var}=0)", f"{prob_0:.4f}")
            c2.metric(f"P({query_var}=1)", f"{prob_1:.4f}")
            c3.metric("Time", f"{time_gibbs*1000:.2f} ms")
            c4.metric("Valid Samples", f"{len(samples)}")
            
            # Plot
            fig = go.Figure([go.Bar(
                x=['0 (False)', '1 (True)'], 
                y=[prob_0, prob_1],
                marker_color=['#ef4444', '#10b981']
            )])
            fig.update_layout(title=f"Approximate Distribution: {query_var}", height=300)
            st.plotly_chart(fig, use_container_width=True)
            
    # --- COMPARISON ---
    if algorithm_choice == "⚡ Compare Both" and len(samples) > 0:
        st.markdown("### ⚖️ COMPARISON")
        error = abs(result_ve.values[1] - prob_1)
        st.metric("Absolute Error", f"{error:.6f}", delta="Lower is better", delta_color="inverse")
