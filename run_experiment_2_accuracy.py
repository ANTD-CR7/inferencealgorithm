"""
EXPERIMENT 2: Accuracy Comparison
Measures Mean Absolute Error (MAE) of Gibbs Sampling vs Exact Inference (VE).
"""

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from experiment_utils import (
    get_all_networks, 
    get_network_queries, 
    run_exact_inference, 
    run_gibbs_inference,
    setup_plot_style,
    save_plot,
    save_results
)

def main():
    parser = argparse.ArgumentParser(description="Run Experiment 2: Accuracy Comparison")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials per network")
    parser.add_argument("--samples", type=int, default=10000, help="Number of samples for Gibbs")
    args = parser.parse_args()

    print("="*60)
    print(f"EXPERIMENT 2: ACCURACY COMPARISON (Trials={args.trials}, Samples={args.samples})")
    print("="*60)

    networks = get_all_networks()
    queries = get_network_queries()
    
    results = {
        'Network': [],
        'Variables': [],
        'VE_Prob': [],
        'Gibbs_Prob_Mean': [],
        'MAE': [],
        'Error_Std': []
    }

    for network_name, model in networks.items():
        print(f"Testing: {network_name}")
        query_var, evidence, target_state = queries[network_name]
        
        # 1. Exact Inference
        ve_prob = run_exact_inference(model, query_var, evidence, target_state)
        print(f"  Exact Probability (VE): {ve_prob:.4f}")
        
        # 2. Approximate Inference
        probs = []
        errors = []
        for _ in range(args.trials):
            gibbs_prob, _ = run_gibbs_inference(model, query_var, evidence, args.samples, target_state)
            probs.append(gibbs_prob)
            errors.append(abs(ve_prob - gibbs_prob))
            
        gibbs_mean = np.mean(probs)
        mae = np.mean(errors)
        error_std = np.std(errors)
        
        results['Network'].append(network_name)
        results['Variables'].append(len(model.nodes()))
        results['VE_Prob'].append(ve_prob)
        results['Gibbs_Prob_Mean'].append(gibbs_mean)
        results['MAE'].append(mae)
        results['Error_Std'].append(error_std)
        
        print(f"  Gibbs Mean Prob: {gibbs_mean:.4f}")
        print(f"  MAE: {mae:.4f} ± {error_std:.4f}\n")

    # Save Results
    df = pd.DataFrame(results)
    save_results(df, 'accuracy_results.csv')

    # Plotting
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(df))
    bars = ax.bar(x, df['MAE'], yerr=df['Error_Std'], color='#ef4444', alpha=0.8, capsize=5, edgecolor='black')
    
    ax.set_ylabel('Mean Absolute Error (MAE)')
    ax.set_title(f'Gibbs Sampling Accuracy (vs VE) - {args.samples} samples')
    ax.set_xticks(x)
    ax.set_xticklabels(df['Network'])
    
    # Value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.4f}', ha='center', va='bottom', fontsize=10)
    
    save_plot('accuracy_comparison.png')
    print("\nExperiment 2 Complete!")

if __name__ == "__main__":
    main()
