from django.urls import path
from .views import take_attendance, attendance_records, recognize_face

urlpatterns = [
    path("take/", take_attendance, name="take_attendance"),
    path("records/", attendance_records, name="attendance_records"),
    path("recognize/", recognize_face, name="recognize_face"),
]
