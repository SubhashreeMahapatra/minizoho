from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from tasks.models import Task
from attendance.models import Attendance
import datetime


class TaskAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='pass123', role='admin')
        self.employee = User.objects.create_user(username='emp', password='pass123', role='employee')
        self.task = Task.objects.create(
            title='API Task', assigned_to=self.employee,
            created_by=self.admin, status='todo', priority='high'
        )

    def _get_token(self, username, password):
        res = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': password})
        return res.data['access']

    def test_list_tasks_authenticated(self):
        token = self._get_token('admin', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_tasks_unauthenticated(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_only_sees_own_tasks(self):
        token = self._get_token('emp', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data['results']), 1)

    def test_complete_task_action(self):
        token = self._get_token('admin', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/tasks/{self.task.pk}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')


class AttendanceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = User.objects.create_user(username='emp', password='pass123', role='employee')

    def _get_token(self):
        res = self.client.post(reverse('token_obtain_pair'), {'username': 'emp', 'password': 'pass123'})
        return res.data['access']

    def test_check_in_api(self):
        token = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/attendance/check_in/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_double_check_in_rejected(self):
        token = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client.post('/api/attendance/check_in/')
        response = self.client.post('/api/attendance/check_in/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
