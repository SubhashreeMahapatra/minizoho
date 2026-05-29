from django.urls import path
from . import views
app_name = 'tasks'
urlpatterns = [
    path('', views.task_list, name='list'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/status/', views.task_update_status, name='update_status'),
]
