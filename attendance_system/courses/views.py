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
            form.save()
            messages.success(request, "Course created successfully!")
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
            form.save()
            messages.success(request, "Course updated successfully!")
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

# 🔹 MANAGE SECTIONS SEPARATELY
@login_required(login_url='/users/login/')
def manage_sections_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    sections = Section.objects.all()
    return render(request, 'courses/manage_sections.html', {'sections': sections})

@login_required(login_url='/users/login/')
def create_section_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Section created successfully!")
            return redirect('manage_sections')
    else:
        form = SectionForm()

    return render(request, 'courses/create_section.html', {'form': form})

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
