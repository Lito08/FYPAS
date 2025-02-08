from django.db import models
from auth_app.models import User  # Import the custom User model

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses", null=True, blank=True)  # Make lecturer optional

    def __str__(self):
        return self.course_name

class Section(models.Model):
    COURSE_TYPE_CHOICES = [
        ("lecture", "Lecture"),
        ("tutorial", "Tutorial")
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES)
    schedule = models.DateTimeField()

    def __str__(self):
        return f"{self.course.course_name} - {self.section_type}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'schedule'], name='unique_course_schedule')
        ]
        # Ensures no two sections of the same course can have overlapping schedules

class Class(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="classes")
    class_date = models.DateField()
    class_time = models.TimeField()

    def __str__(self):
        return f"{self.section.course.course_name} - {self.class_date} {self.class_time}"

    class Meta:
        unique_together = ['section', 'class_date', 'class_time']
        # Ensures no two classes for the same section can have the same date and time
