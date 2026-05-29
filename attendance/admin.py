from django.contrib import admin
from .models import Attendance, LeaveRequest

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user','date','check_in','check_out','status','hours_worked']
    list_filter = ['status','date']
    search_fields = ['user__username','user__first_name']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user','leave_type','start_date','end_date','status','days_requested']
    list_filter = ['status','leave_type']
    search_fields = ['user__username']
