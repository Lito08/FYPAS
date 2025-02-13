from django.db import models
from users.models import User
from courses.models import Section
from django.utils.timezone import now
from datetime import timedelta

class Attendance(models.Model):
    """Tracks student attendance for a specific class session within a section per week."""

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Late', 'Late'),
        ('Absent', 'Absent')
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    week_number = models.IntegerField()  # ✅ Tracks week number of the class
    date = models.DateField()  # ✅ Tracks the specific class session date
    time_checked_in = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Absent')

    class Meta:
        unique_together = ('student', 'section', 'week_number')  # ✅ Prevent duplicate records per week

    def __str__(self):
        return f"{self.student.first_name} - {self.section} (Week {self.week_number}, {self.date})"

class FaceRecognitionStatus(models.Model):
    """Tracks the Face Recognition status for each section per week"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    week_number = models.IntegerField()
    is_enabled = models.BooleanField(default=False)
    enabled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('section', 'week_number')  # ✅ Ensure one entry per week

    def auto_disable(self):
        """Automatically disable Face Recognition if more than 1 minute has passed"""
        if self.is_enabled and self.enabled_at:
            if now() - self.enabled_at > timedelta(minutes=1):  
                self.is_enabled = False
                self.enabled_at = None
                self.save()

    def __str__(self):
        return f"Face Recognition {'Enabled' if self.is_enabled else 'Disabled'} - {self.section} (Week {self.week_number})"
