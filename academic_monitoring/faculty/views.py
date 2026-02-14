from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from accounts.decorators import role_required

from students.models import StudentProfile
from faculty.models import (
    FacultyProfile,
    CounsellingAssignment,
    CounsellingRemark,
    MentorshipRequest
)
from students.models import StudentAcademicRisk
from students.services.xai_messages import generate_risk_message
from alumni.models import AlumniProfile, AlumniFacultyChatMessage
from django.db.models import Q



# =========================
# FACULTY DASHBOARD
# =========================

@login_required
def faculty_dashboard(request):
    faculty = FacultyProfile.objects.filter(user=request.user).first()
    return render(request, "faculty/dashboard.html", {"faculty": faculty})


# =========================
# FACULTY STUDENTS
# =========================

@login_required
def faculty_students_list(request):
    faculty = FacultyProfile.objects.get(user=request.user)

    students = StudentProfile.objects.filter(
        department__iexact=faculty.department.strip()
    )

    return render(
        request,
        "faculty/students_list.html",
        {"faculty": faculty, "students": students}
    )


@login_required
def faculty_students_search(request):
    faculty = FacultyProfile.objects.get(user=request.user)
    q = request.GET.get("q", "").strip()
    year = request.GET.get("year", "").strip()

    students = StudentProfile.objects.filter(
        department__iexact=faculty.department.strip()
    )

    if year and year.isdigit():
        y = int(year)
        min_sem = (y - 1) * 2 + 1
        max_sem = y * 2
        students = students.annotate(
            latest_sem_no=Max('semester__semester_no')
        ).filter(
            latest_sem_no__gte=min_sem,
            latest_sem_no__lte=max_sem
        )

    if q:
        students = students.filter(
            Q(roll_no__icontains=q) |
            Q(user__first_name__icontains=q)
        )

    data = [
        {
            "id": s.id,
            "roll_no": s.roll_no,
            "name": s.user.first_name,
            "department": s.department,
            "section": s.section,
            "year": s.pursuing_year,
        }
        for s in students
    ]

    return JsonResponse({"students": data})



# =========================
# FACULTY STUDENT DETAIL
# =========================

@login_required
def faculty_student_detail(request, student_id):
    faculty = FacultyProfile.objects.filter(user=request.user).first()

    student = get_object_or_404(
        StudentProfile,
        id=student_id,
        counsellingassignment__faculty__user=request.user
    )

    remarks = CounsellingRemark.objects.filter(
        faculty=faculty,
        student=student
    ).order_by("-date")

    if request.method == "POST":
        text = request.POST.get("remark")
        if text:
            CounsellingRemark.objects.create(
                faculty=faculty,
                student=student,
                remark=text
            )

    # 🔹 Fetch Risk Info
    risk = StudentAcademicRisk.objects.filter(student=student).first()
    risk_message = None
    if risk:
        risk_message = generate_risk_message(risk.risk_level, risk.explanation)

    return render(
        request,
        "faculty/student_detail.html",
        {
            "faculty": faculty,
            "student": student,
            "remarks": remarks,
            "risk": risk,
            "risk_message": risk_message
        }
    )



# =========================
# COUNSELLING STUDENTS
# =========================

@login_required
def faculty_counselling_students(request):
    students = StudentProfile.objects.filter(
        counsellingassignment__faculty__user=request.user
    ).distinct()

    return render(
        request,
        "faculty/counselling_students.html",
        {"students": students}
    )


# =========================
# MENTORSHIP (FACULTY SIDE)
# =========================

@login_required
@role_required(["FACULTY"])
def faculty_mentorship_requests(request):
    faculty = FacultyProfile.objects.get(user=request.user)

    requests = MentorshipRequest.objects.filter(
        faculty=faculty,
        status="PENDING"
    )

    return render(
        request,
        "faculty/mentorship_requests.html",
        {"requests": requests}
    )


@login_required
@role_required(["FACULTY"])
def accept_mentorship(request, request_id):
    faculty = FacultyProfile.objects.get(user=request.user)

    req = get_object_or_404(
        MentorshipRequest,
        id=request_id,
        faculty=faculty
    )

    req.status = "ACCEPTED"
    req.save()

    return redirect("faculty_mentorship_requests")


@login_required
@role_required(["FACULTY"])
def reject_mentorship(request, request_id):
    faculty = FacultyProfile.objects.get(user=request.user)

    req = get_object_or_404(
        MentorshipRequest,
        id=request_id,
        faculty=faculty
    )

    req.status = "REJECTED"
    req.save()

    return redirect("faculty_mentorship_requests")
@login_required
@role_required(["FACULTY"])
def faculty_mentees(request):
    faculty = FacultyProfile.objects.get(user=request.user)

    mentees = MentorshipRequest.objects.filter(
        faculty=faculty,
        status="ACCEPTED"
    ).select_related("student", "student__user")

    return render(
        request,
        "faculty/mentees.html",
        {"mentees": mentees}
    )
from django.contrib.auth.models import User
from faculty.models import ChatMessage


