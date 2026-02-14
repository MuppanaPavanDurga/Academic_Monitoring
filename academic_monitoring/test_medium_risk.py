import sys
import os

sys.path.append(os.getcwd())

# Redirect stdout to file to avoid encoding issues
sys.stdout = open("medium_risk_log.txt", "w", encoding="utf-8")

try:
    from students.services.xai_messages import generate_risk_message
    
    # Case 1: MEDIUM RISK with "Grey Area" values
    # Values are > 0.01 (so not "Neutral") but < 0.05 (so ignored by current logic)
    risk_level = "MEDIUM"
    explanation = {
        'CGPA': 0.04,         # Just below 0.05
        'Attendance %': -0.04, # Just above -0.05
        'Failed Subjects': 0.0,
        'Mid Avg': 0.02,
        'Total Subjects': 0.0
    }
    
    print(f"\n--- Testing MEDIUM Risk (Grey Area) ---")
    msg = generate_risk_message(risk_level, explanation)
    print(f"Result: '{msg}'")
    
    if msg.strip() == "":
        print("FAIL: Returned empty message for valid Medium Risk explanation.")
    else:
        print("PASS: Got message.")

except Exception as e:
    print(e)
