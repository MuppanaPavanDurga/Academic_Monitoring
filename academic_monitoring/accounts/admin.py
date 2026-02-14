from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
import csv
from io import TextIOWrapper

from .models import UserProfile
from students.models import StudentProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')


class StudentBulkUploadAdmin(admin.ModelAdmin):
    change_list_template = "admin/student_bulk_upload.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST" and request.FILES.get("csv_file"):
            csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                roll_no = row['roll_no'].strip()
                name = row['name'].strip()

                # Create user if not exists
                if not User.objects.filter(username=roll_no).exists():
                    user = User.objects.create_user(
                        username=roll_no,
                        password=roll_no,
                        first_name=name
                    )

                    UserProfile.objects.create(
                        user=user,
                        role='STUDENT'
                    )

                    StudentProfile.objects.create(
                        user=user,
                        roll_no=roll_no,
                        department='',
                        section=''
                    )

            self.message_user(request, "Students created successfully!")
            return redirect("..")

        return render(request, "admin/student_upload.html")


# Register StudentProfile with custom admin
# admin.site.register(StudentProfile, StudentBulkUploadAdmin)
