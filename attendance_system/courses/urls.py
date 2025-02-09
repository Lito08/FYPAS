from django.urls import path
from .views import (
    manage_courses_view, create_course_view, edit_course_view, delete_course_view,
    manage_sections_view, create_section_view, edit_section_view, delete_section_view, view_course_sections_view,
    manage_enrollments_view, enroll_student_view, unenroll_student_view, admin_enroll_student_view,
    select_course_view, select_sections_view, review_cart_view, remove_from_cart_view, finalize_enrollment_view, student_schedule_view
)

urlpatterns = [
    # 🔹 Course Management
    path('manage-courses/', manage_courses_view, name='manage_courses'),
    path('create-course/', create_course_view, name='create_course'),
    path('edit-course/<int:course_id>/', edit_course_view, name='edit_course'),
    path('delete-course/<int:course_id>/', delete_course_view, name='delete_course'),
    path('view-course-sections/<int:course_id>/', view_course_sections_view, name='view_course_sections'),
    path('create-section/<int:course_id>/', create_section_view, name='create_section_for_course'),

    # 🔹 Section Management
    path('manage-sections/', manage_sections_view, name='manage_sections'),
    path('create-section/', create_section_view, name='create_section'),
    path('edit-section/<int:section_id>/', edit_section_view, name='edit_section'),
    path('delete-section/<int:section_id>/', delete_section_view, name='delete_section'),

    # 🔹 Enrollment Management
    path('manage-enrollments/', manage_enrollments_view, name='manage_enrollments'),
    path('enroll-student/', enroll_student_view, name='enroll_student'),
    path('admin-enroll-student/', admin_enroll_student_view, name='admin_enroll_student'),  # ✅ Admin manual enrollment
    path('unenroll-student/<int:enrollment_id>/', unenroll_student_view, name='unenroll_student'),

    # 🔹 Student Self-Enrollment (Cart-Based Process)
    path('select-course/', select_course_view, name='select_course'),  # ✅ Step 1: Select Courses
    path('select-sections/<int:course_id>/', select_sections_view, name='select_sections'),  # ✅ Step 2: Choose Sections
    path('review-cart/', review_cart_view, name='review_cart'),  # ✅ Step 3: Review Cart
    path('remove-from-cart/<int:cart_id>/', remove_from_cart_view, name='remove_from_cart'),  # ✅ Remove from cart
    path('finalize-enrollment/', finalize_enrollment_view, name='finalize_enrollment'),  # ✅ Step 4: Finalize Enrollment

    # 🔹 Student Schedule
    path('student-schedule/', student_schedule_view, name='student_schedule'),  # ✅ View enrolled courses
]
