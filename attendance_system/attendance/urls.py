from django.urls import path
from .views import (
    take_attendance, enable_attendance, attendance_records,
    lecturer_attendance_dashboard, enable_face_recognition, generate_qr_attendance, manual_attendance
)

urlpatterns = [
    path("take/", take_attendance, name="take_attendance"),  # Student takes attendance
    path("records/", attendance_records, name="attendance_records"),  # View records
    
    path("lecturer-dashboard/", lecturer_attendance_dashboard, name="lecturer_attendance_dashboard"),
    path("enable-face/<int:section_id>/", enable_face_recognition, name="enable_face_recognition"),
    path("generate-qr/<int:section_id>/", generate_qr_attendance, name="generate_qr_attendance"),
    path("manual-attendance/<int:section_id>/", manual_attendance, name="manual_attendance"),
]
