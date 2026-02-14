from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from students.models import StudentProfile
from faculty.models import FacultyProfile



# -------------------------------
# ALUMNI REQUEST (HOME PAGE FORM)
# -------------------------------
class AlumniRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    full_name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20)
    department = models.CharField(max_length=50)
    graduation_year = models.IntegerField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.status})"


# -------------------------------
# VERIFIED ALUMNI PROFILE
# -------------------------------
class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alumni_request = models.OneToOneField(
        AlumniRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    company = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


# -------------------------------
# STUDENT ↔ ALUMNI MENTORSHIP
# -------------------------------
class AlumniMentorshipRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "alumni")

    def __str__(self):
        return f"{self.student.roll_no} → {self.alumni.user.username} ({self.status})"
class AlumniChatMessage(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    sender = models.CharField(
        max_length=10,
        choices=(("STUDENT", "Student"), ("ALUMNI", "Alumni"))
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"


class AlumniFacultyChatMessage(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    sender = models.CharField(
        max_length=10,
        choices=(("FACULTY", "Faculty"), ("ALUMNI", "Alumni"))
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.message[:30]}"

