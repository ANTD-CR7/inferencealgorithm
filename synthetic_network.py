"""
SIMPLE SYNTHETIC NETWORK
Custom 3-variable chain for testing

Structure:
  Rain → Traffic → Late

Simple cause-effect chain:
- Rain causes Traffic
- Traffic causes being Late
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD

def create_synthetic_network():
    """Create and return simple synthetic network"""
    
    # Define structure (simple chain)
    model = DiscreteBayesianNetwork([
        ('Rain', 'Traffic'),
        ('Traffic', 'Late')
    ])
    
    # CPT for Rain (no parents)
    # P(Rain=No) = 0.7, P(Rain=Yes) = 0.3
    cpd_rain = TabularCPD(
        variable='Rain',
        variable_card=2,
        values=[[0.7], [0.3]]
    )
    
    # CPT for Traffic (parent: Rain)
    # Columns: (Rain=No), (Rain=Yes)
    cpd_traffic = TabularCPD(
        variable='Traffic',
        variable_card=2,
        values=[
            [0.8, 0.2],   # P(Traffic=Light | Rain)
            [0.2, 0.8]    # P(Traffic=Heavy | Rain)
        ],
        evidence=['Rain'],
        evidence_card=[2]
    )
    
    # CPT for Late (parent: Traffic)
    # Columns: (Traffic=Light), (Traffic=Heavy)
    cpd_late = TabularCPD(
        variable='Late',
        variable_card=2,
        values=[
            [0.9, 0.1],   # P(Late=No | Traffic)
            [0.1, 0.9]    # P(Late=Yes | Traffic)
        ],
        evidence=['Traffic'],
        evidence_card=[2]
    )
    
    # Add CPTs
    model.add_cpds(cpd_rain, cpd_traffic, cpd_late)
    
    # Verify
    assert model.check_model(), "Model is invalid!"
    
    print("✅ Synthetic Network created!")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))
    
    return model


# Test it

if __name__ == "__main__":
    import sys
    import ast
    network = create_synthetic_network()
    print("\n🎉 Synthetic Network ready!")

    from pgmpy.inference import VariableElimination
    ve = VariableElimination(network)

    # Usage instructions
    print("\nUsage:")
    print("  python notepad_synthetic_network.py [query_var] [evidence_dict]")
    print("  Example: python notepad_synthetic_network.py Late '{\"Rain\": 1}'\n")

    # Parse command-line arguments
    if len(sys.argv) > 1:
        query_var = sys.argv[1]
        evidence = ast.literal_eval(sys.argv[2]) if len(sys.argv) > 2 else None
        print(f"QUERY: P({query_var} | {evidence if evidence else 'no evidence'})")
        try:
            result = ve.query(variables=[query_var], evidence=evidence)
            print(result)
        except Exception as e:
            print(f"Error during inference: {e}")
    else:
        # Default example
        print("QUERY: P(Late | Rain=1)")
        result = ve.query(variables=['Late'], evidence={'Rain': 1})
        print(result)