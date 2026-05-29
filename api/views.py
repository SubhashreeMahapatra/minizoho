from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from accounts.models import User
from tasks.models import Task, TaskComment
from attendance.models import Attendance, LeaveRequest
from .serializers import (UserSerializer, TaskSerializer, TaskCommentSerializer,
                           AttendanceSerializer, LeaveRequestSerializer)
from .permissions import IsAdminRole, IsManagerOrAdmin, IsOwnerOrManagerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'manager'):
            return Task.objects.select_related('assigned_to', 'created_by').all()
        return Task.objects.filter(assigned_to=user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_done()
        return Response({'status': 'Task marked as done'})

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        tasks = [t for t in self.get_queryset() if t.is_overdue]
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'manager'):
            return Attendance.objects.select_related('user').all()
        return Attendance.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        today = timezone.now().date()
        if Attendance.objects.filter(user=request.user, date=today).exists():
            return Response({'error': 'Already checked in today'}, status=400)
        record = Attendance.objects.create(
            user=request.user, date=today,
            check_in=timezone.now().time(), status='present'
        )
        return Response(AttendanceSerializer(record).data, status=201)

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        today = timezone.now().date()
        record = Attendance.objects.filter(user=request.user, date=today).first()
        if not record:
            return Response({'error': 'No check-in found for today'}, status=400)
        record.check_out = timezone.now().time()
        record.save()
        return Response(AttendanceSerializer(record).data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'manager'):
            return LeaveRequest.objects.select_related('user').all()
        return LeaveRequest.objects.filter(user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsManagerOrAdmin])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response({'status': 'Leave approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsManagerOrAdmin])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response({'status': 'Leave rejected'})
