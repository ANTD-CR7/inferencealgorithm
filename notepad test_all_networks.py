"""
Test all three networks work correctly
"""


import time
import random
import itertools
from alarm_network import create_alarm_network
from student_network import create_student_network
from synthetic_network import create_synthetic_network
from pgmpy.inference import VariableElimination

print("="*60)
print("TESTING ALL NETWORKS")
print("="*60)

# Test 1: Alarm Network


print("\n1. Testing Alarm Network...")
alarm = create_alarm_network()
ve_alarm = VariableElimination(alarm)
alarm_tests = [
	(['Burglary'], {'PhoneCall': 1}),
	(['Alarm'], {'Burglary': 1, 'Earthquake': 0}),
	(['PhoneCall'], {'Alarm': 1}),
	(['Alarm'], {'Burglary': 0, 'Earthquake': 1}),
]
alarm_results = []
for query_vars, evidence in alarm_tests:
	try:
		start = time.time()
		result = ve_alarm.query(query_vars, evidence=evidence)
		elapsed = time.time() - start
		alarm_results.append((query_vars, evidence, result.values, elapsed, None))
		print(f"   Query: P({query_vars} | {evidence})")
		print(f"   Result: {result.values} (Time: {elapsed:.4f}s)")
	except Exception as e:
		alarm_results.append((query_vars, evidence, None, 0, str(e)))
		print(f"   Query: P({query_vars} | {evidence}) FAILED: {e}")

# Random evidence test for Alarm Network
try:
	rand_evidence = {'Burglary': random.choice([0,1]), 'Earthquake': random.choice([0,1])}
	start = time.time()
	result = ve_alarm.query(['Alarm'], evidence=rand_evidence)
	elapsed = time.time() - start
	print(f"   Random Query: P(['Alarm'] | {rand_evidence}) = {result.values} (Time: {elapsed:.4f}s)")
except Exception as e:
	print(f"   Random Query FAILED: {e}")

# Test 2: Student Network


print("\n2. Testing Student Network...")
student = create_student_network()
ve_student = VariableElimination(student)
student_tests = [
	(['Intelligence'], {'SAT': 1}),
	(['Grade'], {'Intelligence': 1, 'Difficulty': 0}),
	(['Letter'], {'Grade': 2}),
	(['SAT'], {'Intelligence': 0}),
]
student_results = []
for query_vars, evidence in student_tests:
	try:
		start = time.time()
		result = ve_student.query(query_vars, evidence=evidence)
		elapsed = time.time() - start
		student_results.append((query_vars, evidence, result.values, elapsed, None))
		print(f"   Query: P({query_vars} | {evidence})")
		print(f"   Result: {result.values} (Time: {elapsed:.4f}s)")
	except Exception as e:
		student_results.append((query_vars, evidence, None, 0, str(e)))
		print(f"   Query: P({query_vars} | {evidence}) FAILED: {e}")

# Edge case: Impossible evidence
try:
	result = ve_student.query(['Grade'], evidence={'Intelligence': 1, 'Difficulty': 0, 'SAT': 0, 'Letter': 1})
	print(f"   Edge Case Query: P(['Grade'] | Intelligence=1, Difficulty=0, SAT=0, Letter=1) = {result.values}")
except Exception as e:
	print(f"   Edge Case Query FAILED: {e}")

# Test 3: Synthetic Network


print("\n3. Testing Synthetic Network...")
synthetic = create_synthetic_network()
ve_synthetic = VariableElimination(synthetic)
synthetic_tests = [
	(['Rain'], {'Late': 1}),
	(['Late'], {'Rain': 1}),
	(['Traffic'], {'Rain': 1}),
	(['Traffic'], {'Late': 0}),
]
synthetic_results = []
for query_vars, evidence in synthetic_tests:
	try:
		start = time.time()
		result = ve_synthetic.query(query_vars, evidence=evidence)
		elapsed = time.time() - start
		synthetic_results.append((query_vars, evidence, result.values, elapsed, None))
		print(f"   Query: P({query_vars} | {evidence})")
		print(f"   Result: {result.values} (Time: {elapsed:.4f}s)")
	except Exception as e:
		synthetic_results.append((query_vars, evidence, None, 0, str(e)))
		print(f"   Query: P({query_vars} | {evidence}) FAILED: {e}")

# Random evidence test for Synthetic Network
try:
	rand_evidence = {'Rain': random.choice([0,1]), 'Late': random.choice([0,1])}
	start = time.time()
	result = ve_synthetic.query(['Traffic'], evidence=rand_evidence)
	elapsed = time.time() - start
	print(f"   Random Query: P(['Traffic'] | {rand_evidence}) = {result.values} (Time: {elapsed:.4f}s)")
except Exception as e:
	print(f"   Random Query FAILED: {e}")



# Summary Table
print("\n" + "="*60)
print("SUMMARY TABLE")
print("="*60)
def print_summary(results, name):
	print(f"\n{name} Results:")
	for qvars, evidence, values, elapsed, err in results:
		if err:
			print(f"  Query: P({qvars} | {evidence}) FAILED: {err}")
		else:
			print(f"  Query: P({qvars} | {evidence}) = {values} (Time: {elapsed:.4f}s)")
print_summary(alarm_results, "Alarm Network")
print_summary(student_results, "Student Network")
print_summary(synthetic_results, "Synthetic Network")
print("\nAll advanced tests completed. If no errors above, all networks are robust and queries are producing results.")
print("="*60)