"""
Student Bayesian Network
Classic benchmark for inference algorithms.

Structure:
  Difficulty -> Grade <- Intelligence
  Intelligence -> SAT
  Grade -> Letter
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD


def create_student_network():
    """Build and return the Student Bayesian network."""

    # Graph structure (edges)
    model = DiscreteBayesianNetwork([
        ('Difficulty', 'Grade'),
        ('Intelligence', 'Grade'),
        ('Intelligence', 'SAT'),
        ('Grade', 'Letter')
    ])

    # CPT: Difficulty (no parents)
    cpd_difficulty = TabularCPD(
        variable='Difficulty',
        variable_card=2,
        values=[[0.6], [0.4]]
    )

    # CPT: Intelligence (no parents)
    cpd_intelligence = TabularCPD(
        variable='Intelligence',
        variable_card=2,
        values=[[0.7], [0.3]]
    )

    # CPT: Grade (parents: Difficulty, Intelligence)
    # Columns: (D=0,I=0), (D=0,I=1), (D=1,I=0), (D=1,I=1)
    cpd_grade = TabularCPD(
        variable='Grade',
        variable_card=3,
        values=[
            [0.3, 0.05, 0.9, 0.5],
            [0.4, 0.25, 0.08, 0.3],
            [0.3, 0.7, 0.02, 0.2]
        ],
        evidence=['Difficulty', 'Intelligence'],
        evidence_card=[2, 2]
    )

    # CPT: SAT (parent: Intelligence)
    cpd_sat = TabularCPD(
        variable='SAT',
        variable_card=2,
        values=[[0.95, 0.2], [0.05, 0.8]],
        evidence=['Intelligence'],
        evidence_card=[2]
    )

    # CPT: Letter (parent: Grade)
    cpd_letter = TabularCPD(
        variable='Letter',
        variable_card=2,
        values=[[0.1, 0.4, 0.99], [0.9, 0.6, 0.01]],
        evidence=['Grade'],
        evidence_card=[3]
    )

    # Register CPTs
    model.add_cpds(cpd_difficulty, cpd_intelligence, cpd_grade, cpd_sat, cpd_letter)

    # Validate model
    assert model.check_model(), "Model is invalid"

    print("OK: Student Network created")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))

    return model


if __name__ == "__main__":
    network = create_student_network()
    print("\nOK: Network ready for inference")
