from django import forms
from .models import Course, Section, Enrollment
from datetime import timedelta

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'lecture_required', 'tutorial_required']  # ✅ Added checkboxes

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
        fields = ['section']

    def __init__(self, *args, **kwargs):
        """Filter available sections for the student."""
        self.student = kwargs.pop('student', None)  # ✅ Extract student from kwargs
        super().__init__(*args, **kwargs)

        if self.student:
            # ✅ Get enrolled sections for the student
            enrolled_sections = Enrollment.objects.filter(student=self.student).values_list('section__schedule', 'section__duration')
            unavailable_times = []

            for schedule, duration in enrolled_sections:
                if schedule and duration:  # ✅ Ensure schedule is not None
                    unavailable_times.append((schedule, schedule + timedelta(minutes=duration)))

            # ✅ Filter out sections that overlap with the student's existing schedule
            if unavailable_times:
                self.fields['section'].queryset = Section.objects.exclude(
                    schedule__isnull=False,
                    schedule__range=[t[0] for t in unavailable_times]
                )

    def clean(self):
        """Run additional validation for student schedule conflicts."""
        cleaned_data = super().clean()
        section = cleaned_data.get("section")

        if self.student and section:
            try:
                enrollment = Enrollment(student=self.student, section=section)
                enrollment.clean()  # Call the model validation
            except forms.ValidationError as e:
                raise forms.ValidationError(e)

        return cleaned_data

