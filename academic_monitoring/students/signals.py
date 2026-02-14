from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

# ===================== MODELS =====================

from students.models import (
    StudentAcademicRisk,
    MidMark,
    PeriodAttendance,
)

from hod.models import (
    Semester,
    SubjectMark,
)

# ===================== SERVICES =====================

from students.services.risk_engine import calculate_academic_risk

# ---- ML (optional) ----
try:
    from students.services.ml_risk_engine import predict_academic_risk_ml
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

# ---- XAI (optional) ----
try:
    from students.services.xai_engine import explain_risk_prediction
    XAI_AVAILABLE = True
except Exception:
    XAI_AVAILABLE = False


# ===================================================
# CORE RISK UPDATE FUNCTION
# ===================================================

def update_student_risk(student):
    """
    Dynamically recalculates and stores academic risk
    whenever marks or attendance are updated.
    """

    # ---------- Latest Semester ----------
    latest_sem = (
        Semester.objects
        .filter(student=student)
        .order_by("-semester_no")
        .first()
    )

    cgpa = latest_sem.cgpa if latest_sem else 0

    # ---------- Subject Performance ----------
    fail_count = (
        SubjectMark.objects.filter(semester=latest_sem, grade="F").count()
        if latest_sem else 0
    )

    total_subjects = (
        SubjectMark.objects.filter(semester=latest_sem).count()
        if latest_sem else 0
    )

    # ---------- Attendance ----------
    attendance_qs = PeriodAttendance.objects.filter(student=student)
    total_periods = attendance_qs.count()
    present_periods = attendance_qs.filter(status="PRESENT").count()

    attendance_percentage = (
        (present_periods / total_periods) * 100
        if total_periods > 0 else 0
    )

    # ---------- Mid Marks ----------
    mid_avg = (
        MidMark.objects
        .filter(student=student)
        .aggregate(avg=Avg("overall_internal"))["avg"]
        or 0
    )

    # ---------- Feature Vector ----------
    features = [
        cgpa,
        attendance_percentage,
        fail_count,
        mid_avg,
        total_subjects
    ]

    # ---------- Risk Prediction ----------
    if ML_AVAILABLE:
        try:
            risk_level, risk_score = predict_academic_risk_ml(features)
        except Exception:
            risk_level, risk_score = calculate_academic_risk(
                cgpa,
                attendance_percentage,
                fail_count,
                mid_avg
            )
    else:
        risk_level, risk_score = calculate_academic_risk(
            cgpa,
            attendance_percentage,
            fail_count,
            mid_avg
        )

    # ---------- Explainable AI (XAI) ----------
    try:
        from students.services.xai_engine import explain_risk_prediction
        
        explanation = explain_risk_prediction(features)
        
        # Save Risk & Explanation
        StudentAcademicRisk.objects.update_or_create(
            student=student,
            defaults={
                "risk_score": risk_score * 100,  # Convert to percentage
                "risk_level": risk_level,
                "explanation": explanation  # Save as JSON
            }
        )
        print(f"✅ Risk Updated for {student.roll_no}: {risk_level} (XAI Generated)")

    except Exception as e:
        print(f"❌ Error in XAI Signal: {e}")

# ===================================================
# SIGNAL TRIGGERS
# ===================================================

@receiver(post_save, sender=MidMark)
def update_risk_on_midmark(sender, instance, **kwargs):
    update_student_risk(instance.student)


@receiver(post_save, sender=Semester)
def update_risk_on_semester(sender, instance, **kwargs):
    update_student_risk(instance.student)


@receiver(post_save, sender=SubjectMark)
def update_risk_on_subjectmark(sender, instance, **kwargs):
    update_student_risk(instance.semester.student)


@receiver(post_save, sender=PeriodAttendance)
def update_risk_on_attendance(sender, instance, **kwargs):
    update_student_risk(instance.student)
print("ML_AVAILABLE =", ML_AVAILABLE)
print("XAI_AVAILABLE =", XAI_AVAILABLE)
