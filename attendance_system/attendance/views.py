from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Section, Enrollment, ClassSession
from users.models import User
from .models import Attendance, FaceRecognitionStatus
from django.utils.timezone import now
import qrcode
import io
import base64
from django.http import JsonResponse

@login_required(login_url="/users/login/")
def take_attendance(request):
    """Allows students to take attendance for their ongoing class using QR code."""
    if request.user.role != "Student":
        return render(request, "access_denied.html")

    student = request.user
    section_id = request.GET.get("section_id")
    week_number = request.GET.get("week")

    # ✅ Validate input
    if not section_id or not week_number:
        messages.error(request, "Invalid QR Code data.")
        return redirect("student_schedule")

    # ✅ Ensure section exists
    section = get_object_or_404(Section, id=section_id)
    
    # ✅ Ensure student is enrolled
    if not Enrollment.objects.filter(student=student, section=section).exists():
        messages.error(request, "You are not enrolled in this section.")
        return redirect("student_schedule")

    # ✅ Check if `ClassSession` exists
    class_session = ClassSession.objects.filter(section=section, week_number=week_number).first()
    if not class_session:
        messages.error(request, f"No scheduled class for {section} in Week {week_number}.")
        return redirect("student_schedule")

    # ✅ Record attendance
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        section=section,
        date=class_session.date,  # Use correct session date
        week_number=week_number,
        defaults={"time_checked_in": now().time(), "status": "Present"},
    )

    if not created:
        messages.info(request, f"Attendance already recorded for {section} - Week {week_number}.")
    else:
        messages.success(request, f"You have successfully checked in for {section} - Week {week_number}.")

    return redirect("student_schedule")

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

    # ✅ Get the base URL of your Django app
    base_url = request.build_absolute_uri('/')[:-1]  # Removes the trailing slash

    # ✅ Generate the QR Code Data (Actual Check-in URL)
    qr_data = f"{base_url}/attendance/take/?section_id={section.id}&week={week_number}&timestamp={now().timestamp()}"

    # ✅ Create QR Code
    qr = qrcode.make(qr_data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "attendance/generate_qr.html", {
        "section": section,
        "week_number": week_number,
        "qr_base64": qr_base64,  # ✅ Pass QR Code as Base64 to the template
        "qr_data": qr_data,  # ✅ Pass the URL for debugging
    })

@login_required(login_url="/users/login/")
def manual_attendance(request, section_id, week_number):
    """Manually mark attendance for students in a specific section and week."""
    section = get_object_or_404(Section, id=section_id, lecturer=request.user)
    students = User.objects.filter(enrollment__section=section, role="Student")  # ✅ Get enrolled students

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}", "Absent")  # Default is absent
            Attendance.objects.update_or_create(
                student=student, section=section, week_number=week_number,
                defaults={"status": status, "date": now().date()}
            )
        messages.success(request, f"Attendance updated for Week {week_number} - {section}.")
        return redirect("weekly_attendance_view", section_id=section.id)

    return render(request, "attendance/manual_attendance.html", {
        "section": section,
        "week_number": week_number,
        "students": students  # ✅ Pass students to the template
    })
