from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import User

def user_login(request):
    if request.method == "POST":
        matric_id = request.POST["matric_id"]
        password = request.POST["password"]
        user = authenticate(request, username=matric_id, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def user_management(request):
    if not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        matric_id = request.POST["matric_id"]
        password = request.POST["password"]
        role = request.POST["role"]

        # Ensure unique Matric ID
        if User.objects.filter(matric_id=matric_id).exists():
            return render(request, "user_management.html", {"error": "Matric ID already exists"})

        # Create User
        User.objects.create(
            username=matric_id,
            matric_id=matric_id,
            password=make_password(password),
            role=role,
        )
        return redirect("user_management")

    users = User.objects.exclude(is_superuser=True)
    return render(request, "user_management.html", {"users": users})