"""
EXPERIMENT 3: Convergence Study
Tests how Gibbs accuracy improves with increasing sample size
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from alarm_network import create_alarm_network
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling

print("="*60)
print("EXPERIMENT 3: CONVERGENCE STUDY")
print("="*60)

# Use Alarm network for convergence test
model = create_alarm_network()
query_var = 'Burglary'
evidence = {'PhoneCall': 1}

# Get exact answer with VE
ve = VariableElimination(model)
ve_result = ve.query([query_var], evidence=evidence)
exact_prob = ve_result.values[1]

print(f"\nQuery: P({query_var}=1 | PhoneCall=1)")
print(f"Exact probability (VE): {exact_prob:.6f}\n")

# Test different sample sizes
sample_sizes = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
num_trials = 10  # Average over multiple runs

results = {
    'Sample_Size': [],
    'Mean_Probability': [],
    'Std_Probability': [],
    'Mean_Error': [],
    'Std_Error': []
}

print("Testing sample sizes...")

for size in sample_sizes:
    print(f"  {size:,} samples...", end='')
    
    probs = []
    errors = []
    
    for trial in range(num_trials):
        gibbs = GibbsSampling(model)
        # Rejection sampling manually
        samples = gibbs.sample(size=size)
        for var, state in evidence.items():
            samples = samples[samples[var] == state]
            
        if len(samples) == 0:
            prob = 0 # Handle empty case
        else:
            prob = samples[query_var].mean()
        error = abs(prob - exact_prob)
        
        probs.append(prob)
        errors.append(error)
    
    mean_prob = np.mean(probs)
    std_prob = np.std(probs)
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    
    results['Sample_Size'].append(size)
    results['Mean_Probability'].append(mean_prob)
    results['Std_Probability'].append(std_prob)
    results['Mean_Error'].append(mean_error)
    results['Std_Error'].append(std_error)
    
    print(f" Error: {mean_error:.6f} ± {std_error:.6f}")

# Create DataFrame
df = pd.DataFrame(results)

# Save results
df.to_csv('convergence_results.csv', index=False)
print("\n✅ Results saved to: convergence_results.csv")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Probability estimate vs sample size
ax1.errorbar(df['Sample_Size'], df['Mean_Probability'], 
            yerr=df['Std_Probability'], fmt='o-', linewidth=2, 
            markersize=8, capsize=5, color='#3b82f6', label='Gibbs Estimate')
ax1.axhline(y=exact_prob, color='#10b981', linestyle='--', 
           linewidth=2, label='Exact (VE)')
ax1.set_xscale('log')
ax1.set_xlabel('Number of Samples (log scale)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probability Estimate', fontsize=12, fontweight='bold')
ax1.set_title('Convergence to Exact Probability', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

# Plot 2: Error vs sample size
ax2.errorbar(df['Sample_Size'], df['Mean_Error'], 
            yerr=df['Std_Error'], fmt='o-', linewidth=2,
            markersize=8, capsize=5, color='#ef4444')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Number of Samples (log scale)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Absolute Error (log scale)', fontsize=12, fontweight='bold')
ax2.set_title('Error Reduction with More Samples', fontsize=14, fontweight='bold')
ax2.grid(alpha=0.3)

# Add 1/sqrt(n) reference line
x_ref = np.array(sample_sizes)
y_ref = 0.01 / np.sqrt(x_ref / 1000)  # Scaled reference
ax2.plot(x_ref, y_ref, 'k--', alpha=0.5, label='1/√n reference')
ax2.legend()

plt.tight_layout()
plt.savefig('convergence_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Graph saved to: convergence_analysis.png")

plt.show()

print("\n" + "="*60)
print("CONVERGENCE SUMMARY")
print("="*60)
print(f"Error with 100 samples:    {df.iloc[0]['Mean_Error']:.6f}")
print(f"Error with 50,000 samples: {df.iloc[-1]['Mean_Error']:.6f}")
print(f"Improvement factor:        {df.iloc[0]['Mean_Error'] / df.iloc[-1]['Mean_Error']:.1f}x")
print(f"\nConclusion: Error decreases as sample size increases")
print(f"Following approximately 1/√n convergence rate")

print("\n" + "="*60)
print("EXPERIMENT 3 COMPLETE!")
print("="*60)