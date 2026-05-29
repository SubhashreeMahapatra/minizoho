web: python manage.py makemigrations accounts tasks attendance && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn task_attendance_system.wsgi --log-file -
worker: celery -A task_attendance_system worker -l info
beat: celery -A task_attendance_system beat -l info
