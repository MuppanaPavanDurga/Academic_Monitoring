from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
import pandas as pd
import pickle

from accounts.decorators import role_required
from students.models import StudentProfile, AcademicRecord
from ml_engine.models import PredictionResult
from faculty.models import FacultyProfile, CounsellingRemark, CounsellingAssignment
from hod.models import HODProfile, FacultyAssignment
from alumni.models import AlumniProfile, AlumniRequest  # ✅ IMPORT
from django.utils import timezone


MODEL_PATH = 'ml_engine/student_model.pkl'

from students.services.xai_messages import generate_risk_message
from students.models import StudentAcademicRisk



# =========================
# HOD DASHBOARD
# =========================
@login_required
@role_required(['HOD'])
def hod_dashboard(request):
    hod = HODProfile.objects.get(user=request.user)

    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip()
    )

    return render(
        request,
        "hod/dashboard.html",
        {
            "hod": hod,
            "students": students
        }
    )


# =========================
# HOD CSV UPLOAD (PREDICTION)
# =========================
@login_required
@role_required(['HOD'])
def hod_csv_upload(request):

    low_risk, medium_risk, high_risk = [], [], []

    if request.method == 'POST' and request.FILES.get('csv_file'):
        data = pd.read_csv(request.FILES['csv_file'])

        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)

        for _, row in data.iterrows():
            roll_no = str(row['roll_no']).strip()
            name = row['name']

            features = [[
                row['attendance'],
                row['internal'],
                row['mid'],
                row['previous'],
                row['engagement']
            ]]

            score = model.predict(features)[0]

            if score >= 75:
                risk, bucket = 'Low', low_risk
            elif score >= 50:
                risk, bucket = 'Medium', medium_risk
            else:
                risk, bucket = 'High', high_risk

            student = StudentProfile.objects.filter(roll_no=roll_no).first()
            status = "Registered" if student else "Not Registered"

            if student:
                AcademicRecord.objects.update_or_create(
                    student=student,
                    defaults={
                        'attendance_percentage': row['attendance'],
                        'internal_marks': row['internal'],
                        'mid_sem_marks': row['mid'],
                        'previous_gpa': row['previous'],
                        'engagement_score': row['engagement'],
                    }
                )

                PredictionResult.objects.update_or_create(
                    student=student,
                    defaults={
                        'prediction_score': score,
                        'risk_level': risk
                    }
                )

            bucket.append({
                'roll_no': roll_no,
                'name': name,
                'score': score,
                'status': status
            })

    return render(request, 'hod/upload.html', {
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk
    })


# =========================
# COUNSELLING – FACULTY LIST
# =========================
@login_required
@role_required(['HOD'])
def hod_counselling_faculty(request):
    hod = HODProfile.objects.get(user=request.user)

    faculties = FacultyProfile.objects.filter(
        department=hod.department
    )

    return render(
        request,
        'hod/counselling_faculty.html',
        {
            'faculties': faculties
        }
    )



# =========================
# COUNSELLING – STUDENTS UNDER FACULTY (AUTO SYNC)
# =========================
@login_required
@role_required(['HOD'])
def hod_counselling_students(request, faculty_id):
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)

    assignments = FacultyAssignment.objects.filter(faculty=faculty)

    students = []
    for assign in assignments:
        # 🔥 AUTO CREATE COUNSELLING ASSIGNMENT
        CounsellingAssignment.objects.get_or_create(
            faculty=faculty,
            student=assign.student
        )
        students.append(assign.student)

    return render(request, 'hod/counselling_students.html', {
        'faculty': faculty,
        'students': students
    })


# =========================
# COUNSELLING – STUDENT REMARKS
# =========================
@login_required
@role_required(['HOD'])
def hod_counselling_remarks(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    remarks = CounsellingRemark.objects.filter(student=student).order_by('-date')

    return render(request, 'hod/counselling_remarks.html', {
        'student': student,
        'remarks': remarks
    })


# =========================
# HOD – STUDENT LIST
# =========================
@login_required
@role_required(['HOD'])
def hod_students_list(request):
    hod = HODProfile.objects.get(user=request.user)
    query = request.GET.get("q", "").strip()

    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip()
    ).order_by("section", "roll_no")  # ✅ SECTION ORDER FIX

    if query:
        students = students.filter(
            Q(roll_no__icontains=query) |
            Q(user__first_name__icontains=query)
        )

    return render(
        request,
        "hod/students_list.html",
        {
            "hod": hod,
            "students": students,
            "query": query,
        }
    )

