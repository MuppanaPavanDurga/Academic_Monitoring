from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.alumni_dashboard, name="alumni_dashboard"),
    path("request/", views.alumni_request, name="alumni_request"),
    path("inbox/", views.alumni_inbox, name="alumni_inbox"),

    path("chat/<int:alumni_id>/", views.alumni_chat, name="alumni_chat"),
    path("chat/student/<int:student_id>/", views.alumni_chat_with_student, name="alumni_chat_with_student"),
    path("chat/faculty/<int:faculty_id>/", views.alumni_chat_with_faculty, name="alumni_chat_with_faculty"),


]
