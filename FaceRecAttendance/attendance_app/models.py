from django.db import models
from auth_app.models import User  # Import the User model
from course_app.models import Section  # Import the Section model

class AttendanceRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance_records")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[("present", "Present"), ("absent", "Absent")])

    def __str__(self):
        return f"{self.student.matric_id} - {self.section.course.course_name} ({self.date})"
