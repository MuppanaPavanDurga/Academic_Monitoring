from django.shortcuts import redirect
from django.contrib import messages
from .models import AlumniRequest


def alumni_request(request):
    if request.method == "POST":
        AlumniRequest.objects.create(
            full_name=request.POST["full_name"],
            roll_no=request.POST["roll_no"],
            department=request.POST["department"],
            graduation_year=request.POST["graduation_year"],
        )
        messages.success(
            request,
            "Alumni request submitted successfully. Await admin verification."
        )
        return redirect("home")
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AlumniProfile, AlumniChatMessage
from students.models import StudentProfile


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from students.models import StudentProfile
from students.models import StudentProfile
from faculty.models import FacultyProfile
from .models import AlumniProfile, AlumniChatMessage, AlumniFacultyChatMessage



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from students.models import StudentProfile
from .models import AlumniProfile, AlumniChatMessage


@login_required
def alumni_chat(request, alumni_id):
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)

    student = StudentProfile.objects.filter(user=request.user).first()
    is_alumni = AlumniProfile.objects.filter(user=request.user).exists()

    # 🔒 If alumni is logged in, ensure student already initiated chat
    if is_alumni:
        alumni_user = AlumniProfile.objects.get(user=request.user)

        # Check if any student message exists
        existing_chat = AlumniChatMessage.objects.filter(
            alumni=alumni_user,
            sender="STUDENT"
        ).exists()

        if not existing_chat:
            return redirect("alumni_inbox")  # ❌ No chat started yet

        if not existing_chat:
            return redirect("alumni_inbox")

        # Get the student who initiated chat (This logic was flawed if multiple students exist)
        # But this view is for Student -> Alumni mainly.
        # If Alumni accesses this, they see... their own chat?
        # We will create a SEPARATE view for Alumni -> Student.
        pass


    # Fetch chat messages
    messages = AlumniChatMessage.objects.filter(
        student=student,
        alumni=alumni
    )

    # Handle sending message
    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            AlumniChatMessage.objects.create(
                student=student,
                alumni=alumni,
                sender="ALUMNI" if is_alumni else "STUDENT",
                message=text
            )
        return redirect("alumni_chat", alumni_id=alumni.id)

    return render(
        request,
        "alumni/chat.html",
        {
            "messages": messages,
            "alumni": alumni,
            "is_alumni": is_alumni
        }
    )


@login_required
@role_required(["ALUMNI"])
def alumni_chat_with_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    alumni = AlumniProfile.objects.get(user=request.user)

    messages = AlumniChatMessage.objects.filter(
        student=student,
        alumni=alumni
    )

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            AlumniChatMessage.objects.create(
                student=student,
                alumni=alumni,
                sender="ALUMNI",
                message=text
            )
        return redirect("alumni_chat_with_student", student_id=student.id)

    return render(
        request,
        "alumni/chat.html",
        {
            "messages": messages,
            "alumni": alumni,  # Pass myself
            "is_alumni": True,
            "target_student": student # Pass target student for UI
        }
    )


from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


@login_required
@role_required(["ALUMNI"])
def alumni_dashboard(request):
    alumni = AlumniProfile.objects.get(user=request.user)
    return render(
        request,
        "alumni/dashboard.html",
        {"alumni": alumni}
    )
from django.db.models import Q
from .models import AlumniChatMessage


from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import AlumniProfile, AlumniChatMessage, AlumniFacultyChatMessage



@login_required
@role_required(["ALUMNI"])
def alumni_inbox(request):
    alumni = AlumniProfile.objects.get(user=request.user)

    # 1. Fetch Student Chats
    student_msgs = (
        AlumniChatMessage.objects
        .filter(alumni=alumni)
        .select_related("student", "student__user")
        .order_by("-timestamp")
    )
    unique_student_chats = OrderedDict()
    for msg in student_msgs:
        if msg.student_id not in unique_student_chats:
            unique_student_chats[msg.student_id] = msg

    # 2. Fetch Faculty Chats
    faculty_msgs = (
        AlumniFacultyChatMessage.objects
        .filter(alumni=alumni)
        .select_related("faculty", "faculty__user")
        .order_by("-timestamp")
    )
    unique_faculty_chats = OrderedDict()
    for msg in faculty_msgs:
        if msg.faculty_id not in unique_faculty_chats:
            unique_faculty_chats[msg.faculty_id] = msg

    return render(
        request,
        "alumni/inbox.html",
        {
            "student_chats": unique_student_chats.values(),
            "faculty_chats": unique_faculty_chats.values(),
            "alumni": alumni
        }
    )


@login_required
@role_required(["ALUMNI"])
def alumni_chat_with_faculty(request, faculty_id):
    faculty = get_object_or_404(FacultyProfile, id=faculty_id)
    alumni = AlumniProfile.objects.get(user=request.user)

    messages = AlumniFacultyChatMessage.objects.filter(
        faculty=faculty,
        alumni=alumni
    )

    if request.method == "POST":
        text = request.POST.get("message")
        if text:
            AlumniFacultyChatMessage.objects.create(
                faculty=faculty,
                alumni=alumni,
                sender="ALUMNI",
                message=text
            )
        return redirect("alumni_chat_with_faculty", faculty_id=faculty.id)

    return render(
        request,
        "faculty/chat.html",  # Reusing faculty chat template (generic enough?)
                              # Wait, faculty/chat.html expects 'target_faculty' to show name?
                              # Let's check the template logic.
        {
            "messages": messages,
            "alumni": alumni,
            "is_alumni": True,
            "target_faculty": faculty,
            "sender_role": "ALUMNI"
        }
    )

