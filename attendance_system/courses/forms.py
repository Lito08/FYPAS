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
        required=True,  # ✅ Class hours are required
        min_value=30,  # ✅ Minimum class duration (30 minutes)
        max_value=300,  # ✅ Maximum class duration (5 hours)
        widget=forms.NumberInput(attrs={'placeholder': 'Enter class duration in minutes'})
    )

    class Meta:
        model = Section
        fields = ['course', 'section_type', 'section_number', 'lecturer', 'schedule', 'duration']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'section']
