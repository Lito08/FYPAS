from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("matric_id", "role")}),
    )
    list_display = ("username", "matric_id", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

admin.site.register(User, CustomUserAdmin)
