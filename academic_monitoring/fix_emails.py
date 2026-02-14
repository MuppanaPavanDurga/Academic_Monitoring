
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_monitoring.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import StudentProfile

print("Starting email sync...")
count = 0
students = StudentProfile.objects.all()

for student in students:
    user = student.user
    # If StudentProfile has email but User does not, or they differ
    if student.email and user.email != student.email:
        print(f"Updating {user.username}: {user.email} -> {student.email}")
        user.email = student.email
        user.save()
        count += 1

print(f"Successfully synced {count} student emails to User model.")
