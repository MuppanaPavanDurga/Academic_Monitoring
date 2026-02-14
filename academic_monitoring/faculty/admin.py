from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
import csv
from io import TextIOWrapper

from accounts.models import UserProfile
from .models import FacultyProfile, CounsellingAssignment, CounsellingRemark


# Unregister if already registered (to avoid conflicts)
try:
    admin.site.unregister(FacultyProfile)
except admin.sites.NotRegistered:
    pass


class FacultyAdmin(admin.ModelAdmin):
    list_display = ("get_username", "department")
    change_list_template = "admin/faculty/facultyprofile/change_list.html"

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"

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
                username = row.get("username", "").strip()
                password = row.get("password", "").strip()
                email = row.get("email", "").strip()
                department = row.get("department", "").strip()

                if not username:
                    continue

                # Create User
                user, created = User.objects.get_or_create(username=username)

                if created:
                    user.set_password(password if password else username)
                    user.email = email
                    user.save()

                # Ensure UserProfile
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={"role": "FACULTY"}
                )

                # Create/Update FacultyProfile
                faculty, _ = FacultyProfile.objects.get_or_create(user=user)
                faculty.department = department
                faculty.save()

            self.message_user(
                request,
                "Faculty uploaded successfully. Users & profiles created."
            )
            return redirect("..")

        return render(request, "admin/upload_faculty.html")


admin.site.register(FacultyProfile, FacultyAdmin)

admin.site.register(CounsellingAssignment)
admin.site.register(CounsellingRemark)
