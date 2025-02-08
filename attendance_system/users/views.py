from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        matric_id = request.POST['matric_id']
        password = request.POST['password']

        user = authenticate(request, matric_id=matric_id, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            next_url = request.GET.get('next')  # Get the 'next' URL from GET request
            if next_url:
                return redirect(next_url)  # Redirect to the page the user tried to access
            return redirect('dashboard')  # Default redirect after login
        else:
            messages.error(request, "Invalid Matric ID or Password")

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required(login_url='/users/login/')
def dashboard_view(request):
    return render(request, 'dashboard.html')