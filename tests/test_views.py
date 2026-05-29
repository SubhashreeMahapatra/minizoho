from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from tasks.models import Task
from attendance.models import Attendance
import datetime


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', role='employee')

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('dashboard:home'))

    def test_login_failure(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='pass123', role='admin')
        self.employee = User.objects.create_user(username='emp', password='pass123', role='employee')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:home')}")

    def test_admin_dashboard_loads(self):
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_employee_dashboard_loads(self):
        self.client.login(username='emp', password='pass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(username='mgr', password='pass123', role='manager')
        self.employee = User.objects.create_user(username='emp', password='pass123', role='employee')
        self.task = Task.objects.create(
            title='Test Task', assigned_to=self.employee,
            created_by=self.manager, status='todo', priority='medium'
        )

    def test_task_list_requires_login(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)

    def test_manager_can_see_task_list(self):
        self.client.login(username='mgr', password='pass123')
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_manager_can_create_task(self):
        self.client.login(username='mgr', password='pass123')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'New Task', 'assigned_to': self.employee.pk,
            'priority': 'low', 'status': 'todo'
        })
        self.assertEqual(Task.objects.filter(title='New Task').count(), 1)

    def test_employee_cannot_create_task(self):
        self.client.login(username='emp', password='pass123')
        response = self.client.get(reverse('tasks:create'))
        self.assertRedirects(response, reverse('dashboard:home'))


class AttendanceViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.employee = User.objects.create_user(username='emp', password='pass123', role='employee')

    def test_check_in(self):
        self.client.login(username='emp', password='pass123')
        response = self.client.post(reverse('attendance:check_in'), {'notes': ''})
        self.assertEqual(Attendance.objects.filter(user=self.employee).count(), 1)

    def test_double_check_in_prevented(self):
        self.client.login(username='emp', password='pass123')
        self.client.post(reverse('attendance:check_in'), {'notes': ''})
        response = self.client.post(reverse('attendance:check_in'), {'notes': ''})
        self.assertEqual(Attendance.objects.filter(user=self.employee).count(), 1)
