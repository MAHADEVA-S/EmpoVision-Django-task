from django.db import models
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

class Department(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.location})"

class Employee(models.Model):
    POSITION_CHOICES = [
        ('DEV', 'Developer'),
        ('MGR', 'Manager'),
        ('HR', 'HR'),
        ('ADM', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('ON_LEAVE', 'On Leave'),
    ])

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

class PerformanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_date = models.DateField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField()
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.employee} - {self.review_date} ({self.rating}/5)"

def generate_fake_data():
    # Create departments
    departments = [
        Department.objects.create(
            name=fake.company(),
            location=fake.city(),
            budget=fake.random_number(digits=6)
        ) for _ in range(3)
    ]

    # Create employees
    employees = []
    for _ in range(20):
        emp = Employee.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            position=fake.random_element(elements=('DEV', 'MGR', 'HR', 'ADM')),
            salary=fake.random_number(digits=5),
            hire_date=fake.date_this_decade(),
            department=fake.random_element(elements=departments)
        )
        employees.append(emp)

    # Create attendance records
    for emp in employees:
        for _ in range(20):  # 20 attendance records per employee
            Attendance.objects.create(
                employee=emp,
                date=fake.date_this_year(),
                check_in=fake.time(),
                check_out=fake.time(),
                status=fake.random_element(elements=('PRESENT', 'ABSENT', 'LATE', 'ON_LEAVE'))
            )

    # Create performance records
    for emp in employees:
        for _ in range(2):  # 2 performance reviews per employee
            PerformanceRecord.objects.create(
                employee=emp,
                review_date=fake.date_this_year(),
                rating=fake.random_int(min=1, max=5),
                comments=fake.paragraph(),
                reviewer=None
            )
