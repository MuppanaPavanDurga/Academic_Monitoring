import sys
import os

# Add the project root to sys.path so we can import students.services
sys.path.append(os.getcwd())

try:
    from students.services.xai_engine import explain_risk_prediction
    
    # Dummy features: [CGPA, Attendance %, Failed Subjects, Mid Avg, Total Subjects]
    # Example values
    dummy_features = [8.5, 90.0, 0, 20.0, 5]
    
    print("Attempting to explain risk prediction...")
    explanation = explain_risk_prediction(dummy_features)
    
    if explanation:
        print("Success! Explanation generated:")
        print(explanation)
    else:
        print("Result was None. Check if model file exists or logic returned None.")

except Exception as e:
    print("Caught exception during XAI execution:")
    print(e)
    import traceback
    traceback.print_exc()
