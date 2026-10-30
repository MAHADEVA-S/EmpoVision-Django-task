# EmpoVision — Employee Management System

EmpoVision is a Django REST Framework employee-management application. It supports department management, employee records, attendance, performance reviews, token authentication, filtering, API documentation and a responsive people-operations dashboard.

## Stack
- Python 3.11+
- Django 4.2 and Django REST Framework
- SQLite by default; PostgreSQL through environment configuration
- django-filter, django-cors-headers and drf-yasg
- Responsive HTML/CSS/vanilla JavaScript dashboard

## Local setup (Windows PowerShell)
1. Clone this repository and enter its folder.
2. Create an environment: py -3.11 -m venv .venv
3. Activate it: .\.venv\Scripts\Activate.ps1
4. Install dependencies: python -m pip install --upgrade pip, then pip install -r requirements.txt
5. Copy .env.example to .env and set a strong secret for production.
6. Run migrations: python manage.py migrate
7. Create an admin: python manage.py createsuperuser
8. Start the server: python manage.py runserver

Open the dashboard at http://127.0.0.1:8000/, Django Admin at /admin/, Swagger at /swagger/, ReDoc at /redoc/, and the health endpoint at /health/. On macOS/Linux, activate with source .venv/bin/activate.

## API
- Departments: /api/departments/
- Employees: /api/employees/
- Employee statistics: /api/employees/stats/
- Attendance: /api/attendance/
- Monthly attendance: /api/attendance/monthly_summary/
- Performance: /api/performance/
- Average ratings: /api/performance/average_ratings/
- Token authentication: POST /api-token-auth/

Employee, attendance and performance records require authentication. Obtain a token with POST /api-token-auth/ using username/password JSON, then send Authorization: Token followed by the token. Department reads are public; writes require authentication.

## Configuration and security
Copy .env.example to .env. Production must set DJANGO_SECRET_KEY, DJANGO_DEBUG=false, and explicit DJANGO_ALLOWED_HOSTS. CORS is closed by default; configure CORS_ALLOWED_ORIGINS only when required. Employee contact and salary data require authentication. Use HTTPS in production. Never commit .env.

For PostgreSQL, set DB_ENGINE=django.db.backends.postgresql and configure DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, and DB_PORT.

## Verification
Run python manage.py check, python manage.py makemigrations --check --dry-run, and python manage.py test. GitHub Actions runs these checks for pushes and pull requests.

## License
MIT
