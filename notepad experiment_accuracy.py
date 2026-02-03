"""
EXPERIMENT 2: Accuracy Comparison
Measures Mean Absolute Error (MAE) of Gibbs Sampling vs Exact Inference (VE)
"""

import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from alarm_network import create_alarm_network
from student_network import create_student_network
from synthetic_network import create_synthetic_network
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling

print("="*60)
print("EXPERIMENT 2: ACCURACY COMPARISON")
print("="*60)

# Define networks to test
networks = {
    'Synthetic (3 vars)': create_synthetic_network(),
    'Alarm (4 vars)': create_alarm_network(),
    'Student (5 vars)': create_student_network()
}

# Define queries for each network (Query Variable, Evidence) and finding P(QueryVar=1)
# Format: Network: (QueryVar, EvidenceDict, TargetStateIndex)
# Assuming 0/1 states, we track state 1 (True/High/etc)
queries = {
    'Synthetic (3 vars)': ('Rain', {'Late': 1}, 1),
    'Alarm (4 vars)': ('Burglary', {'PhoneCall': 1}, 1),
    'Student (5 vars)': ('Intelligence', {'SAT': 1}, 1)
}

# Storage for results
results = {
    'Network': [],
    'Variables': [],
    'VE_Prob': [],
    'Gibbs_Prob_Mean': [],
    'MAE': [],
    'Error_Std': []
}

# Settings
num_trials = 10
num_samples = 10000

print(f"\nRunning {num_trials} trials per network (Samples={num_samples})...\n")

for network_name, model in networks.items():
    print(f"Testing: {network_name}")
    
    query_var, evidence, target_state = queries[network_name]
    num_vars = len(model.nodes())
    
    # 1. Exact Inference (Ground Truth)
    ve = VariableElimination(model)
    ve_result = ve.query([query_var], evidence=evidence, show_progress=False)
    # Extract probability of the target state
    ve_prob = ve_result.values[target_state]
    print(f"  Exact Probability (VE): {ve_prob:.4f}")
    
    # 2. Approximate Inference (Gibbs Sampling)
    gibbs_probs = []
    errors = []
    
    for trial in range(num_trials):
        start = time.time()
        gibbs = GibbsSampling(model)
        
        # FIX: Manual Rejection Sampling
        # Generate samples without evidence
        samples = gibbs.sample(size=num_samples)
        
        # Filter samples matching evidence
        for var, state in evidence.items():
            samples = samples[samples[var] == state]
            
        if len(samples) == 0:
            print(f"    Trial {trial+1}: No matching samples! Evidence might be too rare.")
            est_prob = 0.0 # Fallback
        else:
            # Calculate conditional probability from samples
            # count(query_var == target_state) / count(total filtered samples)
            est_prob = samples[query_var].value_counts(normalize=True).get(target_state, 0.0)
            
        gibbs_probs.append(est_prob)
        errors.append(abs(ve_prob - est_prob))
        
    # Calculate statistics
    gibbs_mean = np.mean(gibbs_probs)
    mae = np.mean(errors)
    error_std = np.std(errors)
    
    # Store results
    results['Network'].append(network_name)
    results['Variables'].append(num_vars)
    results['VE_Prob'].append(ve_prob)
    results['Gibbs_Prob_Mean'].append(gibbs_mean)
    results['MAE'].append(mae)
    results['Error_Std'].append(error_std)
    
    print(f"  Gibbs Mean Prob: {gibbs_mean:.4f}")
    print(f"  MAE: {mae:.4f} ± {error_std:.4f}\n")

# Create DataFrame
df = pd.DataFrame(results)

# Save to CSV
df.to_csv('accuracy_results.csv', index=False)
print("✅ Results saved to: accuracy_results.csv")

# Create visualization
fig, ax = plt.subplots(figsize=(10, 6))

# Plot MAE
x = np.arange(len(df))
bars = ax.bar(x, df['MAE'], yerr=df['Error_Std'], 
              color='#ef4444', alpha=0.8, capsize=5, edgecolor='black')

ax.set_xlabel('Network', fontsize=12, fontweight='bold')
ax.set_ylabel('Mean Absolute Error (MAE)', fontsize=12, fontweight='bold')
ax.set_title(f'Gibbs Sampling Accuracy (vs VE) - {num_samples} samples', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(df['Network'])
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.4f}',
            ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('accuracy_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Graph saved to: accuracy_comparison.png")

plt.show()

print("\n" + "="*60)
print("EXPERIMENT 2 COMPLETE!")
print("="*60)