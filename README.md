# Task & Attendance Management System

A full-featured Django web application for managing employee tasks and attendance with role-based access control, REST API, and automated summaries.

## Tech Stack
- **Backend:** Python 3.11+, Django 4.2, Django REST Framework
- **Database:** MySQL 8.0+
- **Task Queue:** Celery + Redis
- **Auth:** JWT (SimpleJWT) + Session Auth
- **API Docs:** drf-spectacular (Swagger/ReDoc)
- **AI-Assisted Development:** GitHub Copilot

## Features
- **Role-Based Access Control** — Admin, Manager, Employee roles with permission guards
- **Task Management** — Create, assign, track, comment on tasks with priority & status
- **Attendance Tracking** — Check-in/check-out, attendance records, monthly reports
- **Leave Management** — Apply, approve/reject leave requests
- **REST API** — Full CRUD API with JWT authentication for all resources
- **Admin Dashboard** — Summary stats, charts, top performers
- **Automated Summaries** — Celery-powered scheduled reports

## Setup

### 1. Clone & Install
```bash
git clone https://github.com/yourname/task-attendance-system.git
cd task-attendance-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials and secret key
```

### 3. MySQL Setup
```sql
CREATE DATABASE task_attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'taskuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON task_attendance_db.* TO 'taskuser'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Run Migrations & Create Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Seed Sample Data (Optional)
```bash
python manage.py seed_data
```

### 6. Start the Server
```bash
python manage.py runserver
```

### 7. Start Celery (optional, for scheduled tasks)
```bash
celery -A task_attendance_system worker -l info
celery -A task_attendance_system beat -l info
```

## URLs
| URL | Description |
|-----|-------------|
| `/` | Dashboard (redirect) |
| `/accounts/login/` | Login page |
| `/dashboard/` | Main dashboard |
| `/tasks/` | Task list |
| `/attendance/` | Attendance records |
| `/attendance/leaves/` | Leave requests |
| `/accounts/users/` | User management (Admin) |
| `/api/` | REST API root |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc API docs |
| `/admin/` | Django Admin |

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/token/` | Get JWT token |
| POST | `/api/auth/token/refresh/` | Refresh JWT |
| GET/POST | `/api/tasks/` | List / Create tasks |
| GET/PUT/DELETE | `/api/tasks/{id}/` | Task detail |
| POST | `/api/tasks/{id}/complete/` | Mark task done |
| GET | `/api/tasks/overdue/` | List overdue tasks |
| POST | `/api/attendance/check_in/` | Check in |
| POST | `/api/attendance/check_out/` | Check out |
| GET/POST | `/api/leaves/` | Leave requests |
| POST | `/api/leaves/{id}/approve/` | Approve leave |

## Running Tests
```bash
python manage.py test tests/
# With coverage:
coverage run --source='.' manage.py test tests/
coverage report
coverage html
```

## Role Permissions Summary
| Feature | Admin | Manager | Employee |
|---------|-------|---------|----------|
| View all tasks | ✅ | ✅ | Own only |
| Create/delete tasks | ✅ | ✅ | ❌ |
| Manage users | ✅ | ❌ | ❌ |
| View all attendance | ✅ | ✅ | Own only |
| Approve leaves | ✅ | ✅ | ❌ |
| View reports | ✅ | ✅ | ❌ |

## Project Structure
```
task_attendance_system/
├── accounts/          # User model, auth, role management
├── tasks/             # Task CRUD, comments
├── attendance/        # Check-in/out, leave requests
├── dashboard/         # Summary views & charts
├── api/               # DRF ViewSets & serializers
├── tests/             # Unit & integration tests
├── templates/         # HTML templates
├── static/            # CSS, JS
├── manage.py
├── requirements.txt
└── .env.example
```
