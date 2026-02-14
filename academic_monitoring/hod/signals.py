from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from hod.models import FacultyAssignment
from faculty.models import CounsellingAssignment


# ✅ CREATE counselling assignment when HOD assigns
@receiver(post_save, sender=FacultyAssignment)
def create_counselling_assignment(sender, instance, **kwargs):
    CounsellingAssignment.objects.get_or_create(
        faculty=instance.faculty,
        student=instance.student
    )


# ✅ DELETE counselling assignment when HOD unassigns
@receiver(post_delete, sender=FacultyAssignment)
def delete_counselling_assignment(sender, instance, **kwargs):
    CounsellingAssignment.objects.filter(
        faculty=instance.faculty,
        student=instance.student
    ).delete()
