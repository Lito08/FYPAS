from django import forms
from .models import Course, Section, Enrollment, EnrollmentCart
from datetime import timedelta

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'lecture_required', 'tutorial_required']

class SectionForm(forms.ModelForm):
    schedule = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    duration = forms.IntegerField(
        required=True,
        min_value=30,
        max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter class duration in minutes'})
    )

    max_students = forms.IntegerField(
        required=True,
        min_value=5,
        max_value=500,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter max students per section'})
    )

    class Meta:
        model = Section
        fields = ['course', 'section_type', 'section_number', 'lecturer', 'schedule', 'duration', 'max_students']

    def clean(self):
        """Validate schedule conflicts and ensure correct section limits."""
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
                    duration=cleaned_data["duration"],
                    max_students=cleaned_data["max_students"]
                )
                section.clean()
            except forms.ValidationError as e:
                raise forms.ValidationError(e)

        return cleaned_data

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['section']

    def __init__(self, *args, **kwargs):
        """Filter available sections for the student."""
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

        if self.student:
            enrolled_sections = Enrollment.objects.filter(student=self.student).values_list('section__schedule', 'section__duration')
            unavailable_times = []

            for schedule, duration in enrolled_sections:
                if schedule and duration:
                    unavailable_times.append((schedule, schedule + timedelta(minutes=duration)))

            if unavailable_times:
                self.fields['section'].queryset = Section.objects.exclude(
                    schedule__isnull=False,
                    schedule__range=[t[0] for t in unavailable_times]
                )

    def clean(self):
        """Ensure section availability before enrolling."""
        cleaned_data = super().clean()
        section = cleaned_data.get("section")

        if self.student and section:
            try:
                enrolled_students = Enrollment.objects.filter(section=section).count()
                if enrolled_students >= section.max_students:
                    raise forms.ValidationError(f"The section {section.section_type} {section.section_number} is full. Please select another section.")

                enrollment = Enrollment(student=self.student, section=section)
                enrollment.clean()
            except forms.ValidationError as e:
                raise forms.ValidationError(e)

        return cleaned_data

class EnrollmentCartForm(forms.ModelForm):
    """Handles adding lecture/tutorial sections separately to the cart."""
    
    class Meta:
        model = EnrollmentCart
        fields = ['lecture_section', 'tutorial_section']

    def __init__(self, *args, **kwargs):
        """Ensure students can only select valid sections."""
        self.student = kwargs.pop('student', None)
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

        if course:
            # ✅ Filter available lecture sections for this course
            self.fields['lecture_section'].queryset = Section.objects.filter(course=course, section_type='Lecture')

            # ✅ Filter available tutorial sections for this course
            self.fields['tutorial_section'].queryset = Section.objects.filter(course=course, section_type='Tutorial')

    def clean(self):
        """Validate section availability before adding to cart."""
        cleaned_data = super().clean()
        lecture_section = cleaned_data.get("lecture_section")
        tutorial_section = cleaned_data.get("tutorial_section")

        # ✅ Ensure at least one section is selected
        if not lecture_section and not tutorial_section:
            raise forms.ValidationError("You must select at least one section (Lecture or Tutorial).")

        # ✅ Ensure sections are not full
        if lecture_section and Enrollment.objects.filter(section=lecture_section).count() >= lecture_section.max_students:
            raise forms.ValidationError(f"Lecture section {lecture_section.section_number} is full. Please select another.")

        if tutorial_section and Enrollment.objects.filter(section=tutorial_section).count() >= tutorial_section.max_students:
            raise forms.ValidationError(f"Tutorial section {tutorial_section.section_number} is full. Please select another.")

        return cleaned_data

