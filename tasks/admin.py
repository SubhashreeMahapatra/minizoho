from django.contrib import admin
from .models import Task, TaskComment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title','assigned_to','priority','status','due_date','is_overdue','created_at']
    list_filter = ['status','priority','created_at']
    search_fields = ['title','description']
    readonly_fields = ['created_at','updated_at','completed_at']

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task','author','created_at']
    search_fields = ['content']
