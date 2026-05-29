from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import User
from .forms import LoginForm, RegisterForm, UserUpdateForm, AdminUserUpdateForm
from .decorators import admin_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect(request.GET.get('next', 'dashboard:home'))
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
@admin_required
def user_list(request):
    users = User.objects.all()
    q = request.GET.get('q')
    role = request.GET.get('role')
    if q:
        users = users.filter(username__icontains=q) | users.filter(first_name__icontains=q)
    if role:
        users = users.filter(role=role)
    page_obj = Paginator(users, 15).get_page(request.GET.get('page'))
    return render(request, 'accounts/user_list.html', {'page_obj': page_obj, 'roles': User.ROLE_CHOICES})

@login_required
@admin_required
def create_user(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'User {user.username} created!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
@admin_required
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = AdminUserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'edit_user': user})

@login_required
@admin_required
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/confirm_delete.html', {'object': user, 'type': 'User'})
