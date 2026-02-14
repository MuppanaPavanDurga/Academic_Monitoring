from django.db import models
from django.contrib.auth.models import User
from students.models import StudentProfile


class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} ({self.department})"


# ✅ NEW MODEL (THIS FIXES VISIBILITY)
class CounsellingAssignment(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.faculty.user.username} → {self.student.roll_no}"


# ✅ KEEP AS-IS (DO NOT REMOVE)
class CounsellingRemark(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="counselling_remarks"
    )
    remark = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty.user.username} → {self.student.roll_no}"
class MentorshipRequest(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="mentorship_requests"
    )
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name="mentorship_requests"
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "faculty")

    def __str__(self):
        return f"{self.student.roll_no} → {self.faculty.user.username} ({self.status})"
class ChatMessage(models.Model):
    mentorship = models.ForeignKey(
        MentorshipRequest,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"
