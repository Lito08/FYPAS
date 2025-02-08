from django.urls import path
from .views import (
    manage_courses_view, create_course_view, edit_course_view, delete_course_view,
    manage_sections_view, create_section_view, edit_section_view, delete_section_view, manage_enrollments_view, enroll_student_view, unenroll_student_view
)

urlpatterns = [
    # 🔹 Course Management
    path('manage-courses/', manage_courses_view, name='manage_courses'),
    path('create-course/', create_course_view, name='create_course'),
    path('edit-course/<int:course_id>/', edit_course_view, name='edit_course'),
    path('delete-course/<int:course_id>/', delete_course_view, name='delete_course'),

    # 🔹 Section Management
    path('manage-sections/', manage_sections_view, name='manage_sections'),
    path('create-section/', create_section_view, name='create_section'),
    path('edit-section/<int:section_id>/', edit_section_view, name='edit_section'),
    path('delete-section/<int:section_id>/', delete_section_view, name='delete_section'),

    # 🔹 Enrollment Management
    path('manage-enrollments/', manage_enrollments_view, name='manage_enrollments'),
    path('enroll-student/', enroll_student_view, name='enroll_student'),
    path('unenroll-student/<int:enrollment_id>/', unenroll_student_view, name='unenroll_student'),
]
