from django.db import models
from django.utils import timezone
from accounts.models import User


class Attendance(models.Model):
    STATUS_CHOICES = [('present','Present'),('absent','Absent'),('late','Late'),('half_day','Half Day'),('leave','On Leave')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.status})"

    @property
    def hours_worked(self):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            ci = datetime.combine(date.today(), self.check_in)
            co = datetime.combine(date.today(), self.check_out)
            diff = co - ci
            return round(diff.seconds / 3600, 2)
        return None


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [('sick','Sick Leave'),('casual','Casual Leave'),('earned','Earned Leave'),('unpaid','Unpaid Leave')]
    STATUS_CHOICES = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1
