import pickle
import pandas as pd

# Load model
with open('ml_engine/student_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Sample student data
sample = pd.DataFrame([{
    'attendance': 60,
    'internal': 55,
    'mid': 52,
    'previous': 6.2,
    'engagement': 50
}])

# Predict
score = model.predict(sample)[0]

# Risk logic
if score >= 75:
    risk = 'Low'
elif score >= 50:
    risk = 'Medium'
else:
    risk = 'High'

print("Predicted Score:", score)
print("Risk Level:", risk)