from students.models import Semester

@login_required
@role_required(['HOD'])
def hod_student_detail(request, student_id):
    hod = HODProfile.objects.get(user=request.user)

    student = get_object_or_404(
        StudentProfile,
        id=student_id,
        department__iexact=hod.department.strip()
    )

    # 🔹 Fetch semester-wise marks
    semesters = Semester.objects.filter(student=student).order_by("semester_no")

    # 🔹 Compute summary per semester
    for sem in semesters:
        subjects = sem.subjectmark_set.all()
        sem.total_subjects = subjects.count()
        sem.fail_count = subjects.filter(grade="F").count()
        sem.pass_count = sem.total_subjects - sem.fail_count

    # 🔹 Fetch Risk Info
    risk = StudentAcademicRisk.objects.filter(student=student).first()
    risk_message = None
    if risk:
        risk_message = generate_risk_message(risk.risk_level, risk.explanation)

    return render(
        request,
        "hod/student_detail.html",
        {
            "hod": hod,
            "student": student,
            "semesters": semesters,
            "risk": risk,
            "risk_message": risk_message,
        }
    )



# =========================
# AJAX SEARCH
# =========================
@login_required
@role_required(['HOD'])
def hod_students_search(request):
    hod = HODProfile.objects.get(user=request.user)
    query = request.GET.get("q", "").strip()
    year = request.GET.get("year", "").strip()  # 1, 2, 3, 4

    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip()
    )

    # Filter by Year
    if year and year.isdigit():
        y = int(year)
        # 1st Year: Sem 1-2
        # 2nd Year: Sem 3-4
        # 3rd Year: Sem 5-6
        # 4th Year: Sem 7-8
        min_sem = (y - 1) * 2 + 1
        max_sem = y * 2

        # Filter: latest semester number is within this range
        students = students.annotate(
            latest_sem_no=Max('semester__semester_no')
        ).filter(
            latest_sem_no__gte=min_sem,
            latest_sem_no__lte=max_sem
        )

    if query:
        students = students.filter(
            Q(roll_no__icontains=query) |
            Q(user__first_name__icontains=query)
        )

    data = [{
        "id": s.id,
        "roll_no": s.roll_no,
        "name": s.user.first_name,
        "department": s.department,
        "section": s.section,
        "year": s.pursuing_year,  # Send computed year to frontend
    } for s in students]

    return JsonResponse({"students": data})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, Attendance
from django.utils import timezone

# Monthly Attendance
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, PeriodAttendance

@login_required
@role_required(["HOD"])
def monthly_attendance_report(request):
    students = []
    department = section = month = year = ""

    if request.GET:
        department = request.GET.get("department")
        section = request.GET.get("section")
        month = request.GET.get("month")
        year = request.GET.get("year")

        if department and section and month and year:
            students = StudentProfile.objects.filter(
                department__iexact=department,
                section__iexact=section
            )

            for s in students:
                total = PeriodAttendance.objects.filter(
                    student=s,
                    date__month=int(month),
                    date__year=int(year)
                ).count()

                present = PeriodAttendance.objects.filter(
                    student=s,
                    date__month=int(month),
                    date__year=int(year),
                    status="PRESENT"
                ).count()

                s.total_periods = total
                s.present_periods = present
                s.percentage = round((present / total) * 100, 2) if total > 0 else 0

    if request.GET.get("download") == "1":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="monthly_attendance_report.csv"'
        writer = csv.writer(response)

        writer.writerow([
            "Roll No", "Name", "Department", "Section",
            "Total Periods", "Present Periods", "Percentage"
        ])

        for s in students:
            writer.writerow([
                s.roll_no,
                s.user.first_name,
                s.department,
                s.section,
                s.total_periods,
                s.present_periods,
                s.percentage
            ])

        return response

    return render(
        request,
        "hod/monthly_attendance_report.html",
        {
            "students": students,
            "department": department,
            "section": section,
            "month": month,
            "year": year,
        }
    )


