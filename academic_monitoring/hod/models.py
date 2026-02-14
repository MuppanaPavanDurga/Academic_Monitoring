from django.db import models
from students.models import StudentProfile
from faculty.models import FacultyProfile

from django.db import models
from django.contrib.auth.models import User


class HODProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.department}"

class FacultyAssignment(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.roll_no} → {self.faculty.user.username}"
import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, Semester, SubjectMark


@login_required
@role_required(["HOD"])
def upload_marks_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
        reader = csv.reader(csv_file)
        header = next(reader)

        semester_idx = header.index("Semester")
        roll_idx = header.index("RollNO")
        cgpa_idx = header.index("CGPA")
        actual_credits_idx = header.index("ActualCredits")
        acquired_credits_idx = header.index("AcquiredCredits")
        result_idx = header.index("Result")

        # Subjects are between Name and ActualCredits
        subject_columns = header[3:actual_credits_idx]

        for row in reader:
            semester_no = int(row[semester_idx])
            roll_no = row[roll_idx]
            cgpa = float(row[cgpa_idx])

            student = StudentProfile.objects.get(roll_no=roll_no)

            semester, _ = Semester.objects.update_or_create(
                student=student,
                semester_no=semester_no,
                defaults={
                    "cgpa": cgpa,
                    "actual_credits": int(row[actual_credits_idx]),
                    "acquired_credits": int(row[acquired_credits_idx]),
                    "result": row[result_idx],
                }
            )

            # Clear old subject data
            SubjectMark.objects.filter(semester=semester).delete()

            for i, subject in enumerate(subject_columns):
                SubjectMark.objects.create(
                    semester=semester,
                    subject_name=subject,
                    grade=row[3 + i]
                )

        return redirect("upload_marks_csv")

    return render(request, "hod/upload_marks_csv.html")
