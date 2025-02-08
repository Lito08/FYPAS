from django import forms
from .models import Course, Section, Class

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'lecturer']  # Include the lecturer field
        widgets = {
            'lecturer': forms.Select(attrs={'required': False}),  # Make lecturer field optional
        }

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # Make lecturer field not required
        self.fields['lecturer'].required = False

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_type', 'schedule']
        widgets = {
            'schedule': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # This will display a date & time picker
        }

# Form for Class
class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_date', 'class_time']
