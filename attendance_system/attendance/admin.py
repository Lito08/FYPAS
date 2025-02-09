from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'section', 'date', 'time_checked_in', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'section__course__name')
