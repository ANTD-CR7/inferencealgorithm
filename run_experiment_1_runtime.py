"""
EXPERIMENT 1: Runtime Comparison
Measures execution time of VE vs Gibbs across different networks.
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
import time
from pgmpy.inference import VariableElimination

def main():
    parser = argparse.ArgumentParser(description="Run Experiment 1: Runtime Comparison")
    parser.add_argument("--trials", type=int, default=10, help="Number of trials per network")
    parser.add_argument("--samples", type=int, default=10000, help="Number of samples for Gibbs")
    args = parser.parse_args()

    print("="*60)
    print(f"EXPERIMENT 1: RUNTIME COMPARISON (Trials={args.trials}, Samples={args.samples})")
    print("="*60)

    networks = get_all_networks()
    queries = get_network_queries()
    
    results = {
        'Network': [],
        'Variables': [],
        'VE_Time_Mean': [],
        'VE_Time_Std': [],
        'Gibbs_Time_Mean': [],
        'Gibbs_Time_Std': [],
        'Speedup': []
    }

    for network_name, model in networks.items():
        print(f"Testing: {network_name}")
        query_var, evidence, target_state = queries[network_name]
        
        # 1. Variable Elimination Timing
        ve_times = []
        for _ in range(args.trials):
            start = time.time()
            ve = VariableElimination(model)
            ve.query([query_var], evidence=evidence, show_progress=False)
            ve_times.append(time.time() - start)
            
        # 2. Gibbs Sampling Timing
        gibbs_times = []
        for _ in range(args.trials):
            _, duration = run_gibbs_inference(model, query_var, evidence, args.samples, target_state)
            gibbs_times.append(duration)
            
        # Statistics
        ve_mean = np.mean(ve_times)
        ve_std = np.std(ve_times)
        gibbs_mean = np.mean(gibbs_times)
        gibbs_std = np.std(gibbs_times)
        speedup = gibbs_mean / ve_mean if ve_mean > 0 else 0
        
        results['Network'].append(network_name)
        results['Variables'].append(len(model.nodes()))
        results['VE_Time_Mean'].append(ve_mean)
        results['VE_Time_Std'].append(ve_std)
        results['Gibbs_Time_Mean'].append(gibbs_mean)
        results['Gibbs_Time_Std'].append(gibbs_std)
        results['Speedup'].append(speedup)
        
        print(f"  VE:    {ve_mean*1000:.2f} ± {ve_std*1000:.2f} ms")
        print(f"  Gibbs: {gibbs_mean*1000:.2f} ± {gibbs_std*1000:.2f} ms")
        print(f"  Speedup: {speedup:.1f}x (Gibbs is slower)" if speedup > 1 else f"  Speedup: {1/speedup:.1f}x (Gibbs is faster)")
        print()

    # Save Results
    df = pd.DataFrame(results)
    save_results(df, 'runtime_results.csv')

    # Plotting
    setup_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Execution Time
    x = np.arange(len(df))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, df['VE_Time_Mean']*1000, width, label='Variable Elimination', color='#3b82f6')
    bars2 = ax1.bar(x + width/2, df['Gibbs_Time_Mean']*1000, width, label='Gibbs Sampling', color='#8b5cf6')
    
    ax1.set_ylabel('Execution Time (ms)')
    ax1.set_title('Runtime Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Variables'])
    ax1.set_xlabel('Network Size (Variables)')
    ax1.legend()
    
    # Plot 2: Speedup
    ax2.bar(df['Variables'], df['Speedup'], color='#10b981', edgecolor='black')
    ax2.axhline(y=1, color='red', linestyle='--')
    ax2.set_ylabel('Ratio (Gibbs Time / VE Time)')
    ax2.set_title('Relative Performance (Higher = VE Faster)')
    ax2.set_xlabel('Network Size (Variables)')
    
    save_plot('runtime_comparison.png')
    print("\nExperiment 1 Complete!")

if __name__ == "__main__":
    main()
