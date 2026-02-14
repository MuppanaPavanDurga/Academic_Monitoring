from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required

from students.models import StudentProfile
from faculty.models import FacultyProfile, MentorshipRequest
from students.models import StudentAcademicRisk

from students.models import Semester
from students.services.xai_messages import generate_risk_message

@login_required
@role_required(["STUDENT"])
def student_dashboard(request):
    student = StudentProfile.objects.get(user=request.user)

    faculties = FacultyProfile.objects.filter(
        department__iexact=student.department.strip()
    )

    mentorship_requests = MentorshipRequest.objects.filter(student=student)

    mentorship_map = {
        req.faculty_id: req
        for req in mentorship_requests
    }

    semesters = Semester.objects.filter(
        student=student
    ).order_by("semester_no")

    risk = StudentAcademicRisk.objects.filter(
        student=student
    ).first()

    # 🔥 EXPLAINABLE AI MESSAGE
    risk_message = None
    if risk:
        risk_message = generate_risk_message(
            risk.risk_level,
            risk.explanation
        )

    return render(
        request,
        "students/dashboard.html",
        {
            "student": student,
            "faculties": faculties,
            "mentorship_map": mentorship_map,
            "semesters": semesters,
            "risk": risk,
            "risk_message": risk_message,  # ✅ ADD THIS
        }
    )



@login_required
@role_required(["STUDENT"])
def request_mentorship(request, faculty_id):
    student = StudentProfile.objects.get(user=request.user)
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)

    MentorshipRequest.objects.update_or_create(
        student=student,
        faculty=faculty,
        defaults={"status": "PENDING"}
    )

    messages.success(request, "Mentorship request sent successfully.")
    return redirect("student_dashboard")
from alumni.models import AlumniProfile
from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from alumni.models import AlumniProfile
from django.shortcuts import render


@login_required
@role_required(["STUDENT"])
def verified_alumni(request):
    query = request.GET.get("q", "").strip()
    
    alumni = AlumniProfile.objects.select_related("alumni_request")

    if query:
        alumni = alumni.filter(
            Q(alumni_request__full_name__icontains=query) |
            Q(alumni_request__roll_no__icontains=query) |
            Q(company__icontains=query)
        )

    return render(
        request,
        "students/alumni_list.html",
        {
            "alumni": alumni,
            "query": query
        }
    )

from .models import StudentSkill
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


@login_required
@role_required(["STUDENT"])
def update_skills(request):
    student = StudentProfile.objects.get(user=request.user)
    skill_obj, _ = StudentSkill.objects.get_or_create(student=student)

    if request.method == "POST":
        skill_obj.skills = request.POST.get("skills")
        skill_obj.save()

    return render(
        request,
        "students/update_skills.html",
        {"skill_obj": skill_obj}
    )
from students.models import Attendance


from students.models import Attendance
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


# @login_required
# @role_required(["STUDENT"])
# def view_attendance(request):
#     student = StudentProfile.objects.get(user=request.user)

#     attendance = Attendance.objects.filter(student=student).order_by("-date")

#     total_classes = attendance.count()
#     present_count = attendance.filter(status="PRESENT").count()

#     percentage = 0
#     if total_classes > 0:
#         percentage = round((present_count / total_classes) * 100, 2)

#     return render(
#         request,
#         "students/view_attendance.html",
#         {
#             "attendance": attendance,
#             "total_classes": total_classes,
#             "present_count": present_count,
#             "percentage": percentage,
#         }
#     )
# from datetime import datetime
# from django.utils.timezone import now
# from students.models import Attendance


# from students.models import PeriodAttendance
# from django.contrib.auth.decorators import login_required
# from accounts.decorators import role_required


# from collections import defaultdict
# from django.contrib.auth.decorators import login_required

# @login_required
# @role_required(["STUDENT"])
# def monthly_attendance(request):
#     student = StudentProfile.objects.get(user=request.user)

#     month = request.GET.get("month")
#     year = request.GET.get("year")

#     attendance = []
#     total_periods = present_periods = percentage = 0
#     attendance_rows = []   # 🔥 NEW

#     if month and year:
#         attendance = PeriodAttendance.objects.filter(
#             student=student,
#             date__month=int(month),
#             date__year=int(year)
#         ).order_by("date", "period")

#         total_periods = attendance.count()
#         present_periods = attendance.filter(
#             status="PRESENT"
#         ).count()

#         if total_periods > 0:
#             percentage = round(
#                 (present_periods / total_periods) * 100,
#                 2
#             )

#         # 🔥 BUILD DAY-WISE, PERIOD-WISE ROWS
#         rows = defaultdict(lambda: ["-"] * 8)

#         for a in attendance:
#             rows[a.date][a.period - 1] = (
#                 "P" if a.status == "PRESENT" else "A"
#             )

#         attendance_rows = [
#             {
#                 "date": date,
#                 "periods": periods
#             }
#             for date, periods in rows.items()
#         ]

#     return render(
#         request,
#         "students/monthly_attendance.html",
#         {
#             "attendance_rows": attendance_rows,  # 🔥 NEW
#             "total": total_periods,
#             "present": present_periods,
#             "percentage": percentage,
#             "month": month,
#             "year": year,
#         }
#     )


