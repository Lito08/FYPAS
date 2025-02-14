from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Course, Section, Enrollment, EnrollmentCart, ClassSession
from .forms import CourseForm, SectionForm, EnrollmentForm, EnrollmentCartForm, AdminEnrollmentForm
from datetime import timedelta, datetime
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Min

# 🔹 MANAGE COURSES
@login_required(login_url='/users/login/')
def manage_courses_view(request):
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    courses = Course.objects.all()
    return render(request, 'courses/manage_courses.html', {'courses': courses})

@login_required(login_url='/users/login/')
def create_course_view(request):
    """Allows Admins to create a course and auto-generate required sections."""
    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()

            # ✅ Auto-create Lecture & Tutorial Sections (if required)
            sections_to_create = []
            if course.lecture_required:
                sections_to_create.append(('Lecture', 1))
            if course.tutorial_required:
                sections_to_create.append(('Tutorial', 1))

            for section_type, section_number in sections_to_create:
                section = Section.objects.create(
                    course=course,
                    section_type=section_type,
                    section_number=section_number,
                    start_date=None,  # Start date will be assigned later
                    class_time=None,  # Class time will be assigned later
                    duration=60,  # Default 1 hour
                )

                # ✅ Generate 14 weeks of class sessions only when start_date & class_time are set
                if section.start_date and section.class_time:
                    for week in range(1, 15):
                        ClassSession.objects.create(
                            section=section,
                            week_number=week,
                            date=section.start_date + timedelta(weeks=week - 1),
                            start_time=section.class_time
                        )

            messages.success(request, "Course and required sections created successfully!")
            return redirect('manage_courses')
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})

