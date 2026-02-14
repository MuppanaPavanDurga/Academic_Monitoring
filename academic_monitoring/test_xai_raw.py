import sys
import os

sys.path.append(os.getcwd())

# Redirect stdout to file
sys.stdout = open("clean_log.txt", "w", encoding="utf-8")

try:
    from students.services.xai_engine import explain_risk_prediction
    from students.services.ml_risk_engine import predict_academic_risk_ml
    
    # Feature Order: [CGPA, Attendance %, Failed Subjects, Mid Avg, Total Subjects]

    # 1. Good Student (Should be LOW RISK)
    good_student = [9.5, 95.0, 0, 24.0, 5]
    print("\n--- GOOD STUDENT ---")
    risk, prob = predict_academic_risk_ml(good_student)
    print(f"Prediction: {risk} (Prob: {prob})")
    
    explanation = explain_risk_prediction(good_student)
    print("Explanation:", explanation)
    
    # 2. Bad Student (Should be HIGH RISK)
    bad_student = [4.0, 50.0, 3, 10.0, 5]
    print("\n--- BAD STUDENT ---")
    risk, prob = predict_academic_risk_ml(bad_student)
    print(f"Prediction: {risk} (Prob: {prob})")
    
    explanation = explain_risk_prediction(bad_student)
    print("Explanation:", explanation)

except Exception as e:
    print(e)