@login_required
@role_required(["HOD"])
def low_attendance_csv(request):
    department = request.GET.get("department")
    section = request.GET.get("section")
    month = request.GET.get("month")
    year = request.GET.get("year")
    threshold = int(request.GET.get("threshold", 75))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="low_attendance_students.csv"'
    writer = csv.writer(response)

    writer.writerow([
        "Roll No", "Name", "Department", "Section",
        "Total Periods", "Present Periods", "Percentage"
    ])

    students = StudentProfile.objects.filter(
        department__iexact=department,
        section__iexact=section
    )

    for s in students:
        total = PeriodAttendance.objects.filter(
            student=s,
            date__month=int(month),
            date__year=int(year)
        ).count()

        present = PeriodAttendance.objects.filter(
            student=s,
            date__month=int(month),
            date__year=int(year),
            status="PRESENT"
        ).count()

        percentage = round((present / total) * 100, 2) if total > 0 else 0

        if percentage < threshold:
            writer.writerow([
                s.roll_no,
                s.user.first_name,
                s.department,
                s.section,
                total,
                present,
                percentage
            ])

    return response

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, Semester, SubjectMark


@login_required
@role_required(["HOD"])
def upload_marks_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        try:
            csv_file = TextIOWrapper(
                request.FILES["csv_file"].file,
                encoding="utf-8",
                newline=""
            )
            reader = csv.reader(csv_file)
            header = next(reader)

            semester_idx = header.index("Semester")
            roll_idx = header.index("RollNO")
            cgpa_idx = header.index("CGPA")
            actual_credits_idx = header.index("ActualCredits")
            acquired_credits_idx = header.index("AcquiredCredits")
            result_idx = header.index("Result")

            subject_columns = header[3:actual_credits_idx]

            for row_no, row in enumerate(reader, start=2):
                try:
                    semester_no = int(row[semester_idx].strip())
                    roll_no = row[roll_idx].strip()
                    cgpa = float(row[cgpa_idx].strip())
                    actual_credits = float(row[actual_credits_idx].strip())
                    acquired_credits = float(row[acquired_credits_idx].strip())
                    result = row[result_idx].strip()

                    student = StudentProfile.objects.get(roll_no=roll_no)

                    semester, _ = Semester.objects.update_or_create(
                        student=student,
                        semester_no=semester_no,
                        defaults={
                            "cgpa": cgpa,
                            "actual_credits": actual_credits,
                            "acquired_credits": acquired_credits,
                            "result": result,
                        }
                    )

                    # Clear old subjects
                    SubjectMark.objects.filter(semester=semester).delete()

                    for i, subject in enumerate(subject_columns):
                        grade = row[3 + i].strip()
                        SubjectMark.objects.create(
                            semester=semester,
                            subject_name=subject.strip(),
                            grade=grade
                        )

                    # ✅ AUTO-GRADUATE CHECK
                    # If student has completed 8 semesters, mark as graduated
                    sem_count = Semester.objects.filter(student=student).count()
                    if sem_count >= 8:
                        student.is_graduated = True
                        student.save()

                        # 🔥 AUTO-CREATE ALUMNI PROFILE
                        if not AlumniProfile.objects.filter(user=student.user).exists():
                            # 1. Create Approved Request
                            alumni_req = AlumniRequest.objects.create(
                                full_name=student.user.first_name,
                                roll_no=student.roll_no,
                                department=student.department,
                                graduation_year=timezone.now().year,
                                status="APPROVED"
                            )
                            # 2. Create Profile
                            AlumniProfile.objects.create(
                                user=student.user,
                                alumni_request=alumni_req
                            )



                except (ValueError, IndexError) as e:
                    messages.error(
                        request,
                        f"Row {row_no} skipped due to invalid data."
                    )
                    continue

            messages.success(request, "Marks CSV uploaded successfully.")
            return redirect("upload_marks_csv")

        except Exception as e:
            messages.error(request, f"Upload failed: {e}")

    return render(request, "hod/upload_marks_csv.html")
import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile, PeriodAttendance


