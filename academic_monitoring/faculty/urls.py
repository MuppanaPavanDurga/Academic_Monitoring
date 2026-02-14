from django.urls import path
from .views import (
    faculty_dashboard,
    faculty_students_list,
    faculty_students_search,
    faculty_student_detail,
    faculty_counselling_students,
    faculty_mentorship_requests,
    accept_mentorship,
    reject_mentorship,
    faculty_mentees,
    mentorship_chat,
    search_by_skill,
    mark_period_attendance,
    upload_subject_marks,
    faculty_alumni_list,
    faculty_alumni_chat,
)


urlpatterns = [
    path("dashboard/", faculty_dashboard, name="faculty_dashboard"),
    path("students/", faculty_students_list, name="faculty_students_list"),
    path("students/search/", faculty_students_search, name="faculty_students_search"),
    path("students/<int:student_id>/", faculty_student_detail, name="faculty_student_detail"),
    path("counselling/", faculty_counselling_students, name="faculty_counselling_students"),
    path("mentorship/requests/", faculty_mentorship_requests, name="faculty_mentorship_requests"),
    path("mentorship/accept/<int:request_id>/", accept_mentorship, name="accept_mentorship"),
    path("mentorship/reject/<int:request_id>/", reject_mentorship, name="reject_mentorship"),
    path("mentorship/mentees/", faculty_mentees, name="faculty_mentees"),
    path(
        "mentorship/chat/<int:mentorship_id>/", mentorship_chat, name="mentorship_chat"),
        path("skills/search/", search_by_skill, name="search_by_skill"),

    path("attendance/period/", mark_period_attendance,
     name="mark_period_attendance"),
    path(
    "marks/upload/",
    upload_subject_marks,
    name="upload_subject_marks"
),

path("alumni/", faculty_alumni_list, name="faculty_alumni_list"),
path("alumni/chat/<int:alumni_id>/", faculty_alumni_chat, name="faculty_alumni_chat"),


]
