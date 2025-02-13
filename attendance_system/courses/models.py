from datetime import timedelta, datetime
from django.db import models
from django.core.exceptions import ValidationError
from users.models import User

class Course(models.Model):
    """Main Course Model"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    lecture_required = models.BooleanField(default=False)
    tutorial_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    """Course Sections (Lectures/Tutorials)"""
    SECTION_TYPES = [
        ('Lecture', 'Lecture'),
        ('Tutorial', 'Tutorial'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=10, choices=SECTION_TYPES)
    section_number = models.IntegerField()
    lecturer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Lecturer'})
    start_date = models.DateField(null=True, blank=True)  # ✅ First class session
    class_time = models.TimeField(null=True, blank=True)  # ✅ Time for each session
    duration = models.PositiveIntegerField(default=60)  # Duration in minutes
    max_students = models.PositiveIntegerField(default=30)  # ✅ Section-based student limit

    class Meta:
        unique_together = ('course', 'section_type', 'section_number')

    def __str__(self):
        return f"{self.course.code} - {self.section_type} {self.section_number}"

    def clean(self):
        """Prevent overlapping schedules for lecturers."""
        if self.start_date and self.class_time and self.lecturer:
            # ✅ Convert class_time to datetime before adding timedelta
            start_datetime = datetime.combine(self.start_date, self.class_time)
            end_datetime = start_datetime + timedelta(minutes=self.duration)  

            # ✅ Find overlapping sections
            overlapping_sections = Section.objects.filter(
                lecturer=self.lecturer,
                start_date=self.start_date,
                class_time__lt=end_datetime.time(),
                class_time__gte=self.class_time
            ).exclude(id=self.id)

            if overlapping_sections.exists():
                raise ValidationError("This lecturer already has a section scheduled at this time.")

        super().clean()

class ClassSession(models.Model):
    """Automatically Generated Weekly Class Sessions for Each Section"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="sessions")
    week_number = models.IntegerField()
    date = models.DateField()
    start_time = models.TimeField()

    class Meta:
        unique_together = ('section', 'week_number')

    def __str__(self):
        return f"{self.section} - Week {self.week_number} ({self.date})"

class Enrollment(models.Model):
    """Tracks Student Enrollment in Sections"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'section')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.matric_id} enrolled in {self.section}"

    def clean(self):
        """Prevent students from enrolling in overlapping schedules and full sections."""
        if self.section.start_date:
            # ✅ Convert class_time to datetime for accurate comparison
            start_datetime = datetime.combine(self.section.start_date, self.section.class_time)
            end_datetime = start_datetime + timedelta(minutes=self.section.duration)

            overlapping_enrollments = Enrollment.objects.filter(
                student=self.student,
                section__start_date=self.section.start_date,
                section__class_time__lt=end_datetime.time(),
                section__class_time__gte=self.section.class_time
            ).exclude(id=self.id)

            if overlapping_enrollments.exists():
                raise ValidationError("This student is already enrolled in another section at this time.")

        # ✅ Check if the section has reached maximum capacity
        enrolled_students = Enrollment.objects.filter(section=self.section).count()
        if enrolled_students >= self.section.max_students:
            raise ValidationError(f"The section {self.section.section_type} {self.section.section_number} is full. Please select another section.")

        super().clean()

class EnrollmentCart(models.Model):
    """Temporary cart for student self-enrollment before final submission."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecture_section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name="cart_lecture")
    tutorial_section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name="cart_tutorial")

    class Meta:
        unique_together = ('student', 'course')  # Ensure only one selection per course

    def __str__(self):
        return f"{self.student.matric_id} - {self.course.name} (Lecture: {self.lecture_section}, Tutorial: {self.tutorial_section})"

    def clean(self):
        """Prevent students from adding incomplete selections and conflicting sections to their cart."""
        cart_items = EnrollmentCart.objects.filter(student=self.student).exclude(id=self.id)

        # ✅ Ensure course requirements are met before allowing finalization
        if not self.lecture_section:
            raise ValidationError(f"⚠️ You must select a Lecture section for {self.course.name}.")
        if self.course.tutorial_required and not self.tutorial_section:
            raise ValidationError(f"⚠️ You must select a Tutorial section for {self.course.name}.")

        # ✅ Check for schedule conflicts
        for cart_item in cart_items:
            if self.lecture_section and cart_item.lecture_section:
                start_dt1 = datetime.combine(self.lecture_section.start_date, self.lecture_section.class_time)
                end_dt1 = start_dt1 + timedelta(minutes=self.lecture_section.duration)
                start_dt2 = datetime.combine(cart_item.lecture_section.start_date, cart_item.lecture_section.class_time)
                end_dt2 = start_dt2 + timedelta(minutes=cart_item.lecture_section.duration)

                if (start_dt1 < end_dt2 and start_dt2 < end_dt1):
                    raise ValidationError(f"⚠️ Lecture {self.lecture_section.section_number} conflicts with Lecture {cart_item.lecture_section.section_number}.")

            if self.tutorial_section and cart_item.tutorial_section:
                start_dt1 = datetime.combine(self.tutorial_section.start_date, self.tutorial_section.class_time)
                end_dt1 = start_dt1 + timedelta(minutes=self.tutorial_section.duration)
                start_dt2 = datetime.combine(cart_item.tutorial_section.start_date, cart_item.tutorial_section.class_time)
                end_dt2 = start_dt2 + timedelta(minutes=cart_item.tutorial_section.duration)

                if (start_dt1 < end_dt2 and start_dt2 < end_dt1):
                    raise ValidationError(f"⚠️ Tutorial {self.tutorial_section.section_number} conflicts with Tutorial {cart_item.tutorial_section.section_number}.")

        # ✅ Ensure the selected section is not already full
        if self.lecture_section and Enrollment.objects.filter(section=self.lecture_section).count() >= self.lecture_section.max_students:
            raise ValidationError(f"⚠️ Lecture section {self.lecture_section.section_number} is full. Please select another.")

        if self.tutorial_section and Enrollment.objects.filter(section=self.tutorial_section).count() >= self.tutorial_section.max_students:
            raise ValidationError(f"⚠️ Tutorial section {self.tutorial_section.section_number} is full. Please select another.")

        super().clean()
