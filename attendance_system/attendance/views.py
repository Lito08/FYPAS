from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Section, Enrollment
from .models import Attendance
from datetime import datetime

@login_required(login_url="/users/login/")
def enable_attendance(request, section_id):
    """Allows the lecturer to enable attendance for a section."""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    if request.user.role != "Lecturer":
        return render(request, "access_denied.html")

    # ✅ Ensure attendance can only be enabled for scheduled classes
    if section.schedule is None:
        messages.error(request, "Cannot enable attendance. This section is not scheduled yet.")
        return redirect("attendance_records")

    # ✅ Enable attendance for the section
    messages.success(request, f"Attendance enabled for {section}. Students can now check in.")
    return redirect("attendance_records")

@login_required(login_url="/users/login/")
def take_attendance(request):
    """Allows students to take attendance for their ongoing class."""
    if request.user.role != "Student":
        return render(request, "access_denied.html")

    student = request.user
    enrollments = Enrollment.objects.filter(student=student, section__schedule__isnull=False)

    if request.method == "POST":
        section_id = request.POST.get("section_id")
        section = get_object_or_404(Section, id=section_id)

        # ✅ Ensure the class is ongoing
        now = datetime.now()
        if section.schedule.date() != now.date():
            messages.error(request, "Attendance can only be taken on the scheduled class date.")
            return redirect("take_attendance")

        # ✅ Record attendance
        Attendance.objects.update_or_create(
            student=student,
            section=section,
            date=section.schedule.date(),
            defaults={"time_checked_in": now.time(), "status": "Present"},
        )

        messages.success(request, f"You have successfully checked in for {section}.")
        return redirect("student_schedule")

    return render(request, "attendance/take_attendance.html", {"enrollments": enrollments})

@login_required(login_url="/users/login/")
def attendance_records(request):
    """Displays attendance records for lecturers or students."""
    if request.user.role == "Lecturer":
        records = Attendance.objects.filter(section__lecturer=request.user)
    elif request.user.role == "Student":
        records = Attendance.objects.filter(student=request.user)
    else:
        return render(request, "access_denied.html")

    return render(request, "attendance/attendance_records.html", {"records": records})
