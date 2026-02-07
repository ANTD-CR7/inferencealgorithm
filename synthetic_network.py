"""
Synthetic Bayesian Network
Small chain network for quick experiments.

Structure:
  Rain -> Traffic -> Late
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD


def create_synthetic_network():
    """Build and return the synthetic Bayesian network."""

    # Graph structure (simple chain)
    model = DiscreteBayesianNetwork([
        ('Rain', 'Traffic'),
        ('Traffic', 'Late')
    ])

    # CPT: Rain (no parents)
    cpd_rain = TabularCPD(
        variable='Rain',
        variable_card=2,
        values=[[0.7], [0.3]]
    )

    # CPT: Traffic (parent: Rain)
    # Columns: (Rain=No), (Rain=Yes)
    cpd_traffic = TabularCPD(
        variable='Traffic',
        variable_card=2,
        values=[[0.9, 0.3], [0.1, 0.7]],
        evidence=['Rain'],
        evidence_card=[2]
    )

    # CPT: Late (parent: Traffic)
    # Columns: (Traffic=Light), (Traffic=Heavy)
    cpd_late = TabularCPD(
        variable='Late',
        variable_card=2,
        values=[[0.9, 0.2], [0.1, 0.8]],
        evidence=['Traffic'],
        evidence_card=[2]
    )

    # Register CPTs
    model.add_cpds(cpd_rain, cpd_traffic, cpd_late)

    # Validate model
    assert model.check_model(), "Model is invalid"

    print("OK: Synthetic Network created")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))

    return model


if __name__ == "__main__":
    network = create_synthetic_network()
    print("\nOK: Network ready for inference")
