from django import forms
from .models import Course, Section, Enrollment

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description']

class SectionForm(forms.ModelForm):
    schedule = forms.DateTimeField(
        required=False,  # ✅ Makes schedule optional
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Section
        fields = ['course', 'section_type', 'section_number', 'lecturer', 'schedule']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'section']