from students.models import Semester


@login_required
@role_required(["STUDENT"])
def view_marks(request):
    student = StudentProfile.objects.get(user=request.user)

    semesters = Semester.objects.filter(student=student).order_by("semester_no")

    for sem in semesters:
        subjects = sem.subjectmark_set.all()
        sem.total_subjects = subjects.count()
        sem.fail_count = subjects.filter(grade="F").count()
        sem.pass_count = sem.total_subjects - sem.fail_count

    return render(
        request,
        "students/view_marks.html",
        {"semesters": semesters}
    )

from django.http import HttpResponse
from students.models import Semester, SubjectMark
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

from students.models import PeriodAttendance


from django.contrib.auth.decorators import login_required
from collections import defaultdict

from collections import defaultdict
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, PeriodAttendance

@login_required
@role_required(["STUDENT"])
def monthly_attendance(request):
    student = StudentProfile.objects.get(user=request.user)
    month = request.GET.get("month")
    year = request.GET.get("year")

    attendance_rows = []
    total_periods = present_periods = percentage = 0

    if month and year:
        attendance = PeriodAttendance.objects.filter(
            student=student,
            date__month=int(month),
            date__year=int(year)
        ).order_by("date", "period")

        total_periods = attendance.count()
        present_periods = attendance.filter(status="PRESENT").count()

        if total_periods > 0:
            percentage = round((present_periods / total_periods) * 100, 2)

        rows = defaultdict(lambda: ["-"] * 8)
        for a in attendance:
            rows[a.date][a.period - 1] = "P" if a.status == "PRESENT" else "A"

        attendance_rows = [
            {"date": date, "periods": periods}
            for date, periods in rows.items()
        ]

    return render(
        request,
        "students/monthly_attendance.html",
        {
            "attendance_rows": attendance_rows,
            "total": total_periods,
            "present": present_periods,
            "percentage": percentage,
            "month": month,
            "year": year,
        }
    )


@login_required
@role_required(["STUDENT"])
def view_period_attendance(request):
    student = StudentProfile.objects.get(user=request.user)

    attendance = PeriodAttendance.objects.filter(
        student=student
    ).order_by("date", "period")

    total_periods = attendance.count()
    present_periods = attendance.filter(status="PRESENT").count()

    percentage = round(
        (present_periods / total_periods) * 100, 2
    ) if total_periods > 0 else 0

    rows = defaultdict(lambda: ["-"] * 8)
    for a in attendance:
        rows[a.date][a.period - 1] = "P" if a.status == "PRESENT" else "A"

    attendance_rows = [
        {"date": date, "periods": periods}
        for date, periods in rows.items()
    ]

    return render(
        request,
        "students/view_period_attendance.html",
        {
            "attendance_rows": attendance_rows,
            "total_periods": total_periods,
            "present_periods": present_periods,
            "percentage": percentage,
        }
    )
from django.db.models import Count, Q
from students.models import PeriodAttendance, StudentProfile
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

@login_required
@role_required(["STUDENT"])
def faculty_wise_attendance(request):
    student = StudentProfile.objects.get(user=request.user)

    attendance = (
        PeriodAttendance.objects
        .filter(student=student)
        .values("faculty__user__first_name", "faculty__user__username")
        .annotate(
            total_periods=Count("id"),
            present_periods=Count("id", filter=Q(status="PRESENT"))
        )
    )

    for a in attendance:
        a["percentage"] = round(
            (a["present_periods"] / a["total_periods"]) * 100, 2
        ) if a["total_periods"] > 0 else 0

    return render(
        request,
        "students/faculty_wise_attendance.html",
        {"attendance": attendance}
    )
from students.models import MidMark
from collections import defaultdict

@login_required
@role_required(["STUDENT"])
def semester_internal_marks(request, semester_no):
    student = StudentProfile.objects.get(user=request.user)

    mids = MidMark.objects.filter(
        student=student,
        semester=semester_no
    )

    subject_map = defaultdict(lambda: {
        "mid1": 0,
        "mid2": 0,
        "total": 0
    })

    for m in mids:
        if m.mid_no == 1:
            subject_map[m.subject.name]["mid1"] = m.overall_internal
        elif m.mid_no == 2:
            subject_map[m.subject.name]["mid2"] = m.overall_internal

    for sub in subject_map:
        subject_map[sub]["total"] = (
            subject_map[sub]["mid1"] +
            subject_map[sub]["mid2"]
        )

    return render(
        request,
        "students/internal_marks.html",
        {
            "semester": semester_no,
            "subjects": subject_map
        }
    )
@login_required
@role_required(["STUDENT"])
def view_mid_marks(request):
    student = StudentProfile.objects.get(user=request.user)

    mid_marks = (
        MidMark.objects
        .filter(student=student)
        .select_related("subject")
        .order_by("semester", "subject__name", "mid_no")
    )

    # Organize as: semester → subject → mids
    semesters = {}

    for m in mid_marks:
        sem = semesters.setdefault(m.semester, {})
        subject = sem.setdefault(m.subject.name, {})
        subject[m.mid_no] = m

    return render(
        request,
        "students/view_mid_marks.html",
        {
            "student": student,
            "semesters": semesters
        }
    )
