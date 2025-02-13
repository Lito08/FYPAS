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

@login_required(login_url="/users/login/")
def lecturer_attendance_dashboard(request):
    """Allows lecturers to select a section to manage attendance"""
    if request.user.role != "Lecturer":
        return render(request, "access_denied.html")

    sections = request.user.section_set.all()
    face_recognition_status = {}

    for section in sections:
        fr_status, _ = FaceRecognitionStatus.objects.get_or_create(section=section)

        # ✅ Auto-disable before displaying
        fr_status.auto_disable()

        # ✅ Store the latest data to ensure the UI updates
        face_recognition_status[section.id] = {
            "enabled": fr_status.is_enabled,
            "enabled_at": fr_status.enabled_at,
        }

    return render(request, "attendance/lecturer_dashboard.html", {
        "sections": sections,
        "face_recognition_status": face_recognition_status
    })

@login_required(login_url="/users/login/")
def toggle_face_recognition(request, section_id):
    """Enable or disable face recognition attendance for a specific section"""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)
    face_recognition, created = FaceRecognitionStatus.objects.get_or_create(section=section)

    # ✅ Auto-disable if 1-minute has passed
    face_recognition.auto_disable()

    if face_recognition.is_enabled:
        # Disable face recognition
        face_recognition.is_enabled = False
        face_recognition.enabled_at = None
        response_data = {"status": "disabled"}
    else:
        # Enable face recognition and save timestamp
        face_recognition.is_enabled = True
        face_recognition.enabled_at = now()
        response_data = {
            "status": "enabled",
            "timestamp": face_recognition.enabled_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    face_recognition.save()
    return JsonResponse(response_data)

@login_required(login_url="/users/login/")
def generate_qr_attendance(request, section_id):
    """Generate QR code for attendance"""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)

    # Logic to generate QR code (to be implemented)
    messages.success(request, f"QR Code generated for {section}.")
    return redirect("lecturer_attendance_dashboard")

@login_required(login_url="/users/login/")
def manual_attendance(request, section_id):
    """Manually take attendance for a specific class session within a section."""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)
    students = Enrollment.objects.filter(section=section).select_related('student')

    if request.method == "POST":
        week_number = int(request.POST.get("week_number"))
        date = request.POST.get("date")

        for student in students:
            status = request.POST.get(f"status_{student.student.id}")

            Attendance.objects.update_or_create(
                student=student.student,
                section=section,
                date=date,
                week_number=week_number,
                defaults={"status": status, "time_checked_in": datetime.now().time()},
            )

        messages.success(request, f"Attendance saved for {section} (Week {week_number}, {date})")
        return redirect("lecturer_attendance_dashboard")

    return render(request, "attendance/manual_attendance.html", {
        "section": section,
        "students": students,
    })
