from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Section, Class
from .forms import CourseForm, SectionForm, ClassForm
from django.contrib.auth.decorators import login_required

# View for adding a new course (restricted to admins)
@login_required
def add_course(request):
    if not request.user.is_superuser:  # Ensure only admin can add courses
        return redirect('course_list')  # Redirect to course list if not admin

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')  # Redirect to course list after saving
    else:
        form = CourseForm()

    return render(request, "add_course.html", {"form": form})

# View for adding a section to a course (restricted to admins)
@login_required
def add_section(request, course_id):
    course = Course.objects.get(id=course_id)

    # Check if the schedule already exists for the course
    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course

            # Check if a section with the same course and schedule already exists
            if Section.objects.filter(course=course, schedule=section.schedule).exists():
                # If it exists, show an error message and redirect
                messages.error(request, "A section with this schedule already exists for this course.")
                return redirect('course_details', course_id=course.id)

            section.save()
            return redirect('course_details', course_id=course.id)
    else:
        form = SectionForm()

    return render(request, "add_section.html", {"form": form, "course": course})

# View for adding a class to a section (restricted to admins)
@login_required
def add_class(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            _class = form.save(commit=False)
            _class.section = section
            _class.save()
            return redirect('edit_course', course_id=section.course.id)
    else:
        form = ClassForm()

    return render(request, 'add_class.html', {'form': form, 'section': section})

# View for editing a course and managing sections/classes
@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course_form = CourseForm(request.POST, instance=course)
        if course_form.is_valid():
            course_form.save()
            return redirect('course_details', course_id=course.id)
    else:
        course_form = CourseForm(instance=course)

    sections = course.sections.all()  # Get all sections for this course
    section_form = SectionForm()

    # Handle adding a new section if POST request
    if request.method == 'POST' and 'add_section' in request.POST:
        section_form = SectionForm(request.POST)
        if section_form.is_valid():
            section = section_form.save(commit=False)
            section.course = course
            section.save()
            return redirect('edit_course', course_id=course.id)

    return render(request, 'edit_course.html', {
        'course_form': course_form,
        'course': course,
        'sections': sections,
        'section_form': section_form
    })

# View for listing all courses (accessible by admins and lecturers)
@login_required
def course_list(request):
    if request.user.is_superuser:
        courses = Course.objects.all()  # Admin sees all courses
    elif request.user.role == 'lecturer':
        courses = Course.objects.filter(lecturer=request.user)  # Lecturer sees only their own courses
    else:
        courses = []  # Students see no courses listed here, we redirect them elsewhere

    return render(request, "course_list.html", {"courses": courses})

# View for showing the details of a course (accessible by all users)
@login_required
def course_details(request, course_id):
    course = Course.objects.get(id=course_id)
    sections = course.sections.all()  # Get all sections for this course
    if request.user.role == 'student':
        return render(request, "course_details_student.html", {"course": course, "sections": sections})
    return render(request, "course_details.html", {"course": course, "sections": sections})
