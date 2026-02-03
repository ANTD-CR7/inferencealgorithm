"""
Run inference on Alarm Network
Compare Variable Elimination vs Gibbs Sampling
"""

from alarm_network import create_alarm_network
from pgmpy.inference import VariableElimination
from pgmpy.sampling import GibbsSampling
import time

print("="*60)
print("BAYESIAN NETWORK INFERENCE DEMO")
print("="*60)

# Create network
print("\n1. Creating Alarm Network...")
model = create_alarm_network()

print("\n2. Setting up inference engines...")
ve = VariableElimination(model)
gibbs = GibbsSampling(model)

print("\n" + "="*60)
print("QUERY: P(Burglary | PhoneCall = True)")
print("="*60)

# Variable Elimination
print("\n🔍 Running Variable Elimination (Exact)...")
start = time.time()
result_ve = ve.query(variables=['Burglary'], evidence={'PhoneCall': 1})
ve_time = time.time() - start

print(result_ve)
print(f"Time: {ve_time:.6f} seconds")


# Gibbs Sampling (filtering evidence after sampling)
print("\n🎲 Running Gibbs Sampling (Approximate)...")
try:
	start = time.time()
	samples = gibbs.sample(size=10000)
	gibbs_time = time.time() - start
	# Filter samples where PhoneCall == 1 (True)
	filtered = samples[samples['PhoneCall'] == 1]
	if len(filtered) == 0:
		print("No samples found with PhoneCall = True. Cannot estimate P(Burglary | PhoneCall=True).")
		prob_burglary_true = float('nan')
	else:
		prob_burglary_true = filtered['Burglary'].mean()
		print(f"\nP(Burglary=0 | PhoneCall=1) = {1-prob_burglary_true:.4f}")
		print(f"P(Burglary=1 | PhoneCall=1) = {prob_burglary_true:.4f}")
	print(f"Time: {gibbs_time:.6f} seconds")
except Exception as e:
	print(f"Gibbs Sampling failed: {e}")
	prob_burglary_true = float('nan')

# Comparison
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
ve_prob = result_ve.values[1]
if not (prob_burglary_true != prob_burglary_true):  # check for nan
	diff = abs(ve_prob - prob_burglary_true)
	print(f"VE:    P(Burglary=1) = {ve_prob:.6f}")
	print(f"Gibbs: P(Burglary=1) = {prob_burglary_true:.6f}")
	print(f"Difference: {diff:.6f}")
	print(f"Speedup: VE was {gibbs_time/ve_time:.1f}x faster")
else:
	print("Gibbs Sampling did not produce a valid estimate.")

print("\n✅ Inference complete!")