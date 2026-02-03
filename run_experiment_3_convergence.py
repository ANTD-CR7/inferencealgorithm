"""
EXPERIMENT 3: Convergence Study
Tests how Gibbs accuracy improves with increasing sample size.
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from experiment_utils import (
    create_alarm_network, 
    run_exact_inference, 
    run_gibbs_inference,
    setup_plot_style,
    save_plot,
    save_results
)

def main():
    parser = argparse.ArgumentParser(description="Run Experiment 3: Convergence Study")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials per sample size")
    args = parser.parse_args()

    print("="*60)
    print(f"EXPERIMENT 3: CONVERGENCE STUDY (Trials={args.trials})")
    print("="*60)

    # Use Alarm network
    model = create_alarm_network()
    query_var = 'Burglary'
    evidence = {'PhoneCall': 1}
    target_state = 1
    
    # 1. Exact Answer
    exact_prob = run_exact_inference(model, query_var, evidence, target_state)
    print(f"\nExact Probability (P({query_var}=1 | {evidence})): {exact_prob:.6f}\n")
    
    # 2. Test sample sizes
    sample_sizes = [100, 500, 1000, 2500, 5000, 10000, 25000]
    
    results = {
        'Sample_Size': [], 'Mean_Probability': [], 'Std_Probability': [],
        'Mean_Error': [], 'Std_Error': []
    }
    
    print("Testing sample sizes...")
    for size in sample_sizes:
        print(f"  {size:,} samples...", end='', flush=True)
        
        probs = []
        errors = []
        
        for _ in range(args.trials):
            prob, _ = run_gibbs_inference(model, query_var, evidence, size, target_state)
            probs.append(prob)
            errors.append(abs(prob - exact_prob))
            
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
        
    # Save Results
    df = pd.DataFrame(results)
    save_results(df, 'convergence_results.csv')
    
    # Plotting
    setup_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Probability vs Samples
    ax1.errorbar(df['Sample_Size'], df['Mean_Probability'], yerr=df['Std_Probability'], 
                 fmt='o-', linewidth=2, markersize=8, capsize=5, label='Gibbs Estimate', color='#3b82f6')
    ax1.axhline(y=exact_prob, color='#10b981', linestyle='--', linewidth=2, label='Exact (VE)')
    ax1.set_xscale('log')
    ax1.set_xlabel('Number of Samples (log scale)')
    ax1.set_ylabel('Probability Estimate')
    ax1.set_title('Convergence to Exact Probability')
    ax1.legend()
    
    # Plot 2: Error vs Samples
    ax2.errorbar(df['Sample_Size'], df['Mean_Error'], yerr=df['Std_Error'], 
                 fmt='o-', linewidth=2, markersize=8, capsize=5, color='#ef4444')
    
    # Reference line 1/sqrt(n)
    x_ref = np.array(sample_sizes)
    y_ref = 0.01 / np.sqrt(x_ref / 1000) 
    ax2.plot(x_ref, y_ref, 'k--', alpha=0.5, label='1/√n reference')
    
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Number of Samples (log scale)')
    ax2.set_ylabel('Absolute Error (log scale)')
    ax2.set_title('Error Reduction')
    ax2.legend()
    
    save_plot('convergence_analysis.png')
    print("\nExperiment 3 Complete!")

if __name__ == "__main__":
    main()
