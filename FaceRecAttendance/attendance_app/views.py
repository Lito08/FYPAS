import cv2
import numpy as np
import face_recognition
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import AttendanceRecord, User, Section
import os

def take_attendance(request):
    return render(request, "take_attendance.html")

@csrf_exempt
def recognize_face(request):
    if request.method == "POST" and request.FILES.get("image"):
        file = request.FILES["image"]
        file_name = default_storage.save(f"temp/{file.name}", ContentFile(file.read()))
        file_path = default_storage.path(file_name)

        # Load the uploaded image
        img = face_recognition.load_image_file(file_path)
        face_encodings = face_recognition.face_encodings(img)

        # Cleanup: Remove temp file
        os.remove(file_path)

        if not face_encodings:
            return JsonResponse({"message": "No face detected"}, status=400)

        # Fetch all stored student face encodings from the database
        students = User.objects.filter(role="student")
        for student in students:
            if student.face_encoding:  # Ensure the student has a stored face encoding
                stored_encoding = np.frombuffer(student.face_encoding, dtype=np.float64)
                match = face_recognition.compare_faces([stored_encoding], face_encodings[0])[0]

                if match:
                    # Mark attendance
                    AttendanceRecord.objects.create(student=student, status="present")
                    return JsonResponse({"message": f"Attendance marked for {student.matric_id}"})

        return JsonResponse({"message": "Face not recognized"}, status=400)

    return JsonResponse({"message": "Invalid request"}, status=400)

def attendance_records(request):
    records = AttendanceRecord.objects.all()
    return render(request, "attendance_records.html", {"records": records})