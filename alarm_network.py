"""
ALARM BAYESIAN NETWORK
Standard benchmark for inference algorithms

Structure:
  Burglary → Alarm ← Earthquake
  Alarm → PhoneCall
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD

def create_alarm_network():
    """Create and return Alarm Network"""
    
    # Define structure (edges)
    model = DiscreteBayesianNetwork([
        ('Burglary', 'Alarm'),
        ('Earthquake', 'Alarm'),
        ('Alarm', 'PhoneCall')
    ])
    
    # CPT for Burglary (no parents)
    cpd_burglary = TabularCPD(
        variable='Burglary',
        variable_card=2,
        values=[[0.999], [0.001]]
    )
    
    # CPT for Earthquake (no parents)
    cpd_earthquake = TabularCPD(
        variable='Earthquake',
        variable_card=2,
        values=[[0.998], [0.002]]
    )
    
    # CPT for Alarm (parents: Burglary, Earthquake)
    cpd_alarm = TabularCPD(
        variable='Alarm',
        variable_card=2,
        values=[
            [0.999, 0.71, 0.06, 0.05],
            [0.001, 0.29, 0.94, 0.95]
        ],
        evidence=['Burglary', 'Earthquake'],
        evidence_card=[2, 2]
    )
    
    # CPT for PhoneCall (parent: Alarm)
    cpd_phone = TabularCPD(
        variable='PhoneCall',
        variable_card=2,
        values=[
            [0.95, 0.10],
            [0.05, 0.90]
        ],
        evidence=['Alarm'],
        evidence_card=[2]
    )
    
    # Add CPTs to model
    model.add_cpds(cpd_burglary, cpd_earthquake, cpd_alarm, cpd_phone)
    
    # Verify model
    assert model.check_model(), "Model is invalid!"
    
    print("✅ Alarm Network created!")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))
    
    return model


# Test it
if __name__ == "__main__":
    network = create_alarm_network()
    print("\n🎉 Network ready for inference!")