@login_required
def mentorship_chat(request, mentorship_id):
    mentorship = get_object_or_404(
        MentorshipRequest,
        id=mentorship_id,
        status="ACCEPTED"
    )

    # Only student or faculty involved can chat
    if request.user not in [mentorship.student.user, mentorship.faculty.user]:
        return redirect("student_dashboard")

    messages_qs = ChatMessage.objects.filter(
        mentorship=mentorship
    ).order_by("timestamp")

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            ChatMessage.objects.create(
                mentorship=mentorship,
                sender=request.user,
                message=text
            )
        return redirect("mentorship_chat", mentorship_id=mentorship.id)

    return render(
        request,
        "chat/chat.html",
        {
            "mentorship": mentorship,
            "messages": messages_qs
        }
    )
import csv
from django.http import HttpResponse
from students.models import StudentProfile, StudentSkill
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


import csv
import re
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentSkill


import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentSkill


@login_required
@role_required(["FACULTY"])
def search_by_skill(request):
    students = []
    query = ""

    if request.GET.get("skill"):
        query = request.GET.get("skill").strip().lower()

        # Fetch all skills and filter EXACT match at Python level
        all_skills = StudentSkill.objects.select_related(
            "student", "student__user"
        )

        students = [
            s for s in all_skills
            if query in [skill.strip().lower() for skill in s.skills.split(",")]
        ]

    # CSV download
    if request.GET.get("download") == "1" and query:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="students_by_skill.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["Roll No", "Name", "Department", "Skills"])

        for s in students:
            writer.writerow([
                s.student.roll_no,
                s.student.user.first_name,
                s.student.department,
                s.skills
            ])

        return response

    return render(
        request,
        "faculty/search_by_skill.html",
        {
            "students": students,
            "query": query
        }
    )
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import role_required
from students.models import StudentProfile, PeriodAttendance

@login_required
@role_required(["FACULTY"])
def mark_period_attendance(request):
    students = []
    department = section = ""
    period = None

    if request.method == "POST":
        department = request.POST.get("department")
        section = request.POST.get("section")
        period = int(request.POST.get("period"))

        students = StudentProfile.objects.filter(
            department__iexact=department,
            section__iexact=section
        )

        if "save_attendance" in request.POST:
            for s in students:
                status = request.POST.get(f"status_{s.id}")
                if status:
                    PeriodAttendance.objects.update_or_create(
                        student=s,
                        faculty=request.user.facultyprofile,  # ✅ VERY IMPORTANT
                        date=timezone.now().date(),
                        period=period,
                        defaults={"status": status}
                    )

            # You may keep redirect OR remove it if using AJAX
            return redirect("mark_period_attendance")

    return render(
        request,
        "faculty/mark_period_attendance.html",
        {
            "students": students,
            "department": department,
            "section": section,
            "period": period,
        }
    )

import csv
from students.models import StudentProfile, Subject, MidMark
from django.contrib import messages

@login_required
@role_required(["FACULTY"])
def upload_subject_marks(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        file = request.FILES["csv_file"]
        decoded = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        for row in reader:
            semester = int(row["Semester"])
            mid_no = int(row["Mid"])
            roll_no = row["RollNo"].strip()
            subject_name = row["Subject"].strip()

            student = StudentProfile.objects.get(
                roll_no__iexact=roll_no
            )

            subject, _ = Subject.objects.get_or_create(
                name=subject_name,
                semester=semester
            )

            MidMark.objects.update_or_create(
                student=student,
                subject=subject,
                semester=semester,
                mid_no=mid_no,
                defaults={
                    "actual_marks": int(row["ActualMarks"]),
                    "gained_marks": int(row["GainedMarks"]),
                    "actual_assignment":int(row["ActualAssignment"]),
                    "assignment_marks": int(row["AssignmentMarks"]),
                    "actual_online":int(row["ActualOnline"]),
                    "online_quiz":int(row["OnlineQuiz"]),
                    "actual_internal":int(row["ActualOverall"]),
                    "overall_internal": int(row["OverallInternal"]),
                }
            )

        messages.success(request, "Subject marks uploaded successfully.")
        return redirect("upload_subject_marks")

    return render(request, "faculty/upload_subject_marks.html")
    return render(request, "faculty/upload_subject_marks.html")


# =========================
# FACULTY - ALUMNI CONNECT
# =========================

@login_required
@role_required(["FACULTY"])
def faculty_alumni_list(request):
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
        "faculty/alumni_list.html",
        {
            "alumni": alumni,
            "query": query
        }
    )


@login_required
@role_required(["FACULTY"])
def faculty_alumni_chat(request, alumni_id):
    faculty = FacultyProfile.objects.get(user=request.user)
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)

    messages = AlumniFacultyChatMessage.objects.filter(
        faculty=faculty,
        alumni=alumni
    )

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            AlumniFacultyChatMessage.objects.create(
                faculty=faculty,
                alumni=alumni,
                sender="FACULTY",
                message=text
            )
        return redirect("faculty_alumni_chat", alumni_id=alumni.id)

    return render(
        request,
        "faculty/chat.html",
        {
            "messages": messages,
            "alumni": alumni,
            "is_alumni": False,  # Viewing as Faculty
            "sender_role": "FACULTY"
        }
    )
