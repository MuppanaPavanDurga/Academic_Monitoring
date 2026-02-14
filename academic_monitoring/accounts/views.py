from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UserProfile
def home(request):
    return render(request, "accounts/home.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = UserProfile.objects.get(user=user)

            if profile.role == 'STUDENT':
                return redirect('student_dashboard')
            elif profile.role == 'FACULTY':
                return redirect('faculty_dashboard')
            elif profile.role == 'HOD':
                return redirect('hod_dashboard')
            elif profile.role == 'ALUMNI':
                return redirect('alumni_dashboard')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'accounts/login.html')
