import joblib

MODEL_PATH = "student_risk_model.pkl"

def predict_academic_risk_ml(features):
    model = joblib.load(MODEL_PATH)

    prediction = model.predict([features])[0]
    probability = max(model.predict_proba([features])[0])

    risk_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

    return risk_map[prediction], round(probability, 2)
