from django.db import models
from students.models import StudentProfile

class PredictionResult(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    risk_level = models.CharField(max_length=10)
    prediction_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
