# EmpoVision - Employee Management System

A Django REST Framework based employee management system with API endpoints, authentication, and data visualization.

## Features

- Employee data management
- Department organization
- Attendance tracking
- Performance records
- REST API endpoints
- Swagger/OpenAPI documentation
- JWT Authentication
- Rate limiting
- PostgreSQL/SQLite support
- Admin interface

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/MAHADEVA-S/EmpoVision-Django-task.git
cd EmpoVision-Django-task
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure database:
- For SQLite (default): No setup needed
- For PostgreSQL: Update DATABASES in settings.py

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Admin Interface

Access the admin panel at:
http://localhost:8000/admin/

## Generating Test Data

To populate the database with sample data:
```bash
python manage.py shell
>>> from api.models import generate_fake_data
>>> generate_fake_data()
>>> exit()
```

## Project Structure

```
├── api/                  # Main app
│   ├── models.py         # Database models
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views
│   ├── urls.py           # App URLs
│   └── ...
├── employee_management/  # Project config
│   ├── settings.py       # Django settings
│   ├── urls.py           # Project URLs
│   └── ...
├── requirements.txt      # Dependencies
└── manage.py             # Django CLI
```

## Deployment

For production deployment:
1. Set DEBUG=False in settings.py
2. Configure proper database
3. Set up static files
4. Use WSGI server (Gunicorn/uWSGI)
5. Use web server (Nginx/Apache)

## License

MIT License