from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm

def login_view(request):
    if request.method == 'POST':
        matric_id = request.POST['matric_id']
        password = request.POST['password']

        user = authenticate(request, matric_id=matric_id, password=password)

        if user is not None:
            login(request, user)

            # ✅ If first login, redirect to password change page
            if user.first_login:
                return redirect('change_password')  # Redirect to password change page
            
            messages.success(request, "Login successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Matric ID or Password")

    return render(request, 'users/login.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            user.first_login = False  # ✅ Mark as password changed
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Password updated successfully!")
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required(login_url='/users/login/')
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/users/login/')
def manage_users_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')  # Restrict access for non-superadmin/admin users

    # Retrieve users categorized by role
    students = User.objects.filter(role="Student")
    lecturers = User.objects.filter(role="Lecturer")
    admins = User.objects.filter(role="Admin") if request.user.role == "Superadmin" else None  # Hide Admins from Admin users

    context = {
        'students': students,
        'lecturers': lecturers,
        'admins': admins,
    }

    return render(request, 'users/manage_users.html', context)

@login_required(login_url='/users/login/')
def create_user_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user, temp_password = form.save()

            # Send credentials to the user's PERSONAL email
            subject = "Your University System Account Credentials"
            message = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"Your university account has been created.\n"
                f"Matric ID: {user.matric_id}\n"
                f"Login Email: {user.email}\n"
                f"Temporary Password: {temp_password}\n\n"
                f"Please log in and change your password immediately.\n\n"
                f"Best Regards,\nUniversity Administration"
            )

            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.personal_email])

            messages.success(request, "User created successfully! Credentials have been sent to the personal email.")
            return redirect('manage_users')
        else:
            messages.error(request, "Failed to create user. Please fix the errors below.")

    else:
        form = UserCreationForm()

    return render(request, 'users/create_user.html', {'form': form})

@login_required(login_url='/users/login/')
def edit_user_view(request, user_id):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    user = get_object_or_404(User, id=user_id)

    # ✅ Prevent Admins from editing other Admins
    if request.user.role == 'Admin' and user.role == 'Admin':  
        messages.error(request, "You are not allowed to edit other Admins.")
        return redirect('manage_users')

    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User details updated successfully!")
            return redirect('manage_users')
        else:
            messages.error(request, "Failed to update user. Please fix the errors below.")
    else:
        form = UserCreationForm(instance=user)

    return render(request, 'users/edit_user.html', {'form': form, 'user': user})

@login_required(login_url='/users/login/')
def delete_user_view(request, user_id):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    user = get_object_or_404(User, id=user_id)

    if request.user.role == 'Admin' and user.role == 'Admin':
        return render(request, 'access_denied.html')  # Admins cannot delete other Admins

    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect('manage_users')
