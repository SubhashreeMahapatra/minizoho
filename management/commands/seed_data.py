from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from tasks.models import Task
from attendance.models import Attendance
import datetime
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create users
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'first_name': 'System', 'last_name': 'Admin',
            'email': 'admin@company.com', 'role': 'admin', 'department': 'IT',
            'is_staff': True, 'is_superuser': True,
        })
        admin.set_password('admin123')
        admin.save()

        manager, _ = User.objects.get_or_create(username='manager1', defaults={
            'first_name': 'Riya', 'last_name': 'Sharma',
            'email': 'riya@company.com', 'role': 'manager', 'department': 'Engineering',
        })
        manager.set_password('manager123')
        manager.save()

        employees = []
        emp_data = [
            ('emp1', 'Arjun', 'Mehta', 'arjun@company.com', 'Engineering'),
            ('emp2', 'Priya', 'Singh', 'priya@company.com', 'Design'),
            ('emp3', 'Rohit', 'Kumar', 'rohit@company.com', 'Engineering'),
        ]
        for uname, fn, ln, email, dept in emp_data:
            emp, _ = User.objects.get_or_create(username=uname, defaults={
                'first_name': fn, 'last_name': ln, 'email': email,
                'role': 'employee', 'department': dept,
            })
            emp.set_password('emp123')
            emp.save()
            employees.append(emp)

        # Create tasks
        task_titles = [
            ('Build login page', 'high', 'done'),
            ('Set up MySQL database', 'critical', 'done'),
            ('Implement REST API', 'high', 'in_progress'),
            ('Write unit tests', 'medium', 'todo'),
            ('Design dashboard UI', 'medium', 'in_progress'),
            ('Deploy to production', 'critical', 'todo'),
            ('Code review session', 'low', 'review'),
            ('Documentation update', 'low', 'todo'),
        ]
        for title, priority, status in task_titles:
            Task.objects.get_or_create(title=title, defaults={
                'assigned_to': random.choice(employees),
                'created_by': manager,
                'priority': priority, 'status': status,
                'due_date': datetime.date.today() + datetime.timedelta(days=random.randint(-3, 14)),
            })

        # Create attendance records
        for emp in employees:
            for i in range(7):
                d = datetime.date.today() - datetime.timedelta(days=i)
                Attendance.objects.get_or_create(user=emp, date=d, defaults={
                    'check_in': datetime.time(9, random.randint(0, 30)),
                    'check_out': datetime.time(17, random.randint(0, 30)),
                    'status': random.choice(['present', 'present', 'present', 'late']),
                })

        self.stdout.write(self.style.SUCCESS(
            f'Done! Users: admin/admin123, manager1/manager123, emp1-3/emp123'
        ))
