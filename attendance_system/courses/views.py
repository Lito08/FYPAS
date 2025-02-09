from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Section, Enrollment, EnrollmentCart
from .forms import CourseForm, SectionForm, EnrollmentForm, EnrollmentCartForm

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

# 🔹 ADMIN MANUAL STUDENT ENROLLMENT
@login_required(login_url='/users/login/')
def admin_enroll_student_view(request):
    """Allows Superadmins/Admins to manually enroll a student into a section."""
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'courses/access_denied.html')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)

            # ✅ Check if section is full
            enrolled_students = Enrollment.objects.filter(section=enrollment.section).count()
            if enrolled_students >= enrollment.section.max_students:
                messages.error(request, f"The section {enrollment.section.section_type} {enrollment.section.section_number} is full. Please select another.")
                return render(request, 'courses/admin_enroll_student.html', {'form': form})

            enrollment.save()
            messages.success(request, "Student enrolled successfully!")
            return redirect('manage_enrollments')
    else:
        form = EnrollmentForm()

    return render(request, 'courses/admin_enroll_student.html', {'form': form})

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

# 🔹 SELECT COURSES (Step 1)
@login_required(login_url='/users/login/')
def select_course_view(request):
    """Step 1: Student selects courses to enroll in."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    courses = Course.objects.all()
    return render(request, 'courses/select_course.html', {'courses': courses})

# 🔹 SELECT SECTIONS (Step 2)
@login_required(login_url='/users/login/')
def select_sections_view(request, course_id):
    """Step 2: Student selects sections for the selected course."""
    if request.user.role != 'Student':
        return render(request, 'courses/access_denied.html')

    course = get_object_or_404(Course, id=course_id)

    if EnrollmentCart.objects.filter(student=request.user, course=course).exists():
        messages.error(request, "You have already added this course to your enrollment cart.")
        return redirect('review_cart')

    if request.method == 'POST':
        form = EnrollmentCartForm(request.POST, student=request.user, course=course)
        if form.is_valid():
            enrollment_cart, created = EnrollmentCart.objects.get_or_create(student=request.user, course=course)
            enrollment_cart.lecture_section = form.cleaned_data['lecture_section']
            enrollment_cart.tutorial_section = form.cleaned_data['tutorial_section']
            enrollment_cart.save()

            messages.success(request, "Course added to enrollment cart!")
            return redirect('review_cart')
    else:
        form = EnrollmentCartForm(student=request.user, course=course)

    return render(request, 'courses/select_sections.html', {'course': course, 'form': form})

# 🔹 REVIEW CART (Step 3)
@login_required(login_url='/users/login/')
def review_cart_view(request):
    """Step 3: Student reviews selected courses before final enrollment."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    cart_items = EnrollmentCart.objects.filter(student=request.user)
    return render(request, 'courses/review_cart.html', {'cart_items': cart_items})

# 🔹 REMOVE FROM CART
@login_required(login_url='/users/login/')
def remove_from_cart_view(request, cart_id):
    """Allows students to remove a course from their cart before finalizing enrollment."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    cart_item = get_object_or_404(EnrollmentCart, id=cart_id, student=request.user)
    cart_item.delete()
    messages.success(request, "Course removed from cart!")
    return redirect('review_cart')

# 🔹 FINALIZE ENROLLMENT (Step 4)
@login_required(login_url='/users/login/')
def finalize_enrollment_view(request):
    """Step 4: Finalize enrollment for all selected courses."""
    if request.user.role != 'Student':
        return render(request, 'courses/access_denied.html')

    cart_items = EnrollmentCart.objects.filter(student=request.user)

    for cart_item in cart_items:
        Enrollment.objects.create(student=request.user, section=cart_item.lecture_section)
        if cart_item.tutorial_section:
            Enrollment.objects.create(student=request.user, section=cart_item.tutorial_section)

    # ✅ Clear cart after finalizing enrollment
    cart_items.delete()

    messages.success(request, "Enrollment completed successfully!")
    return redirect('student_schedule')

# 🔹 VIEW STUDENT SCHEDULE
@login_required(login_url='/users/login/')
def student_schedule_view(request):
    """Displays the enrolled sections in a weekly schedule."""
    if request.user.role != 'Student':
        return render(request, 'courses/access_denied.html')

    enrollments = Enrollment.objects.filter(student=request.user).select_related('section').order_by('section__schedule')
    return render(request, 'courses/student_schedule.html', {'enrollments': enrollments})
