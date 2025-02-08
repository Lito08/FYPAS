from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

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