@login_required(login_url='/users/login/')
def edit_course_view(request, course_id):
    """Allows Admins to edit a course and auto-handle related sections."""
    course = get_object_or_404(Course, id=course_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()

            # ✅ Handle Lecture Section
            if course.lecture_required:
                lecture_section, created = Section.objects.get_or_create(
                    course=course,
                    section_type='Lecture',
                    section_number=1,
                    defaults={'start_date': None, 'class_time': None, 'duration': 60}
                )
                if created and lecture_section.start_date and lecture_section.class_time:
                    for week in range(1, 15):
                        ClassSession.objects.create(
                            section=lecture_section,
                            week_number=week,
                            date=lecture_section.start_date + timedelta(weeks=week - 1),
                            start_time=lecture_section.class_time
                        )
            else:
                Section.objects.filter(course=course, section_type='Lecture').delete()

            # ✅ Handle Tutorial Section
            if course.tutorial_required:
                tutorial_section, created = Section.objects.get_or_create(
                    course=course,
                    section_type='Tutorial',
                    section_number=1,
                    defaults={'start_date': None, 'class_time': None, 'duration': 60}
                )
                if created and tutorial_section.start_date and tutorial_section.class_time:
                    for week in range(1, 15):
                        ClassSession.objects.create(
                            section=tutorial_section,
                            week_number=week,
                            date=tutorial_section.start_date + timedelta(weeks=week - 1),
                            start_time=tutorial_section.class_time
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

    # ✅ Find sections missing class sessions
    sections_missing_classes = [s for s in sections if s.sessions.count() == 0]

    return render(request, 'courses/manage_sections.html', {
        'sections': sections,
        'sections_missing_classes': sections_missing_classes
    })

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
                section.course = course  # ✅ Assign course
            section.save()

            # ✅ Ensure class sessions are generated correctly
            existing_sessions = ClassSession.objects.filter(section=section).count()
            if existing_sessions == 0:
                for week in range(1, 15):  # ✅ Generate 14 weeks
                    ClassSession.objects.create(
                        section=section,
                        week_number=week,
                        date=section.start_date + timedelta(weeks=week - 1),
                        start_time=section.class_time
                    )

            messages.success(request, "Section created and class sessions generated successfully!")
            return redirect('view_course_sections', course_id=course.id)
    else:
        form = SectionForm(initial={'course': course})

    return render(request, 'courses/create_section.html', {'form': form, 'course': course})

@login_required(login_url='/users/login/')
def edit_section_view(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.user.role not in ['Superadmin', 'Admin']:
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            section = form.save()

            # ✅ Ensure class sessions are generated if they don't exist
            existing_sessions = ClassSession.objects.filter(section=section).count()
            if existing_sessions == 0:
                for week in range(1, 15):  # ✅ Generate 14 weeks if missing
                    ClassSession.objects.create(
                        section=section,
                        week_number=week,
                        date=section.start_date + timedelta(weeks=week - 1),
                        start_time=section.class_time
                    )
                messages.success(request, "Section updated and missing class sessions were generated!")

            else:
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
        form = AdminEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)

            # ✅ Check if section is full
            enrolled_students = Enrollment.objects.filter(section=enrollment.section).count()
            if enrolled_students >= enrollment.section.max_students:
                messages.error(request, f"The section {enrollment.section.section_type} {enrollment.section.section_number} is full.")
                return render(request, 'courses/admin_enroll_student.html', {'form': form})

            enrollment.save()
            messages.success(request, "Student enrolled successfully!")
            return redirect('manage_enrollments')
    else:
        form = AdminEnrollmentForm()

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

# 🔹 SELECT COURSES
@login_required(login_url='/users/login/')
def select_course_view(request):
    """Step 1: Student selects courses to enroll in, excluding already enrolled ones."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    # Get course IDs that the student has already enrolled in
    enrolled_courses = Enrollment.objects.filter(student=request.user).values_list('section__course_id', flat=True)
    
    # Exclude already enrolled courses
    available_courses = Course.objects.exclude(id__in=enrolled_courses)

    return render(request, 'courses/select_course.html', {'courses': available_courses})

# 🔹 SELECT SECTIONS
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

        # ✅ Ensure section has a valid schedule
        if not section.start_date or not section.class_time:
            messages.error(request, f"⚠️ Cannot select {section.section_type} {section.section_number} as its schedule is not set.")
            return redirect('select_sections', course_id=course.id)

        # ✅ Convert to full datetime for proper time calculations
        selected_section_start = datetime.combine(section.start_date, section.class_time)
        selected_section_end = selected_section_start + timedelta(minutes=section.duration)

        # ✅ Prevent schedule clashes with sections already in the cart
        if cart_item.lecture_section and cart_item.lecture_section.start_date and cart_item.lecture_section.class_time:
            lecture_start = datetime.combine(cart_item.lecture_section.start_date, cart_item.lecture_section.class_time)
            lecture_end = lecture_start + timedelta(minutes=cart_item.lecture_section.duration)

            if (
                lecture_start <= selected_section_start < lecture_end or
                lecture_start < selected_section_end <= lecture_end
            ):
                messages.error(request, f"⚠️ Cannot add {section.section_type} {section.section_number} as it conflicts with Lecture {cart_item.lecture_section.section_number}.")
                return redirect('select_sections', course_id=course.id)

        if cart_item.tutorial_section and cart_item.tutorial_section.start_date and cart_item.tutorial_section.class_time:
            tutorial_start = datetime.combine(cart_item.tutorial_section.start_date, cart_item.tutorial_section.class_time)
            tutorial_end = tutorial_start + timedelta(minutes=cart_item.tutorial_section.duration)

            if (
                tutorial_start <= selected_section_start < tutorial_end or
                tutorial_start < selected_section_end <= tutorial_end
            ):
                messages.error(request, f"⚠️ Cannot add {section.section_type} {section.section_number} as it conflicts with Tutorial {cart_item.tutorial_section.section_number}.")
                return redirect('select_sections', course_id=course.id)

        # ✅ Add section to cart (Lecture or Tutorial)
        if section.section_type == "Lecture":
            cart_item.lecture_section = section  # Ensures only one lecture section
        elif section.section_type == "Tutorial":
            cart_item.tutorial_section = section  # Ensures only one tutorial section
        cart_item.save()

        messages.success(request, f"✅ {section.section_type} {section.section_number} added to cart successfully!")

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

# 🔹 REVIEW CART
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

# 🔹 FINALIZE ENROLLMENT
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

@login_required(login_url='/users/login/')
def student_schedule_view(request):
    """Displays the student's weekly schedule with AJAX support."""
    student = request.user
    enrollments = Enrollment.objects.filter(student=student).select_related('section__course')

    # ✅ Get the selected week date from the request
    week_date_str = request.GET.get("week_date")
    if week_date_str:
        selected_date = datetime.strptime(week_date_str, "%Y-%m-%d").date()
    else:
        selected_date = now().date()  # Default to today's date

    # ✅ Find the earliest start date among the student's enrolled courses
    earliest_start_date = enrollments.aggregate(Min("section__start_date"))["section__start_date__min"]
    
    if earliest_start_date:
        # ✅ Adjust the selected week based on the actual start date
        week_offset = (selected_date - earliest_start_date).days // 7
        start_of_week = earliest_start_date + timedelta(weeks=week_offset)
    else:
        # If no courses have a start date, default to the current week
        start_of_week = selected_date - timedelta(days=selected_date.weekday())

    # ✅ Retrieve class sessions for the student's enrolled sections
    weekly_schedule = []
    for enrollment in enrollments:
        class_sessions = ClassSession.objects.filter(
            section=enrollment.section,
            date__range=[start_of_week, start_of_week + timedelta(days=4)]
        )

        for session in class_sessions:
            weekly_schedule.append({
                "course": enrollment.section.course.name,
                "type": enrollment.section.section_type,
                "day": session.date.strftime("%A"),
                "hour": session.start_time.hour,
            })

    # ✅ Debugging Output
    print(f"Adjusted Start of Week: {start_of_week} | Selected Date: {selected_date}")
    print("Weekly Schedule Data:", weekly_schedule)

    # ✅ Return JSON if it's an AJAX request
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"schedule": weekly_schedule, "start_of_week": start_of_week.strftime("%Y-%m-%d")})

    return render(request, "courses/student_schedule.html", {
        "enrollments": enrollments,
        "selected_week": start_of_week.strftime("%Y-%m-%d"),
    })