@login_required
@role_required(["HOD"])
def overall_attendance_report(request):
    students = []
    department = section = ""

    if request.GET:
        department = request.GET.get("department")
        section = request.GET.get("section")

        if department and section:
            students = StudentProfile.objects.filter(
                department__iexact=department,
                section__iexact=section
            )

            for s in students:
                total = PeriodAttendance.objects.filter(student=s).count()
                present = PeriodAttendance.objects.filter(
                    student=s, status="PRESENT"
                ).count()

                s.total_periods = total
                s.present_periods = present
                s.percentage = round((present / total) * 100, 2) if total > 0 else 0

    # CSV DOWNLOAD
    if request.GET.get("download") == "1":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="overall_attendance_report.csv"'
        writer = csv.writer(response)

        writer.writerow([
            "Roll No", "Name", "Department", "Section",
            "Total Periods", "Present Periods", "Percentage"
        ])

        for s in students:
            writer.writerow([
                s.roll_no,
                s.user.first_name,
                s.department,
                s.section,
                s.total_periods,
                s.present_periods,
                s.percentage
            ])

        return response

    return render(
        request,
        "hod/overall_attendance_report.html",
        {
            "students": students,
            "department": department,
            "section": section,
        }
    )
#Counsellor Assignment
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required

from students.models import StudentProfile
from faculty.models import FacultyProfile
from hod.models import FacultyAssignment


@login_required
@role_required(["HOD"])
def assign_counsellor(request):
    hod = HODProfile.objects.get(user=request.user)

    faculties = FacultyProfile.objects.filter(
        department__iexact=hod.department.strip()
    )

    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip()
    )

    if request.method == "POST":
        faculty_id = request.POST.get("faculty")
        student_id = request.POST.get("student")

        faculty = FacultyProfile.objects.get(id=faculty_id)
        student = StudentProfile.objects.get(id=student_id)

        FacultyAssignment.objects.update_or_create(
            student=student,
            defaults={"faculty": faculty}
        )

        messages.success(request, "Counselling faculty assigned successfully.")
        return redirect("assign_counsellor")

    return render(
        request,
        "hod/assign_counsellor.html",
        {
            "faculties": faculties,
            "students": students
        }
    )


@login_required
@role_required(["HOD"])
def assign_counsellor_csv(request):
    hod = HODProfile.objects.get(user=request.user)

    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        decoded = csv_file.read().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(decoded)

        success = 0
        failed = 0

        for row in reader:
            # Normalize headers
            row = {k.strip().lower(): v.strip() for k, v in row.items()}

            faculty_username = row.get("faculty name")
            roll_no = row.get("student rollno")

            if not faculty_username or not roll_no:
                failed += 1
                continue

            try:
                faculty = FacultyProfile.objects.get(
                    user__username__iexact=faculty_username,
                    department__iexact=hod.department.strip()
                )

                student = StudentProfile.objects.get(
                    roll_no__iexact=roll_no,
                    department__iexact=hod.department.strip()
                )

                FacultyAssignment.objects.update_or_create(
                    student=student,
                    defaults={"faculty": faculty}
                )

                success += 1

            except (FacultyProfile.DoesNotExist, StudentProfile.DoesNotExist):
                failed += 1
                continue

        messages.success(
            request,
            f"CSV upload completed. Assigned: {success}, Failed: {failed}"
        )

    return redirect("assign_counsellor")

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings


from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count, Q

from students.models import StudentProfile, PeriodAttendance
from hod.models import HODProfile


@login_required
@role_required(["HOD"])
def send_attendance_alerts(request):
    if request.method != "POST":
        return redirect("hod_dashboard")

    hod = HODProfile.objects.get(user=request.user)

    sent = 0

    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip(),
        user__email__isnull=False
    ).exclude(user__email="")

    for student in students:
        attendance = (
            PeriodAttendance.objects
            .filter(student=student)
            .aggregate(
                total=Count("id"),
                present=Count("id", filter=Q(status="PRESENT"))
            )
        )

        total = attendance["total"]
        present = attendance["present"]

        if total == 0:
            continue

        percentage = (present / total) * 100

        # Determine Status
        if percentage < 75:
            status = "CRITICAL"
            subject_line = "⚠️ Attendance Alert: Action Required"
            title = "Attendance Warning Notice"
            message_body = "Your attendance has dropped below the minimum required academic threshold."
            color = "#dc2626"  # Red
            bg_color = "#fee2e2"
            border_color = "#ef4444"
            
        elif 75 <= percentage < 85:
            status = "MODERATE"
            subject_line = "⚠️ Attendance Update: Improvement Needed"
            title = "Attendance Status: Moderate"
            message_body = "Your attendance is within the moderate range. Please strive to improve it to ensure academic safety."
            color = "#d97706"  # Amber
            bg_color = "#fef3c7"
            border_color = "#f59e0b"

        else:  # >= 85
            status = "EXCELLENT"
            subject_line = "🌟 Attendance Appreciation: Excellent"
            title = "Attendance Status: Excellent"
            message_body = "Great job! Your attendance record is excellent. Keep up the consistent performance!"
            color = "#16a34a"  # Green
            bg_color = "#dcfce7"
            border_color = "#22c55e"

        # Prepare HTML content
        html_message = render_to_string('emails/attendance_alert.html', {
            'student': student,
            'percentage': percentage,
            'status': status,
            'title': title,
            'message_body': message_body,
            'color': color,
            'bg_color': bg_color,
            'border_color': border_color,
            'year': timezone.now().year
        })
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject_line,
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.user.email],
                html_message=html_message,
                fail_silently=False
            )
            sent += 1
        except Exception as e:
            print(f"Error sending email to {student.user.email}: {e}")

    messages.success(request, f"Attendance status emails sent to {sent} students successfully.")
    return redirect("hod_dashboard")



from students.models import StudentAcademicRisk
from students.services.xai_messages import generate_risk_message

@login_required
@role_required(["HOD"])
def send_risk_alerts(request):
    if request.method != "POST":
        return redirect("hod_dashboard")

    from django.conf import settings
    from django.core.mail import send_mail
    from students.models import StudentAcademicRisk
    from students.services.xai_messages import generate_risk_message

    sent = 0

    for risk in StudentAcademicRisk.objects.select_related("student"):
        if risk.risk_level not in ["HIGH", "MEDIUM"]:
            continue

        student = risk.student
        email = student.user.email
        if not email:
            continue

        message_text = generate_risk_message(risk.risk_level, risk.explanation)

        html_message = render_to_string('emails/risk_alert.html', {
            'student': student,
            'risk': risk,
            'message': message_text
        })
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=f"⚠️ Academic Risk Alert: {risk.risk_level}",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )
            sent += 1
        except Exception as e:
            print(f"Error sending risk alert to {email}: {e}")

    if sent == 0:
        messages.info(request, "No high/medium risk students found to alert.")
    else:
        messages.success(request, f"Risk alerts sent to {sent} students successfully.")

    return redirect("hod_dashboard")



@login_required
@role_required(["HOD"])
def send_apology_email(request):
    if request.method == "POST":
        from django.core.mail import send_mail
        from django.conf import settings
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from students.models import StudentProfile

        students = StudentProfile.objects.select_related("user").all()
        sent = 0
        
        subject = "Clarification Regarding Previous Academic Alert Email"
        from_email = settings.EMAIL_HOST_USER
        
        # Pre-render template since content is static
        html_message = render_to_string("emails/apology.html", {})
        plain_message = strip_tags(html_message)

        for student in students:
            email = student.user.email
            if not email:
                continue

            try:
                # We send individually to personalize if needed or just iterate
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=from_email,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False
                )
                sent += 1
            except Exception as e:
                print(f"Error sending apology to {email}: {e}")
        
        messages.success(request, f"Apology emails sent to {sent} students.")
    
    return redirect("hod_dashboard")


