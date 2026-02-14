import joblib
import numpy as np
import shap
import os

# Define the model path relative to this file or absolute
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_engine", "student_model.pkl")

# Feature names MUST match the training order exactly
FEATURE_NAMES = [
    "CGPA",
    "Attendance %",
    "Failed Subjects",
    "Mid Avg",
    "Total Subjects",
]

def explain_risk_prediction(features):
    """
    Generates a SHAP explanation for the given student features.
    
    Args:
        features (list): [CGPA, Attendance, Failures, Mid, Subjects]
        
    Returns:
        dict: {feature_name: shap_value}
        None: If model not found or error occurs.
    """
    try:
        if not os.path.exists(MODEL_PATH):
            print(f"XAI Error: Model not found at {MODEL_PATH}")
            return None

        # Load Model
        model = joblib.load(MODEL_PATH)

        # Prepare Input
        # Reshape to (1, n_features) as expected by sklearn/shap
        X = np.array(features, dtype=float).reshape(1, -1)

        # Create Explainer
        # TreeExplainer is suitable for Random Forest / Gradient Boosting models
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        # Note: shap_values() returns different shapes depending on model type (binary vs multiclass)
        shap_values_output = explainer.shap_values(X)
        
        # Get Predicted Class
        predicted_class = int(model.predict(X)[0])
        
        # Extract SHAP values for the specific predicted class
        # Heuristic to handle differnet shap versions/output formats
        if isinstance(shap_values_output, list):
            # Multiclass: list of arrays, one per class
            # shap_values_output[class_index][sample_index]
            class_shap_values = shap_values_output[predicted_class][0]
        elif isinstance(shap_values_output, np.ndarray) and len(shap_values_output.shape) == 3:
             # Multiclass: (samples, classes, features)
            class_shap_values = shap_values_output[0, predicted_class, :]
        else:
            # Binary/Regression: (samples, features)
            # For boolean binary, usually it returns the log-odds for class 1
            class_shap_values = shap_values_output[0]

        # Construct Dictionary
        explanation = {}
        for i, name in enumerate(FEATURE_NAMES):
            if i < len(class_shap_values):
                # Round for checking, but keep precision reasonable
                explanation[name] = round(float(class_shap_values[i]), 4)
            else:
                explanation[name] = 0.0

        return explanation

    except Exception as e:
        print(f"XAI Engine Error: {e}")
        import traceback
        traceback.print_exc()
        return None
