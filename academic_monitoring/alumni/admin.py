from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from accounts.models import UserProfile
from .models import AlumniRequest, AlumniProfile


@admin.register(AlumniRequest)
class AlumniRequestAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "roll_no",
        "department",
        "graduation_year",
        "status"
    )
    list_filter = ("status",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status == "APPROVED":
            roll_no = obj.roll_no

            # 1️⃣ Create User
            user, created = User.objects.get_or_create(
                username=roll_no,
                defaults={
                    "first_name": obj.full_name,
                    "password": make_password(roll_no),
                }
            )

            # 2️⃣ Create UserProfile (THIS FIXES LOGIN ERROR)
            UserProfile.objects.get_or_create(
                user=user,
                defaults={"role": "ALUMNI"}
            )

            # 3️⃣ Create AlumniProfile
            AlumniProfile.objects.get_or_create(
                user=user,
                alumni_request=obj
            )
