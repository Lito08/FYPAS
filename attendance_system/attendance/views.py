from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Section, Enrollment
from .models import Attendance, FaceRecognitionStatus
from datetime import datetime
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse

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
        now_time = now()
        if section.schedule.date() != now_time.date():
            messages.error(request, "Attendance can only be taken on the scheduled class date.")
            return redirect("take_attendance")

        # ✅ Record attendance
        Attendance.objects.update_or_create(
            student=student,
            section=section,
            date=section.schedule.date(),
            defaults={"time_checked_in": now_time.time(), "status": "Present"},
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

@login_required(login_url="/users/login/")
def lecturer_attendance_dashboard(request):
    """Allows lecturers to select a section to manage attendance"""
    if request.user.role != "Lecturer":
        return render(request, "access_denied.html")

    sections = request.user.section_set.all()

    return render(request, "attendance/lecturer_dashboard.html", {
        "sections": sections
    })

@login_required(login_url="/users/login/")
def weekly_attendance_view(request, section_id):
    """Allows lecturers to manage attendance per week for a section"""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    weeks = range(1, 15)  # Assuming 14 weeks

    face_recognition_status = {}
    for week in weeks:
        fr_status, _ = FaceRecognitionStatus.objects.get_or_create(section=section, week_number=week)
        fr_status.auto_disable()

        face_recognition_status[week] = {
            "enabled": fr_status.is_enabled,
            "enabled_at": fr_status.enabled_at.strftime('%Y-%m-%d %H:%M:%S') if fr_status.enabled_at else None
        }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"face_recognition_status": face_recognition_status}, safe=False)

    return render(request, "attendance/weekly_attendance.html", {
        "section": section,
        "weeks": weeks,
        "face_recognition_status": face_recognition_status,
    })

@login_required(login_url="/users/login/")
def toggle_face_recognition_weekly(request, section_id, week_number):
    """Enable or disable face recognition for a specific section & week"""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    face_recognition, _ = FaceRecognitionStatus.objects.get_or_create(section=section, week_number=week_number)

    face_recognition.auto_disable()

    if face_recognition.is_enabled:
        face_recognition.is_enabled = False
        face_recognition.enabled_at = None
        status = "disabled"
    else:
        face_recognition.is_enabled = True
        face_recognition.enabled_at = now()
        status = "enabled"

    face_recognition.save()

    return JsonResponse({
        "status": status,
        "timestamp": face_recognition.enabled_at.strftime('%Y-%m-%d %H:%M:%S') if face_recognition.enabled_at else None
    })

@login_required(login_url="/users/login/")
def generate_qr_attendance(request, section_id, week_number):
    """Generates a QR code for students to check in for a specific section and week."""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    qr_data = f"{section.id}|Week{week_number}|{now().timestamp()}"
    
    qr_url = f"https://example.com/attendance/take/?data={qr_data}"

    return render(request, "attendance/generate_qr.html", {
        "section": section,
        "week_number": week_number,
        "qr_url": qr_url
    })

@login_required(login_url="/users/login/")
def manual_attendance(request, section_id, week_number):
    """Manually mark attendance for students in a specific section and week."""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    # ✅ Fetch students enrolled in this section
    students = Enrollment.objects.filter(section=section).select_related("student")

    if request.method == "POST":
        for enrollment in students:
            student = enrollment.student
            status = request.POST.get(f"status_{student.id}", "Absent")  # Default to absent

            Attendance.objects.update_or_create(
                student=student, section=section, week_number=week_number,
                defaults={"status": status, "date": now().date()}
            )

        messages.success(request, f"Attendance updated for Week {week_number} - {section}.")
        return redirect("weekly_attendance", section_id=section.id)

    return render(request, "attendance/manual_attendance.html", {
        "section": section,
        "week_number": week_number,
        "students": students
    })