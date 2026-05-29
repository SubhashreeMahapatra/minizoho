web: python manage.py collectstatic --noinput && python manage.py migrate --run-syncdb && gunicorn task_attendance_system.wsgi --log-file -
worker: celery -A task_attendance_system worker -l info
beat: celery -A task_attendance_system beat -l info
