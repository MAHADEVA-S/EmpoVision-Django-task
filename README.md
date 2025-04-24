# Employee Management API

A Django REST Framework-based web app for managing employee data.

## Features

- Employee, Department, Attendance, and Performance Record management
- REST API endpoints with filtering and pagination
- Swagger UI documentation
- PostgreSQL database integration
- Authentication and rate limiting
- Synthetic data generation

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-management
   ```

2. **Set up virtual environment and install dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   - Install PostgreSQL if not already installed
   - Create a database named `employee_db` (or update .env with your preferred name)
   - Update .env file with your database credentials if different from defaults

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Generate test data (optional)**
   ```bash
   python manage.py shell
   >>> from api.models import generate_fake_data
   >>> generate_fake_data()
   >>> exit()
   ```

6. **Create superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

Access Swagger UI at: http://localhost:8000/swagger/

## Authentication

- Use Django admin or create users via API
- Obtain auth token: POST to `/api-token-auth/` with username/password
- Include token in headers: `Authorization: Token <your-token>`

## Rate Limits

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour