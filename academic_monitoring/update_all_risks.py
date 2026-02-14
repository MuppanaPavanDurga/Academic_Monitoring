import sys
import os
import django

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "academic_monitoring.settings")
django.setup()

from students.models import StudentProfile

print("Refreshing Risk for ALL Students...")
students = StudentProfile.objects.all()

for s in students:
    # Saving triggers the signal -> triggers update_student_risk -> triggers XAI
    s.save()
    print(f"Updated: {s.roll_no}")

print("\nDone! All students have fresh XAI explanations.")
