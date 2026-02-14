from django.core.management.base import BaseCommand
from students.models import StudentProfile
from students.signals import update_student_risk


class Command(BaseCommand):
    help = "Recalculate academic risk for all students using ML + XAI if available"

    def handle(self, *args, **kwargs):

        students = StudentProfile.objects.all()

        if not students.exists():
            self.stdout.write(self.style.WARNING("No students found"))
            return

        for student in students:
            update_student_risk(student)

        self.stdout.write(
            self.style.SUCCESS("Risk backfill completed using ML/XAI")
        )
