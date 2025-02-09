from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from users.models import User

class Course(models.Model):
    """Main Course Model"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    lecture_required = models.BooleanField(default=False)  # ✅ New field
    tutorial_required = models.BooleanField(default=False)  # ✅ New field
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
    duration = models.PositiveIntegerField(default=60)  # Duration in minutes

    class Meta:
        unique_together = ('course', 'section_type', 'section_number')

    def __str__(self):
        return f"{self.course.code} - {self.section_type} {self.section_number}"

    def clean(self):
        """Prevent overlapping schedules for lecturers and students."""
        if self.schedule and self.lecturer:
            end_time = self.schedule + timedelta(minutes=self.duration)

            # Check if this lecturer has another section during the same time
            overlapping_sections = Section.objects.filter(
                lecturer=self.lecturer,
                schedule__lt=end_time,
                schedule__gte=self.schedule
            ).exclude(id=self.id)  # Exclude the current section (for editing)

            if overlapping_sections.exists():
                raise ValidationError("This lecturer already has a section scheduled at this time.")

        super().clean()

class Enrollment(models.Model):
    """Tracks Student Enrollment in Sections"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'section')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.matric_id} enrolled in {self.section}"

    def clean(self):
        """Prevent students from enrolling in overlapping schedules."""
        if self.section.schedule:
            end_time = self.section.schedule + timedelta(minutes=self.section.duration)

            # Check if this student is already enrolled in another section during the same time
            overlapping_enrollments = Enrollment.objects.filter(
                student=self.student,
                section__schedule__lt=end_time,
                section__schedule__gte=self.section.schedule
            ).exclude(id=self.id)  # Exclude the current enrollment if updating

            if overlapping_enrollments.exists():
                raise ValidationError("This student is already enrolled in another section at this time.")

        super().clean()
