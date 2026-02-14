import sys
import os

sys.path.append(os.getcwd())

# Redirect stdout to file
sys.stdout = open("clean_test_log.txt", "w", encoding="utf-8")

try:
    from students.services.xai_messages import generate_risk_message
    
    # Case 1: LOW RISK
    # Positive SHAP for 'CGPA' -> Should be 'Good Grades'
    # Negative SHAP for 'Attendance %' -> Should be 'Low Attendance'
    risk_level = "LOW"
    explanation = {'CGPA': 0.2, 'Attendance %': -0.1} 
    
    print(f"\n--- Testing LOW Risk ---")
    msg = generate_risk_message(risk_level, explanation)
    print(f"Result: {msg}")
    
    # Case 2: HIGH RISK
    # Positive SHAP for 'CGPA' -> Should be 'Low Grades' (Risk Factor)
    # Negative SHAP for 'Attendance %' -> Should be 'High Attendance' (Mitigating)
    risk_level = "HIGH"
    explanation = {'CGPA': 0.2, 'Attendance %': -0.1}
    
    print(f"\n--- Testing HIGH Risk ---")
    msg = generate_risk_message(risk_level, explanation)
    print(f"Result: {msg}")

except Exception as e:
    print(e)
