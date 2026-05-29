from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


@shared_task
def send_task_due_reminder():
    """Send email reminders for tasks due tomorrow."""
    from tasks.models import Task
    import datetime
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    due_tasks = Task.objects.filter(due_date=tomorrow, status__in=['todo', 'in_progress']).select_related('assigned_to')
    for task in due_tasks:
        if task.assigned_to and task.assigned_to.email:
            send_mail(
                subject=f'Task Due Tomorrow: {task.title}',
                message=f'Hi {task.assigned_to.first_name},\n\nYour task "{task.title}" is due tomorrow.\n\nPriority: {task.priority}\n\nPlease make sure it is completed on time.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assigned_to.email],
                fail_silently=True,
            )
    return f'Sent reminders for {due_tasks.count()} tasks'


@shared_task
def generate_daily_attendance_summary():
    """Generate and email daily attendance summary to admins."""
    from attendance.models import Attendance
    from accounts.models import User
    today = timezone.now().date()
    present = Attendance.objects.filter(date=today, status='present').count()
    absent = Attendance.objects.filter(date=today, status='absent').count()
    late = Attendance.objects.filter(date=today, status='late').count()
    total = User.objects.filter(role='employee', is_active=True).count()
    admins = User.objects.filter(role='admin', email__isnull=False).exclude(email='')
    report = f"""Daily Attendance Summary - {today}
Total Employees: {total}
Present: {present}
Late: {late}
Absent: {absent}
Not Marked: {total - present - absent - late}"""
    for admin in admins:
        send_mail(
            subject=f'Daily Attendance Summary - {today}',
            message=report,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin.email],
            fail_silently=True,
        )
    return report


@shared_task
def auto_mark_absent():
    """Mark employees as absent if no attendance recorded by end of day."""
    from attendance.models import Attendance
    from accounts.models import User
    today = timezone.now().date()
    marked_users = Attendance.objects.filter(date=today).values_list('user_id', flat=True)
    unmarked = User.objects.filter(role='employee', is_active=True).exclude(id__in=marked_users)
    count = 0
    for emp in unmarked:
        Attendance.objects.create(user=emp, date=today, status='absent')
        count += 1
    return f'Marked {count} employees as absent'
