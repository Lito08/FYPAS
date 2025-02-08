# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from users.forms import CustomPasswordResetForm
from .views import change_password_view, dashboard_view, manage_users_view, create_user_view, edit_user_view, delete_user_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', change_password_view, name='change_password'),
    path(
        'reset-password/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            form_class=CustomPasswordResetForm  # ✅ Use custom form
        ),
        name='password_reset'
    ),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    
    path('dashboard/', dashboard_view, name='dashboard'),
    
    path('manage-users/', manage_users_view, name='manage_users'),
    path('create-user/', create_user_view, name='create_user'),
    path('edit-user/<int:user_id>/', edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user_view, name='delete_user'),
]
