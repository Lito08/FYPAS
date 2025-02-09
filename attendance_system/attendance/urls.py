from django.urls import path
from .views import take_attendance, enable_attendance, attendance_records

urlpatterns = [
    path("take/", take_attendance, name="take_attendance"),  # Student takes attendance
    path("enable/<int:section_id>/", enable_attendance, name="enable_attendance"),  # Lecturer enables attendance
    path("records/", attendance_records, name="attendance_records"),  # View records
]
