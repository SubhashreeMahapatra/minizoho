web: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py shell -c 
"from accounts.models import User; User.objects.filter(username='admin').exists() or 
User.objects.create_superuser('admin', 'admin@example.com', 'Admin@1234')" && gunicorn task_attendance_system.wsgi --log-file -
worker: celery -A task_attendance_system worker -l info
beat: celery -A task_attendance_system beat -l info
