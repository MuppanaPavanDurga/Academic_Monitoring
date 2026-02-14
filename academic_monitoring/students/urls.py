from django.urls import path
from .views import student_dashboard
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path(
        "request-mentorship/<int:faculty_id>/",
        views.request_mentorship,
        name="request_mentorship"
    ),
    path("alumni/", views.verified_alumni, name="verified_alumni"),
    path("skills/", views.update_skills, name="update_skills"),
    # path("attendance/", views.view_attendance, name="view_attendance"),
    path("attendance/monthly/", views.monthly_attendance, name="monthly_attendance"),
    path("marks/", views.view_marks, name="view_marks"),
    path("attendance/periods/",
     views.view_period_attendance,
     name="view_period_attendance"),
    path(
    "attendance/faculty-wise/",
    views.faculty_wise_attendance,
    name="faculty_wise_attendance"
),
    path("marks/mids/", views.view_mid_marks, name="view_mid_marks"),
    path("marks/semester/<int:semester_no>/", views.semester_internal_marks, name="semester_internal_marks"),




]

