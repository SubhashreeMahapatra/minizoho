from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Attendance, LeaveRequest
from .forms import AttendanceForm, CheckInForm, LeaveRequestForm
from accounts.decorators import manager_or_admin_required, admin_required
from accounts.models import User


@login_required
def attendance_list(request):
    records = Attendance.objects.select_related('user')
    if request.user.role == 'employee':
        records = records.filter(user=request.user)
    month = request.GET.get('month')
    user_id = request.GET.get('user')
    if month:
        y, m = month.split('-')
        records = records.filter(date__year=y, date__month=m)
    if user_id and request.user.role != 'employee':
        records = records.filter(user_id=user_id)
    page_obj = Paginator(records, 20).get_page(request.GET.get('page'))
    users = User.objects.filter(is_active=True) if request.user.role != 'employee' else None
    return render(request, 'attendance/attendance_list.html', {'page_obj': page_obj, 'users': users})


@login_required
def check_in(request):
    today = timezone.now().date()
    existing = Attendance.objects.filter(user=request.user, date=today).first()
    if existing:
        messages.warning(request, 'Already checked in today.')
        return redirect('attendance:list')
    form = CheckInForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Attendance.objects.create(
            user=request.user,
            date=today,
            check_in=timezone.now().time(),
            status='present',
            notes=form.cleaned_data.get('notes', '')
        )
        messages.success(request, 'Checked in successfully!')
        return redirect('attendance:list')
    return render(request, 'attendance/check_in.html', {'form': form})


@login_required
def check_out(request):
    today = timezone.now().date()
    record = Attendance.objects.filter(user=request.user, date=today).first()
    if not record:
        messages.error(request, 'No check-in record found for today.')
        return redirect('attendance:list')
    if record.check_out:
        messages.warning(request, 'Already checked out today.')
        return redirect('attendance:list')
    if request.method == 'POST':
        record.check_out = timezone.now().time()
        record.save()
        messages.success(request, f'Checked out. Hours worked: {record.hours_worked}')
        return redirect('attendance:list')
    return render(request, 'attendance/check_out.html', {'record': record})


@login_required
@manager_or_admin_required
def attendance_manage(request):
    form = AttendanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Attendance recorded.')
        return redirect('attendance:list')
    return render(request, 'attendance/attendance_form.html', {'form': form, 'title': 'Record Attendance'})


@login_required
def leave_list(request):
    if request.user.role == 'employee':
        leaves = LeaveRequest.objects.filter(user=request.user)
    else:
        leaves = LeaveRequest.objects.select_related('user', 'reviewed_by').all()
    page_obj = Paginator(leaves, 15).get_page(request.GET.get('page'))
    return render(request, 'attendance/leave_list.html', {'page_obj': page_obj})


@login_required
def leave_apply(request):
    form = LeaveRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.user = request.user
        leave.save()
        messages.success(request, 'Leave request submitted!')
        return redirect('attendance:leave_list')
    return render(request, 'attendance/leave_form.html', {'form': form})


@login_required
@manager_or_admin_required
def leave_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('approved', 'rejected'):
            leave.status = action
            leave.reviewed_by = request.user
            leave.save()
            messages.success(request, f'Leave {action}.')
            return redirect('attendance:leave_list')
    return render(request, 'attendance/leave_review.html', {'leave': leave})