@login_required
@role_required(["HOD"])
def hod_marks_list(request):
    # Get filter options
    departments = StudentProfile.objects.values_list('department', flat=True).distinct()
    sections = StudentProfile.objects.values_list('section', flat=True).distinct()
    
    selected_dept = request.GET.get('department')
    selected_sec = request.GET.get('section')
    selected_sem = request.GET.get('semester')
    selected_year = request.GET.get('year')
    
    students_data = []
    subjects = []
    
    if selected_dept and selected_sec and selected_sem:
        from students.models import Semester, SubjectMark
        
        # Fetch relevant semester records
        sem_records = Semester.objects.filter(
            student__department=selected_dept,
            student__section=selected_sec,
            semester_no=selected_sem
        ).select_related('student', 'student__user').prefetch_related('subjectmark_set')

        # Filter by Pursuing Year
        if selected_year:
            year_map = {
                "1st Year": [1, 2],
                "2nd Year": [3, 4],
                "3rd Year": [5, 6],
                "4th Year": [7, 8],
            }
            target_sems = year_map.get(selected_year)
            if target_sems:
                # Find students currently in this year
                students_in_year = StudentProfile.objects.annotate(
                    max_sem=Max('semester__semester_no')
                ).filter(max_sem__in=target_sems)
                
                sem_records = sem_records.filter(student__in=students_in_year)
        
        if sem_records.exists():
            # Collect all unique subjects for header
            # We filter marks only for these semesters to avoid fetching all marks in DB
            all_marks = SubjectMark.objects.filter(semester__in=sem_records)
            subjects = list(all_marks.values_list('subject_name', flat=True).distinct().order_by('subject_name'))
            
            for sem in sem_records:
                marks_list = []
                student_marks = sem.subjectmark_set.all()
                
                # Create a simple list/dict for template to consume
                for mark in student_marks:
                    marks_list.append({
                        'subject': mark.subject_name,
                        'grade': mark.grade
                    })
                
                students_data.append({
                    'student': sem.student,
                    'semester': sem,
                    'marks': marks_list
                })

        # ==========================
        # CSV EXPORT LOGIC
        # ==========================
        if request.GET.get('download') == 'csv':
            import csv
            from django.http import HttpResponse

            response = HttpResponse(content_type='text/csv')
            filename = f"Marks_{selected_dept}_{selected_sec}_Sem{selected_sem}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            writer = csv.writer(response)
            
            # 1. Header Row
            header = ['Roll No', 'Name'] + subjects + ['SGPA', 'Result']
            writer.writerow(header)

            # 2. Data Rows
            for row in students_data:
                student = row['student']
                sem = row['semester']
                marks = row['marks'] # List of dicts {'subject':..., 'grade':...}
                
                # Create a map for quick lookup
                grade_map = {m['subject']: m['grade'] for m in marks}
                
                # Fill subject columns
                subject_grades = []
                for subj in subjects:
                    subject_grades.append(grade_map.get(subj, '-')) # '-' if no mark found
                
                # Full Row
                data_row = [
                    student.roll_no,
                    student.user.first_name,
                ] + subject_grades + [
                    sem.cgpa,
                    sem.result
                ]
                writer.writerow(data_row)
            
            return response

    return render(request, 'hod/marks_list.html', {
        'departments': departments,
        'sections': sections,
        'selected_dept': selected_dept,
        'selected_sec': selected_sec,
        'selected_sem': selected_sem,
        'selected_year': selected_year,
        'students_data': students_data,
        'subjects': subjects
    })
from students.services.sms_service import send_sms
from django.db.models import Count, Q
from students.models import StudentProfile, PeriodAttendance
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from hod.models import HODProfile


from students.services.sms_service import send_sms
from django.db.models import Count, Q
from students.models import StudentProfile, PeriodAttendance
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from hod.models import HODProfile


@login_required
@role_required(["HOD"])
def send_attendance_sms_alerts(request):

    if request.method != "POST":
        return redirect("hod_dashboard")

    hod = HODProfile.objects.get(user=request.user)

    sent = 0

    # IMPORTANT: correct field name mobile_no
    students = StudentProfile.objects.filter(
        department__iexact=hod.department.strip()
    ).exclude(mobile_no="").exclude(mobile_no__isnull=True)

    for student in students:

        attendance = (
            PeriodAttendance.objects
            .filter(student=student)
            .aggregate(
                total=Count("id"),
                present=Count("id", filter=Q(status="PRESENT"))
            )
        )

        total = attendance["total"]
        present = attendance["present"]

        if total == 0:
            continue

        percentage = (present / total) * 100

        # -------- STATUS LOGIC --------
        if percentage < 75:
            sms_message = (
                f"⚠️ Attendance Alert\n"
                f"{student.user.first_name}, your attendance is {round(percentage,2)}%.\n"
                f"Minimum required is 75%.\n"
                f"Attend classes regularly immediately.\n"
                f"- HOD"
            )

        elif 75 <= percentage < 85:
            sms_message = (
                f"Attendance Notice\n"
                f"{student.user.first_name}, your attendance is {round(percentage,2)}%.\n"
                f"You are close to shortage. Improve attendance.\n"
                f"- HOD"
            )

        else:
            # Do not send SMS to good attendance students
            continue

        # SEND SMS
        success = send_sms(student.mobile_no, sms_message)

        if success:
            sent += 1
        else:
            print("SMS failed for:", student.mobile_no)

    messages.success(request, f"Attendance SMS alerts sent to {sent} students.")
    return redirect("hod_dashboard")
