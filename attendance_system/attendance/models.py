from django.db import models
from users.models import User
from courses.models import Section

class Attendance(models.Model):
    """Tracks student attendance for a section"""
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Absent', 'Absent')
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_checked_in = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    def __str__(self):
        return f"{self.student.first_name} - {self.section} ({self.status})"
