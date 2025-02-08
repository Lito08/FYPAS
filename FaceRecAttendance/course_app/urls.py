from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_course, name='add_course'),
    path('edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course_list/', views.course_list, name='course_list'),
    path('add_section/<int:course_id>/', views.add_section, name='add_section'),
    path('add_class/<int:section_id>/', views.add_class, name='add_class'),
    path('course_details/<int:course_id>/', views.course_details, name='course_details'),
]
