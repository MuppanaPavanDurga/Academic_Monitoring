from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
import csv
from io import TextIOWrapper

from accounts.models import UserProfile
from .models import StudentProfile, AcademicRecord, Attendance


# 🔥 ENSURE CLEAN STATE (VERY IMPORTANT)
try:
    admin.site.unregister(StudentProfile)
except admin.sites.NotRegistered:
    pass


class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_no", "department", "section")
    change_list_template = "admin/students/studentprofile/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_csv),
            ),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST" and request.FILES.get("csv_file"):
            csv_file = TextIOWrapper(
                request.FILES["csv_file"].file,
                encoding="utf-8-sig"
            )
            reader = csv.DictReader(csv_file)

            for row in reader:
                roll_no = row.get("roll_no", "").strip()
                name = row.get("name", "").strip()
                department = row.get("department", "").strip()
                section = row.get("section", "").strip()
                section = row.get("section", "").strip()
                email = row.get("email", "").strip()
                mobile_no = row.get("mobile_no", "").strip()

                if not roll_no:
                    continue

                # ✅ CREATE / GET USER
                user, created = User.objects.get_or_create(username=roll_no)

                if created:
                    user.set_password(roll_no)   # password = roll number
                    user.first_name = name
                    user.email = email  # ✅ SAVE EMAIL TO USER MODEL
                    user.save()
                else:
                    # Update email if user already exists
                    if user.email != email:
                        user.email = email
                        user.save()

                # ✅ ALWAYS ENSURE USER PROFILE EXISTS
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={"role": "STUDENT"}
                )

                # ✅ CREATE / UPDATE STUDENT PROFILE
                student, _ = StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={"roll_no": roll_no}
                )

                student.department = department
                student.section = section
                student.email = email
                student.mobile_no = mobile_no
                student.save()

            self.message_user(
                request,
                "Students uploaded successfully. Users & profiles created."
            )
            return redirect("..")

        return render(request, "admin/upload_students.html")


# ✅ REGISTER MODELS (ONLY ONCE)
admin.site.register(StudentProfile, StudentAdmin)
admin.site.register(AcademicRecord)
admin.site.register(Attendance)
