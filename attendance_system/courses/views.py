from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Section, Enrollment
from .forms import CourseForm, SectionForm, EnrollmentForm

# 🔹 MANAGE COURSES
@login_required(login_url='/users/login/')
def manage_courses_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    courses = Course.objects.all()
    return render(request, 'courses/manage_courses.html', {'courses': courses})

@login_required(login_url='/users/login/')
def create_course_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()

            # ✅ Auto-create Lecture Section
            if course.lecture_required:
                Section.objects.create(
                    course=course,
                    section_type='Lecture',
                    section_number=1,  # Default section number
                    schedule=None,  # Can be set later
                    duration=60  # Default 1 hour
                )

            # ✅ Auto-create Tutorial Section
            if course.tutorial_required:
                Section.objects.create(
                    course=course,
                    section_type='Tutorial',
                    section_number=1,  # Default section number
                    schedule=None,  # Can be set later
                    duration=60  # Default 1 hour
                )

            messages.success(request, "Course and required sections created successfully!")
            return redirect('manage_courses')
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})

@login_required(login_url='/users/login/')
def edit_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()

            # ✅ Handle Lecture Section Creation/Deletion
            if course.lecture_required:
                Section.objects.get_or_create(
                    course=course,
                    section_type='Lecture',
                    section_number=1,  # Default section number
                    defaults={'schedule': None, 'duration': 60}
                )
            else:
                Section.objects.filter(course=course, section_type='Lecture').delete()

            # ✅ Handle Tutorial Section Creation/Deletion
            if course.tutorial_required:
                Section.objects.get_or_create(
                    course=course,
                    section_type='Tutorial',
                    section_number=1,  # Default section number
                    defaults={'schedule': None, 'duration': 60}
                )
            else:
                Section.objects.filter(course=course, section_type='Tutorial').delete()

            messages.success(request, "Course and sections updated successfully!")
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/edit_course.html', {'form': form})

@login_required(login_url='/users/login/')
def delete_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully!")
    return redirect('manage_courses')

@login_required(login_url='/users/login/')
def view_course_sections_view(request, course_id):
    """Displays all sections related to a specific course."""
    course = get_object_or_404(Course, id=course_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    sections = Section.objects.filter(course=course)
    return render(request, 'courses/view_course_sections.html', {'course': course, 'sections': sections})

# 🔹 MANAGE SECTIONS SEPARATELY
@login_required(login_url='/users/login/')
def manage_sections_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    sections = Section.objects.all()
    return render(request, 'courses/manage_sections.html', {'sections': sections})

@login_required(login_url='/users/login/')
def create_section_view(request, course_id=None):
    """Allows Admins to create a section for a specific course."""
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    course = None
    if course_id:
        course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            if course:
                section.course = course  # ✅ Automatically assign the course
            section.save()
            messages.success(request, "Section created successfully!")
            return redirect('view_course_sections', course_id=course.id)
    else:
        form = SectionForm(initial={'course': course})  # ✅ Prefill course field if provided

    return render(request, 'courses/create_section.html', {'form': form, 'course': course})

@login_required(login_url='/users/login/')
def edit_section_view(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated successfully!")
            return redirect('manage_sections')
    else:
        form = SectionForm(instance=section)

    return render(request, 'courses/edit_section.html', {'form': form})

@login_required(login_url='/users/login/')
def delete_section_view(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    section.delete()
    messages.success(request, "Section deleted successfully!")
    return redirect('manage_sections')

# 🔹 MANAGE ENROLLMENT
@login_required(login_url='/users/login/')
def manage_enrollments_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    enrollments = Enrollment.objects.all()
    return render(request, 'courses/manage_enrollments.html', {'enrollments': enrollments})

@login_required(login_url='/users/login/')
def enroll_student_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student enrolled successfully!")
            return redirect('manage_enrollments')
    else:
        form = EnrollmentForm()

    return render(request, 'courses/enroll_student.html', {'form': form})

@login_required(login_url='/users/login/')
def unenroll_student_view(request, enrollment_id):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.delete()
    messages.success(request, "Student unenrolled successfully!")
    return redirect('manage_enrollments')

@login_required(login_url='/users/login/')
def student_enroll_view(request):
    """Allows students to self-enroll in sections while ensuring no schedule conflicts."""
    if request.user.role != 'Student':  # ✅ Only students can access this page
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user  # ✅ Explicitly set the student before saving
            enrollment.save()
            messages.success(request, "You have successfully enrolled in the section!")
            return redirect('student_enrollment')
    else:
        form = EnrollmentForm()

    return render(request, 'courses/student_enroll.html', {'form': form})
