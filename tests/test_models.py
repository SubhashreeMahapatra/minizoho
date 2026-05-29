from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from tasks.models import Task, TaskComment
from attendance.models import Attendance, LeaveRequest
import datetime


class UserModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass123', role='admin')
        self.manager = User.objects.create_user(username='mgr1', password='pass123', role='manager')
        self.employee = User.objects.create_user(username='emp1', password='pass123', role='employee')

    def test_role_properties(self):
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_manager)
        self.assertTrue(self.manager.is_manager)
        self.assertTrue(self.employee.is_employee)

    def test_str_representation(self):
        self.assertIn('admin', str(self.admin))


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taskuser', password='pass123')
        self.task = Task.objects.create(
            title='Test Task', assigned_to=self.user, created_by=self.user,
            priority='high', status='todo'
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.status, 'todo')

    def test_is_overdue_false_when_no_due_date(self):
        self.assertFalse(self.task.is_overdue)

    def test_is_overdue_true_when_past_due(self):
        self.task.due_date = datetime.date.today() - datetime.timedelta(days=1)
        self.task.save()
        self.assertTrue(self.task.is_overdue)

    def test_mark_done(self):
        self.task.mark_done()
        self.assertEqual(self.task.status, 'done')
        self.assertIsNotNone(self.task.completed_at)


class AttendanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='attuser', password='pass123')
        self.attendance = Attendance.objects.create(
            user=self.user, date=timezone.now().date(),
            check_in=datetime.time(9, 0), check_out=datetime.time(17, 0),
            status='present'
        )

    def test_hours_worked(self):
        self.assertEqual(self.attendance.hours_worked, 8.0)

    def test_str_representation(self):
        self.assertIn('attuser', str(self.attendance))


class LeaveRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='leaveuser', password='pass123')
        self.leave = LeaveRequest.objects.create(
            user=self.user, leave_type='casual',
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=2),
            reason='Personal work'
        )

    def test_days_requested(self):
        self.assertEqual(self.leave.days_requested, 3)
