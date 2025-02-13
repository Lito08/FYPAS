from django.urls import path
from .views import (
    take_attendance, attendance_records,
    lecturer_attendance_dashboard, toggle_face_recognition, generate_qr_attendance, manual_attendance
)

urlpatterns = [
    path("take/", take_attendance, name="take_attendance"),  # Student takes attendance
    path("records/", attendance_records, name="attendance_records"),  # View records
    
    path("lecturer-dashboard/", lecturer_attendance_dashboard, name="lecturer_attendance_dashboard"),
    path("toggle-face/<int:section_id>/", toggle_face_recognition, name="toggle_face_recognition"),  # Updated to toggle ON/OFF
    path("generate-qr/<int:section_id>/", generate_qr_attendance, name="generate_qr_attendance"),
    path("manual-attendance/<int:section_id>/", manual_attendance, name="manual_attendance"),
]
