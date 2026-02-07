"""
Experiment Utilities
Shared helper functions for Bayesian Network experiments.
"""

from typing import Dict, Any, Tuple, Optional
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pgmpy.models import BayesianNetwork
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling

# Network factories (used by experiments and API)
from alarm_network import create_alarm_network
from student_network import create_student_network
from synthetic_network import create_synthetic_network

def get_all_networks() -> Dict[str, BayesianNetwork]:
    """Returns a dictionary of all test networks."""
    return {
        'Synthetic (3 vars)': create_synthetic_network(),
        'Alarm (4 vars)': create_alarm_network(),
        'Student (5 vars)': create_student_network()
    }

def get_network_queries() -> Dict[str, Tuple[str, Dict[str, int], int]]:
    """
    Returns standard queries for each network.
    Format: NetworkName -> (QueryVar, EvidenceDict, TargetState)
    """
    return {
        'Synthetic (3 vars)': ('Rain', {'Late': 1}, 1),
        'Alarm (4 vars)': ('Burglary', {'PhoneCall': 1}, 1),
        'Student (5 vars)': ('Intelligence', {'SAT': 1}, 1)
    }

def run_exact_inference(model: BayesianNetwork, query_var: str, evidence: Dict[str, int], target_state: int) -> float:
    """Exact inference via Variable Elimination (returns P(query_var=target_state | evidence))."""
    ve = VariableElimination(model)
    result = ve.query([query_var], evidence=evidence, show_progress=False)
    return result.values[target_state]

def run_gibbs_inference(model: BayesianNetwork, query_var: str, evidence: Dict[str, int], 
                       samples: int, target_state: int) -> Tuple[float, float]:
    """
    Gibbs sampling with manual evidence filtering.
    Returns (estimated_probability, execution_time_seconds).
    """
    gibbs = GibbsSampling(model)
    start_time = time.time()
    
    # Generate unconditional samples; evidence is applied by filtering.
    generated_samples = gibbs.sample(size=samples)
    
    # Evidence filtering (manual rejection)
    filtered_samples = generated_samples
    for var, state in evidence.items():
        filtered_samples = filtered_samples[filtered_samples[var] == state]
        
    execution_time = time.time() - start_time
    
    if len(filtered_samples) == 0:
        return 0.0, execution_time
        
    # Empirical probability of the target state
    prob = filtered_samples[query_var].value_counts(normalize=True).get(target_state, 0.0)
    
    return prob, execution_time

def setup_plot_style():
    """Configures professional plotting aesthetics."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rc('font', size=12)
    plt.rc('axes', titlesize=14, labelsize=12)
    plt.rc('xtick', labelsize=10)
    plt.rc('ytick', labelsize=10)
    plt.rc('legend', fontsize=11)
    plt.rc('figure', titlesize=16)

def save_plot(filename: str):
    """Saves plot with high resolution."""
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"OK: Graph saved to: {filename}")

def save_results(df: pd.DataFrame, filename: str):
    """Saves DataFrame to CSV."""
    df.to_csv(filename, index=False)
    print(f"OK: Results saved to: {filename}")

