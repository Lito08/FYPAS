from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Section, Enrollment, EnrollmentCart
from .forms import CourseForm, SectionForm, EnrollmentForm, EnrollmentCartForm
from datetime import timedelta

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
    """Allows students to select lecture and tutorial sections separately and add them to cart."""
    if request.user.role != 'Student':
        return render(request, 'courses/access_denied.html')

    course = get_object_or_404(Course, id=course_id)
    lecture_sections = Section.objects.filter(course=course, section_type='Lecture')
    tutorial_sections = Section.objects.filter(course=course, section_type='Tutorial')

    # ✅ Get the cart item for this student and course, ensuring only one exists
    cart_item, created = EnrollmentCart.objects.get_or_create(
        student=request.user, 
        course=course,
        defaults={'lecture_section': None, 'tutorial_section': None}
    )

    # ✅ Delete duplicate cart entries (if any exist)
    EnrollmentCart.objects.filter(student=request.user, course=course).exclude(id=cart_item.id).delete()

    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        section = get_object_or_404(Section, id=section_id)

        # ✅ Prevent schedule clashes with sections already in the cart
        if cart_item.lecture_section and cart_item.lecture_section.schedule and section.schedule:
            if (
                cart_item.lecture_section.schedule <= section.schedule < cart_item.lecture_section.schedule + timedelta(minutes=cart_item.lecture_section.duration)
            ):
                messages.error(request, f"Cannot add {section.section_type} {section.section_number} as it conflicts with Lecture {cart_item.lecture_section.section_number}.")
                return redirect('select_sections', course_id=course.id)

        if cart_item.tutorial_section and cart_item.tutorial_section.schedule and section.schedule:
            if (
                cart_item.tutorial_section.schedule <= section.schedule < cart_item.tutorial_section.schedule + timedelta(minutes=cart_item.tutorial_section.duration)
            ):
                messages.error(request, f"Cannot add {section.section_type} {section.section_number} as it conflicts with Tutorial {cart_item.tutorial_section.section_number}.")
                return redirect('select_sections', course_id=course.id)

        # ✅ Add section to cart (Lecture or Tutorial)
        if section.section_type == "Lecture":
            cart_item.lecture_section = section  # Ensures only one lecture section
        elif section.section_type == "Tutorial":
            cart_item.tutorial_section = section  # Ensures only one tutorial section
        cart_item.save()

        messages.success(request, f"{section.section_type} {section.section_number} added to cart successfully!")

        # ✅ Stay on page until all required selections are made
        if cart_item.lecture_section and (not course.tutorial_required or cart_item.tutorial_section):
            return redirect('review_cart')  # Proceed to review if all required sections are added

        return redirect('select_sections', course_id=course.id)  # Stay on page if requirements are not met

    return render(request, 'courses/select_sections.html', {
        'course': course,
        'lecture_sections': lecture_sections,
        'tutorial_sections': tutorial_sections,
        'cart_item': cart_item
    })

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

    # ✅ Ensure each course has 1 Lecture & 1 Tutorial (if required)
    for cart_item in cart_items:
        if not cart_item.lecture_section:
            messages.error(request, f"⚠️ You must select a Lecture for {cart_item.course.name}.")
            return redirect('review_cart')
        if cart_item.course.tutorial_required and not cart_item.tutorial_section:
            messages.error(request, f"⚠️ You must select a Tutorial for {cart_item.course.name}.")
            return redirect('review_cart')

    # ✅ Proceed with Enrollment
    for cart_item in cart_items:
        Enrollment.objects.create(student=request.user, section=cart_item.lecture_section)
        if cart_item.tutorial_section:
            Enrollment.objects.create(student=request.user, section=cart_item.tutorial_section)

    # ✅ Clear the cart after finalizing enrollment
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

    # Define available hours and weekdays
    hours = [str(i).zfill(2) for i in range(8, 22)]  # 08:00 to 21:00
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    return render(request, 'courses/student_schedule.html', {
        'enrollments': enrollments,
        'hours': hours,
        'weekdays': weekdays
    })
