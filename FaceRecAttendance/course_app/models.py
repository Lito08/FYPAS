from django.db import models
from auth_app.models import User  # Import the custom User model

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.course_name

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=10, choices=[("lecture", "Lecture"), ("tutorial", "Tutorial")])
    schedule = models.DateTimeField()

    def __str__(self):
        return f"{self.course.course_name} - {self.section_type}"
