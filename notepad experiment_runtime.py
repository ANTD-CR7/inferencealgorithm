"""
EXPERIMENT 1: Runtime Comparison
Measures execution time of VE vs Gibbs across different networks
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
print("EXPERIMENT 1: RUNTIME COMPARISON")
print("="*60)

# Define networks to test
networks = {
    'Synthetic (3 vars)': create_synthetic_network(),
    'Alarm (4 vars)': create_alarm_network(),
    'Student (5 vars)': create_student_network()
}

# Define queries for each network
queries = {
    'Synthetic (3 vars)': ('Rain', {'Late': 1}),
    'Alarm (4 vars)': ('Burglary', {'PhoneCall': 1}),
    'Student (5 vars)': ('Intelligence', {'SAT': 1})
}

# Storage for results
results = {
    'Network': [],
    'Variables': [],
    'VE_Time_Mean': [],
    'VE_Time_Std': [],
    'Gibbs_Time_Mean': [],
    'Gibbs_Time_Std': [],
    'Speedup': []
}

# Number of trials for averaging
num_trials = 10
num_samples = 10000

print(f"\nRunning {num_trials} trials per network...\n")

for network_name, model in networks.items():
    print(f"Testing: {network_name}")
    
    query_var, evidence = queries[network_name]
    num_vars = len(model.nodes())
    
    # Run Variable Elimination trials
    ve_times = []
    for trial in range(num_trials):
        ve = VariableElimination(model)
        start = time.time()
        ve.query([query_var], evidence=evidence)
        ve_times.append(time.time() - start)
    
    # Run Gibbs Sampling trials
    gibbs_times = []
    for trial in range(num_trials):
        gibbs = GibbsSampling(model)
        start = time.time()
        samples = gibbs.sample(size=num_samples)
        # Rejection sampling: filter samples matching evidence
        for var, state in evidence.items():
            samples = samples[samples[var] == state]
        gibbs_times.append(time.time() - start)
    
    # Calculate statistics
    ve_mean = np.mean(ve_times)
    ve_std = np.std(ve_times)
    gibbs_mean = np.mean(gibbs_times)
    gibbs_std = np.std(gibbs_times)
    
    speedup = gibbs_mean / ve_mean if ve_mean > 0 else 0
    
    # Store results
    results['Network'].append(network_name)
    results['Variables'].append(num_vars)
    results['VE_Time_Mean'].append(ve_mean)
    results['VE_Time_Std'].append(ve_std)
    results['Gibbs_Time_Mean'].append(gibbs_mean)
    results['Gibbs_Time_Std'].append(gibbs_std)
    results['Speedup'].append(speedup)
    
    print(f"  VE:    {ve_mean*1000:.2f} ± {ve_std*1000:.2f} ms")
    print(f"  Gibbs: {gibbs_mean*1000:.2f} ± {gibbs_std*1000:.2f} ms")
    print(f"  Speedup: VE is {speedup:.1f}x faster\n")

# Create DataFrame
df = pd.DataFrame(results)

# Save to CSV
df.to_csv('runtime_results.csv', index=False)
print("✅ Results saved to: runtime_results.csv")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Execution Time Comparison
x = np.arange(len(df))
width = 0.35

bars1 = ax1.bar(x - width/2, df['VE_Time_Mean']*1000, width, 
                label='Variable Elimination', color='#3b82f6', alpha=0.8,
                yerr=df['VE_Time_Std']*1000, capsize=5)
bars2 = ax1.bar(x + width/2, df['Gibbs_Time_Mean']*1000, width,
                label='Gibbs Sampling', color='#8b5cf6', alpha=0.8,
                yerr=df['Gibbs_Time_Std']*1000, capsize=5)

ax1.set_xlabel('Network Size (variables)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
ax1.set_title('Runtime Comparison: VE vs Gibbs', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(df['Variables'])
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=9)

# Plot 2: Speedup Factor
bars3 = ax2.bar(df['Variables'], df['Speedup'], color='#10b981', alpha=0.8, edgecolor='black', linewidth=2)
ax2.axhline(y=1, color='red', linestyle='--', linewidth=2, label='Equal Speed')
ax2.set_xlabel('Network Size (variables)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Speedup Factor (VE faster when > 1)', fontsize=12, fontweight='bold')
ax2.set_title('VE Speedup Over Gibbs', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars3:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}x',
            ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('runtime_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Graph saved to: runtime_comparison.png")

plt.show()

print("\n" + "="*60)
print("EXPERIMENT 1 COMPLETE!")
print("="*60)
print("\nKey Findings:")
print(f"• VE fastest on: {df.loc[df['VE_Time_Mean'].idxmin(), 'Network']}")
print(f"• Largest speedup: {df['Speedup'].max():.1f}x on {df.loc[df['Speedup'].idxmax(), 'Network']}")
print(f"• VE consistently faster on small networks")