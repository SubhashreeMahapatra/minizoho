from django.urls import path
from . import views
app_name = 'attendance'
urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('manage/', views.attendance_manage, name='manage'),
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:pk>/review/', views.leave_review, name='leave_review'),
]
