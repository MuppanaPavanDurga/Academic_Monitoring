from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    email = models.CharField(max_length=30)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    is_graduated = models.BooleanField(default=False)


    @property
    def current_semester(self):
        """
        Returns the student's latest semester object.
        """
        # Avoid circular import by importing inside method if needed, 
        # but Semester is in same app (though defined below). 
        # Models defined below cannot be referenced directly by class name if not string.
        # But 'Semester' is defined in this file. 
        # We can use "Semester" string or method approach.
        return self.semester_set.order_by("-semester_no").first()

    @property
    def pursuing_year(self):
        """
        Returns the pursuing year based on the current semester.
        """
        if self.is_graduated:
            return "Graduated"

        latest_sem = self.current_semester

        if not latest_sem:
            return "Not Started"
        
        sem = latest_sem.semester_no
        
        if sem in [1, 2]:
            return "1st Year"
        elif sem in [3, 4]:
            return "2nd Year"
        elif sem in [5, 6]:
            return "3rd Year"
        elif sem in [7, 8]:
            return "4th Year"
        else:
            return "Completed"


    def __str__(self):
        return self.roll_no
class AcademicRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField()
    internal_marks = models.FloatField()
    mid_sem_marks = models.FloatField()
    previous_gpa = models.FloatField()
    engagement_score = models.FloatField()

    def __str__(self):
        return self.student.roll_no
from django.db import models

from django.db import models


class StudentAcademicRisk(models.Model):
    RISK_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    student = models.OneToOneField(
        "students.StudentProfile",
        on_delete=models.CASCADE,
        related_name="academic_risk"
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RISK_CHOICES
    )

    risk_score = models.FloatField(
        help_text="Normalized risk score (0 to 1)"
    )

    explanation = models.JSONField(
        null=True,
        blank=True,
        help_text="Explainable AI (SHAP) feature contributions"
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Student Academic Risk"
        verbose_name_plural = "Student Academic Risks"
        ordering = ["-risk_score"]

    def __str__(self):
        return f"{self.student.roll_no} - {self.risk_level}"





from django.utils import timezone

class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=(("PRESENT", "Present"), ("ABSENT", "Absent")),
        default="PRESENT"   # ✅ ADD THIS
    )

    class Meta:
        unique_together = ("student", "date")


class StudentSkill(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    skills = models.TextField(
        help_text="Comma-separated skills (e.g. Python, ML, SQL)"
    )

    def __str__(self):
        return f"{self.student.roll_no} Skills"
    
class Semester(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    semester_no = models.IntegerField()
    cgpa = models.FloatField()

    actual_credits = models.FloatField()
    acquired_credits = models.FloatField()
    result = models.CharField(max_length=10)

    class Meta:
        unique_together = ("student", "semester_no")

    def __str__(self):
        return f"{self.student.roll_no} - Sem {self.semester_no}"



class SubjectMark(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.subject_name} - {self.grade}"
from django.utils import timezone

from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone

class PeriodAttendance(models.Model):
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.CASCADE
    )

    faculty = models.ForeignKey(
        "faculty.FacultyProfile",
        on_delete=models.CASCADE
    )

    date = models.DateField(default=timezone.now)

    period = models.IntegerField()  # 1 to 8

    status = models.CharField(
        max_length=10,
        choices=(("PRESENT", "Present"), ("ABSENT", "Absent"))
    )

    class Meta:
        unique_together = ("student", "faculty", "date", "period")

    def __str__(self):
        return (
            f"{self.student.roll_no} | "
            f"{self.faculty.user.first_name} | "
            f"{self.date} | P{self.period} | {self.status}"
        )
class Subject(models.Model):
    name = models.CharField(max_length=100)
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.name} (Sem {self.semester})"
class MidMark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.IntegerField()
    mid_no = models.IntegerField()  # 1 or 2

    actual_marks = models.IntegerField()
    gained_marks = models.IntegerField()
    actual_assignment = models.IntegerField()
    assignment_marks = models.IntegerField()
    actual_online = models.IntegerField()
    online_quiz = models.IntegerField()
    actual_internal = models.IntegerField()
    overall_internal = models.IntegerField()

    class Meta:
        unique_together = ("student", "subject", "mid_no")

    def __str__(self):
        return f"{self.student.roll_no} - {self.subject.name} - Mid {self.mid_no}"
