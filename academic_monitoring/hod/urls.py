from django.urls import path
from .views import (
    hod_dashboard,
    hod_csv_upload,
    hod_counselling_faculty,
    hod_counselling_students,
    hod_counselling_remarks,
    hod_students_list,
    hod_student_detail,
    hod_students_search,
    # mark_attendance,
    monthly_attendance_report,
    low_attendance_csv,
    upload_marks_csv,
    overall_attendance_report,
    assign_counsellor_csv,
    assign_counsellor,
    send_risk_alerts,
    send_risk_alerts,
    send_attendance_alerts,
    send_attendance_alerts,
    send_apology_email,
    hod_marks_list,
    send_attendance_sms_alerts,
)

urlpatterns = [
    path('dashboard/', hod_dashboard, name='hod_dashboard'),
    path('upload/', hod_csv_upload, name='hod_upload'),
    path("students/", hod_students_list, name="hod_students_list"),
    # Counselling flow
    path('counselling/', hod_counselling_faculty, name='hod_counselling_faculty'),
    path('counselling/faculty/<int:faculty_id>/', hod_counselling_students, name='hod_counselling_students'),
    path('counselling/student/<int:student_id>/', hod_counselling_remarks, name='hod_counselling_remarks'),
    path("students/<int:student_id>/", hod_student_detail, name="hod_student_detail"),
    path("students/search/", hod_students_search, name="hod_students_search"),
    # path("attendance/", mark_attendance, name="mark_attendance"),
    path("attendance/monthly/", monthly_attendance_report,
     name="monthly_attendance_report"),
    path("attendance/low-attendance-csv/",
     low_attendance_csv,
     name="low_attendance_csv"),
    path("marks/upload/", upload_marks_csv, name="upload_marks_csv"),
    path(
    "attendance/overall/",
    overall_attendance_report,
    name="overall_attendance_report"
),
    path(
    "assign-counsellor/",
    assign_counsellor,
    name="assign_counsellor"
),

path(
    "assign-counsellor/upload/",
    assign_counsellor_csv,
    name="assign_counsellor_csv"
),

    path("alerts/attendance/", send_attendance_alerts, name="send_attendance_alerts"),
    path("alerts/risk/", send_risk_alerts, name="send_risk_alerts"),
    path("alerts/apology/", send_apology_email, name="send_apology_email"),
    path("marks/view/", hod_marks_list, name="hod_marks_list"),
    path("alerts/attendance/sms/", send_attendance_sms_alerts, name="send_attendance_sms"),

]
