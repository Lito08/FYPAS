from django.urls import path
from .views import (
    take_attendance, attendance_records,
    lecturer_attendance_dashboard, weekly_attendance_view, toggle_face_recognition_weekly,
    generate_qr_attendance, manual_attendance, face_recognition_attendance
)

urlpatterns = [
    path("take/", take_attendance, name="take_attendance"),  
    path("records/", attendance_records, name="attendance_records"),  

    path("lecturer-dashboard/", lecturer_attendance_dashboard, name="lecturer_attendance_dashboard"),
    path("weekly-attendance/<int:section_id>/", weekly_attendance_view, name="weekly_attendance_view"),
    path("toggle-face-weekly/<int:section_id>/<int:week_number>/", toggle_face_recognition_weekly, name="toggle_face_recognition_weekly"),
    
    path("generate-qr/<int:section_id>/<int:week_number>/", generate_qr_attendance, name="generate_qr_attendance"),
    path("manual-attendance/<int:section_id>/<int:week_number>/", manual_attendance, name="manual_attendance"),
    path("face-recognition/<int:section_id>/<int:week_number>/", face_recognition_attendance, name="face_recognition_attendance"),
]
