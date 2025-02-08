from django import forms
from .models import Course, Section, Enrollment

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description']

class SectionForm(forms.ModelForm):
    schedule = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    duration = forms.IntegerField(
        required=True,
        min_value=30,  # Minimum 30 minutes
        max_value=300,  # Maximum 5 hours
        widget=forms.NumberInput(attrs={'placeholder': 'Enter class duration in minutes'})
    )

    class Meta:
        model = Section
        fields = ['course', 'section_type', 'section_number', 'lecturer', 'schedule', 'duration']

    def clean(self):
        """Run additional validation for schedule conflicts."""
        cleaned_data = super().clean()
        schedule = cleaned_data.get("schedule")
        lecturer = cleaned_data.get("lecturer")

        if schedule and lecturer:
            try:
                section = Section(
                    course=cleaned_data["course"],
                    section_type=cleaned_data["section_type"],
                    section_number=cleaned_data["section_number"],
                    lecturer=lecturer,
                    schedule=schedule,
                    duration=cleaned_data["duration"]
                )
                section.clean()  # Call the model validation
            except forms.ValidationError as e:
                raise forms.ValidationError(e)

        return cleaned_data

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'section']

    def clean(self):
        """Run additional validation for student schedule conflicts."""
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        section = cleaned_data.get("section")

        if student and section:
            try:
                enrollment = Enrollment(student=student, section=section)
                enrollment.clean()  # Call the model validation
            except forms.ValidationError as e:
                raise forms.ValidationError(e)

        return cleaned_data