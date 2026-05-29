from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Task, TaskComment
from .forms import TaskForm, TaskCommentForm
from accounts.decorators import manager_or_admin_required


@login_required
def task_list(request):
    tasks = Task.objects.select_related('assigned_to', 'created_by')
    if request.user.role == 'employee':
        tasks = tasks.filter(assigned_to=request.user)
    q = request.GET.get('q')
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    page_obj = Paginator(tasks, 15).get_page(request.GET.get('page'))
    return render(request, 'tasks/task_list.html', {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comment_form = TaskCommentForm()
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.task = task
            c.author = request.user
            c.save()
            messages.success(request, 'Comment added.')
            return redirect('tasks:detail', pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task, 'comment_form': comment_form})


@login_required
@manager_or_admin_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.save()
        messages.success(request, 'Task created!')
        return redirect('tasks:list')
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user.role == 'employee' and task.assigned_to != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('tasks:list')
    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Task updated!')
        return redirect('tasks:detail', pk=pk)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})


@login_required
@manager_or_admin_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('tasks:list')
    return render(request, 'tasks/confirm_delete.html', {'object': task, 'type': 'Task'})


@login_required
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'done':
                task.mark_done()
            else:
                task.save()
            messages.success(request, f'Status updated to {new_status}.')
    return redirect('tasks:detail', pk=pk)