@login_required(login_url='/users/login/')
def my_courses_view(request):
    """Displays all enrolled courses for the student with options to drop or change sections."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    # ✅ Fetch enrolled courses and their sections
    enrollments = Enrollment.objects.filter(student=request.user).select_related('section__course')

    return render(request, 'courses/my_courses.html', {'enrollments': enrollments})

@login_required(login_url='/users/login/')
def change_section_view(request, course_id):
    """Allows students to change their section for an enrolled course."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    # ✅ Ensure the student is enrolled in this course
    enrollment = Enrollment.objects.filter(student=request.user, section__course_id=course_id).first()
    if not enrollment:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('my_courses')

    course = enrollment.section.course

    # ✅ Get available sections for this course
    lecture_sections = Section.objects.filter(course=course, section_type='Lecture').exclude(schedule=None)
    tutorial_sections = Section.objects.filter(course=course, section_type='Tutorial').exclude(schedule=None)

    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        section = get_object_or_404(Section, id=section_id)

        # ✅ Prevent schedule conflicts
        enrolled_sections = Enrollment.objects.filter(student=request.user).exclude(section=enrollment.section)
        for e in enrolled_sections:
            if section.schedule and e.section.schedule:
                end_time = section.schedule + timedelta(minutes=section.duration)
                if e.section.schedule < end_time and section.schedule < (e.section.schedule + timedelta(minutes=e.section.duration)):
                    messages.error(request, "This section conflicts with another enrolled section.")
                    return redirect('change_section', course_id=course.id)

        # ✅ Update enrollment with new section
        enrollment.section = section
        enrollment.save()

        messages.success(request, f"Successfully changed section to {section.section_type} {section.section_number}.")
        return redirect('my_courses')

    return render(request, 'courses/change_section.html', {
        'course': course,
        'lecture_sections': lecture_sections,
        'tutorial_sections': tutorial_sections,
        'current_section': enrollment.section
    })

@login_required(login_url='/users/login/')
def drop_course_view(request, course_id):
    """Allows students to drop a course they are currently enrolled in."""
    if request.user.role != 'Student':
        return render(request, 'access_denied.html')

    # ✅ Get the enrolled sections for this course
    enrollments = Enrollment.objects.filter(student=request.user, section__course_id=course_id)
    
    if not enrollments.exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('my_courses')

    if request.method == 'POST':
        enrollments.delete()
        messages.success(request, "Successfully dropped the course.")
        return redirect('my_courses')

    return render(request, 'courses/drop_course.html', {
        'course': enrollments.first().section.course
    })
