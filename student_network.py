"""
STUDENT BAYESIAN NETWORK
Standard benchmark from Koller & Friedman textbook

Structure:
  Difficulty → Grade ← Intelligence
  Intelligence → SAT
  Grade → Letter

Variables:
  D = Difficulty (of course)
  I = Intelligence (of student)
  G = Grade (in course)
  S = SAT (score)
  L = Letter (recommendation)
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD

def create_student_network():
    """Create and return Student Network"""
    
    # Define structure
    model = DiscreteBayesianNetwork([
        ('Difficulty', 'Grade'),
        ('Intelligence', 'Grade'),
        ('Intelligence', 'SAT'),
        ('Grade', 'Letter')
    ])
    
    # CPT for Difficulty (no parents)
    # P(Difficulty=Easy) = 0.6, P(Difficulty=Hard) = 0.4
    cpd_difficulty = TabularCPD(
        variable='Difficulty',
        variable_card=2,
        values=[[0.6], [0.4]]
    )
    
    # CPT for Intelligence (no parents)
    # P(Intelligence=Low) = 0.7, P(Intelligence=High) = 0.3
    cpd_intelligence = TabularCPD(
        variable='Intelligence',
        variable_card=2,
        values=[[0.7], [0.3]]
    )
    
    # CPT for Grade (parents: Difficulty, Intelligence)
    # Columns: (D=0,I=0), (D=0,I=1), (D=1,I=0), (D=1,I=1)
    # 0 = Low/Easy, 1 = High/Hard
    cpd_grade = TabularCPD(
        variable='Grade',
        variable_card=3,  # 3 grades: A, B, C
        values=[
            [0.3, 0.05, 0.9, 0.5],   # P(Grade=A | D, I)
            [0.4, 0.25, 0.08, 0.3],  # P(Grade=B | D, I)
            [0.3, 0.7, 0.02, 0.2]    # P(Grade=C | D, I)
        ],
        evidence=['Difficulty', 'Intelligence'],
        evidence_card=[2, 2]
    )
    
    # CPT for SAT (parent: Intelligence)
    cpd_sat = TabularCPD(
        variable='SAT',
        variable_card=2,  # High or Low
        values=[
            [0.95, 0.2],   # P(SAT=Low | Intelligence)
            [0.05, 0.8]    # P(SAT=High | Intelligence)
        ],
        evidence=['Intelligence'],
        evidence_card=[2]
    )
    
    # CPT for Letter (parent: Grade)
    cpd_letter = TabularCPD(
        variable='Letter',
        variable_card=2,  # Good or Bad
        values=[
            [0.1, 0.4, 0.99],   # P(Letter=Bad | Grade=A/B/C)
            [0.9, 0.6, 0.01]    # P(Letter=Good | Grade=A/B/C)
        ],
        evidence=['Grade'],
        evidence_card=[3]
    )
    
    # Add all CPTs
    model.add_cpds(
        cpd_difficulty,
        cpd_intelligence,
        cpd_grade,
        cpd_sat,
        cpd_letter
    )
    
    # Verify
    assert model.check_model(), "Model is invalid!"
    
    print("✅ Student Network created!")
    print("   Variables:", list(model.nodes()))
    print("   Edges:", list(model.edges()))
    
    return model


# Test it
if __name__ == "__main__":
    import sys
    import ast
    network = create_student_network()
    print("\n🎉 Student Network ready!")

    from pgmpy.inference import VariableElimination
    ve = VariableElimination(network)

    # Usage instructions
    print("\nUsage:")
    print("  python notepad_student_network.py [query_var] [evidence_dict]")
    print("  Example: python notepad_student_network.py Intelligence '{\"Letter\": 1}'\n")

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
        print("QUERY: P(Intelligence | Letter=Good)")
        result = ve.query(variables=['Intelligence'], evidence={'Letter': 1})
        print(result)