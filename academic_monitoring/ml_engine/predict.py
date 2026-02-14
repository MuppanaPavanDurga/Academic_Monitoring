import pickle
import pandas as pd
from .models import PredictionResult
from students.models import AcademicRecord

MODEL_PATH = 'ml_engine/student_model.pkl'


def predict_student_risk(student):
    # Load ML model
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    # Get latest academic record
    record = AcademicRecord.objects.filter(student=student).last()

    if not record:
        return None

    # Prepare input
    input_data = pd.DataFrame([{
        'attendance': record.attendance_percentage,
        'internal': record.internal_marks,
        'mid': record.mid_sem_marks,
        'previous': record.previous_gpa,
        'engagement': record.engagement_score
    }])

    # Predict score
    predicted_score = model.predict(input_data)[0]

    # Risk classification
    if predicted_score >= 75:
        risk = 'Low'
    elif predicted_score >= 50:
        risk = 'Medium'
    else:
        risk = 'High'

    # Save or update prediction
    PredictionResult.objects.update_or_create(
        student=student,
        defaults={
            'prediction_score': predicted_score,
            'risk_level': risk
        }
    )

    return predicted_score, risk
