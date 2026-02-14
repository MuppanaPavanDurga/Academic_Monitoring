from django.core.management.base import BaseCommand
from django.db.models import Avg
import joblib
from sklearn.ensemble import RandomForestClassifier

from students.models import StudentProfile, StudentAcademicRisk
from hod.models import Semester, SubjectMark
from students.models import MidMark
from students.models import PeriodAttendance


class Command(BaseCommand):
    help = "Train academic risk prediction model"

    def handle(self, *args, **kwargs):
        X = []
        y = []

        for risk in StudentAcademicRisk.objects.all():
            student = risk.student

            latest_sem = (
                Semester.objects
                .filter(student=student)
                .order_by("-semester_no")
                .first()
            )
            if not latest_sem:
                continue

            cgpa = latest_sem.cgpa

            fail_count = SubjectMark.objects.filter(
                semester=latest_sem,
                grade="F"
            ).count()

            mid_avg = (
                MidMark.objects
                .filter(student=student)
                .aggregate(avg=Avg("overall_internal"))["avg"] or 0
            )

            attendance_qs = PeriodAttendance.objects.filter(student=student)
            total = attendance_qs.count()
            present = attendance_qs.filter(status="PRESENT").count()
            attendance_pct = (present / total * 100) if total else 0

            total_subjects = SubjectMark.objects.filter(
                semester=latest_sem
            ).count()

            X.append([
                cgpa,
                attendance_pct,
                fail_count,
                mid_avg,
                total_subjects
            ])

            y.append(
                {"LOW": 0, "MEDIUM": 1, "HIGH": 2}[risk.risk_level]
            )

        if not X:
            self.stdout.write(
                self.style.ERROR("No training data available")
            )
            return

        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X, y)

        joblib.dump(model, "student_risk_model.pkl")

        self.stdout.write(
            self.style.SUCCESS("Risk model trained successfully")
        )
