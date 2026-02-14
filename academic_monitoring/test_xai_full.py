import sys
import os

sys.path.append(os.getcwd())
sys.stdout = open("full_xai_test_log.txt", "w", encoding="utf-8")

try:
    from students.services.xai_messages import generate_risk_message
    
    print("=== XAI FULL TEST ===\n")

    # Case 1: LOW RISK (Good Student)
    # Positive SHAP = Strength
    low_risk_expl = {'CGPA': 0.15, 'Attendance %': 0.08, 'Failed Subjects': 0.01}
    msg_low = generate_risk_message("LOW", low_risk_expl)
    print(f"[LOW RISK]\nInput: {low_risk_expl}\nOutput: {msg_low}\n")
    
    # Case 2: HIGH RISK (Bad Student)
    # Positive SHAP = Risk Factor
    high_risk_expl = {'CGPA': 0.25, 'Failed Subjects': 0.12, 'Attendance %': -0.05}
    msg_high = generate_risk_message("HIGH", high_risk_expl)
    print(f"[HIGH RISK]\nInput: {high_risk_expl}\nOutput: {msg_high}\n")

    # Case 3: MEDIUM RISK (The Problem Case)
    # Smaller values, mixed signals
    medium_risk_expl = {'CGPA': 0.04, 'Attendance %': -0.03, 'Mid Avg': 0.025}
    msg_med = generate_risk_message("MEDIUM", medium_risk_expl)
    print(f"[MEDIUM RISK]\nInput: {medium_risk_expl}\nOutput: {msg_med}\n")

    # Case 4: EMPTY/NEUTRAL (Should have fallback)
    neutral_expl = {'CGPA': 0.001, 'Attendance %': 0.002}
    msg_neut = generate_risk_message("MEDIUM", neutral_expl)
    print(f"[NEUTRAL/MEDIUM]\nInput: {neutral_expl}\nOutput: {msg_neut}\n")

except Exception as e:
    print(f"ERROR: {e}")
