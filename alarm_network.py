"""
Alarm Bayesian Network
Standard benchmark for inference algorithms.

Structure:
  Burglary -> Alarm <- Earthquake
  Alarm -> PhoneCall
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD


def create_alarm_network():
    """Build and return the Alarm Bayesian network."""

    # Graph structure (edges)
    model = DiscreteBayesianNetwork([
        ('Burglary', 'Alarm'),
        ('Earthquake', 'Alarm'),
        ('Alarm', 'PhoneCall')
    ])

    # CPT: Burglary (no parents)
    cpd_burglary = TabularCPD(
        variable='Burglary',
        variable_card=2,
        values=[[0.999], [0.001]]
    )

    # CPT: Earthquake (no parents)
    cpd_earthquake = TabularCPD(
        variable='Earthquake',
        variable_card=2,
        values=[[0.998], [0.002]]
    )

    # CPT: Alarm (parents: Burglary, Earthquake)
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

    # CPT: PhoneCall (parent: Alarm)
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

    # Register CPTs with the model
    model.add_cpds(cpd_burglary, cpd_earthquake, cpd_alarm, cpd_phone)

    # Validate model consistency
    assert model.check_model(), "Model is invalid"

    print("OK: Alarm Network created")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))

    return model


if __name__ == "__main__":
    network = create_alarm_network()
    print("\nOK: Network ready for inference")
