import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle

# Load dataset
data = pd.read_csv('datasets/student_data.csv')

# Features and target
X = data[['attendance', 'internal', 'mid', 'previous', 'engagement']]
y = data['final_score']

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
model.fit(X, y)

# Save model
with open('ml_engine/student_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ ML Model trained and saved successfully!")
