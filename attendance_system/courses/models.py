from django.db import models
from users.models import User  # Import User model

class Course(models.Model):
    """Main Course Model"""
    code = models.CharField(max_length=10, unique=True)  # e.g., "CS101"
    name = models.CharField(max_length=100)  # e.g., "Computer Science 101"
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    """Course Sections (Lectures/Tutorials/Labs)"""
    SECTION_TYPES = [
        ('Lecture', 'Lecture'),
        ('Tutorial', 'Tutorial'),
        ('Lab', 'Lab')
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=10, choices=SECTION_TYPES)
    section_number = models.IntegerField()
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Lecturer'})
    schedule = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=60)  # ✅ New field (Duration in minutes)

    class Meta:
        unique_together = ('course', 'section_type', 'section_number')

    def __str__(self):
        return f"{self.course.code} - {self.section_type} {self.section_number}"

class Enrollment(models.Model):
    """Tracks Student Enrollment in Sections"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'section')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.matric_id} enrolled in {self.section}"
