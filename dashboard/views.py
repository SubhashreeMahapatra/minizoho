from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from tasks.models import Task
from attendance.models import Attendance, LeaveRequest
from accounts.models import User
import json


@login_required
def home(request):
    today = timezone.now().date()
    user = request.user

    if user.role in ('admin', 'manager'):
        total_tasks = Task.objects.count()
        tasks_done = Task.objects.filter(status='done').count()
        tasks_in_progress = Task.objects.filter(status='in_progress').count()
        overdue_tasks = [t for t in Task.objects.exclude(status__in=['done','cancelled']) if t.is_overdue]
        present_today = Attendance.objects.filter(date=today, status='present').count()
        total_employees = User.objects.filter(role='employee', is_active=True).count()
        pending_leaves = LeaveRequest.objects.filter(status='pending').count()
        my_tasks = Task.objects.filter(assigned_to=user, status__in=['todo','in_progress'])[:5]
        recent_attendance = Attendance.objects.select_related('user').filter(date=today)[:10]

        status_data = list(Task.objects.values('status').annotate(count=Count('id')))
        priority_data = list(Task.objects.values('priority').annotate(count=Count('id')))

        context = {
            'total_tasks': total_tasks, 'tasks_done': tasks_done,
            'tasks_in_progress': tasks_in_progress, 'overdue_count': len(overdue_tasks),
            'present_today': present_today, 'total_employees': total_employees,
            'pending_leaves': pending_leaves, 'my_tasks': my_tasks,
            'recent_attendance': recent_attendance,
            'status_data': json.dumps(status_data),
            'priority_data': json.dumps(priority_data),
        }
    else:
        my_tasks = Task.objects.filter(assigned_to=user).exclude(status='cancelled')
        today_attendance = Attendance.objects.filter(user=user, date=today).first()
        pending_tasks = my_tasks.filter(status__in=['todo','in_progress']).count()
        done_tasks = my_tasks.filter(status='done').count()
        my_leaves = LeaveRequest.objects.filter(user=user).order_by('-created_at')[:3]
        context = {
            'my_tasks': my_tasks[:5], 'today_attendance': today_attendance,
            'pending_tasks': pending_tasks, 'done_tasks': done_tasks,
            'my_leaves': my_leaves,
        }

    return render(request, 'dashboard/home.html', context)


@login_required
def summary(request):
    from django.db.models.functions import TruncMonth
    user = request.user
    tasks_by_status = Task.objects.values('status').annotate(count=Count('id'))
    attendance_summary = Attendance.objects.values('status').annotate(count=Count('id'))
    top_performers = (
        User.objects.filter(role='employee')
        .annotate(done_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status='done')))
        .order_by('-done_tasks')[:5]
    )
    context = {
        'tasks_by_status': list(tasks_by_status),
        'attendance_summary': list(attendance_summary),
        'top_performers': top_performers,
    }
    return render(request, 'dashboard/summary.html', context)
