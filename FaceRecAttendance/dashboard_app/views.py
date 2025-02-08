from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from attendance_app.models import AttendanceRecord
from auth_app.models import User

@login_required
def dashboard(request):
    # Superadmin/Admin Dashboard
    if request.user.is_superuser or request.user.is_staff:
        total_users = User.objects.exclude(is_superuser=True).count()
        total_students = User.objects.filter(role="student").count()
        total_lecturers = User.objects.filter(role="lecturer").count()
        total_attendance_records = AttendanceRecord.objects.count()
        
        return render(request, "dashboard/admin_dashboard.html", {
            "total_users": total_users,
            "total_students": total_students,
            "total_lecturers": total_lecturers,
            "total_attendance_records": total_attendance_records
        })

    # Lecturer Dashboard
    elif request.user.role == "lecturer":
        lecturer_attendance = AttendanceRecord.objects.filter(section__course__lecturer=request.user)
        return render(request, "dashboard/lecturer_dashboard.html", {"attendance_records": lecturer_attendance})

    # Student Dashboard
    elif request.user.role == "student":
        student_attendance = AttendanceRecord.objects.filter(student=request.user)
        return render(request, "dashboard/student_dashboard.html", {"attendance_records": student_attendance})

    # If user has no role
    return render(request, "home.html")
