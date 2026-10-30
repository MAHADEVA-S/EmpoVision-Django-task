from datetime import date, time
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Attendance, Department, Employee, PerformanceRecord, generate_fake_data
from .serializers import EmployeeSerializer

class EmployeeManagementAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manager", password="StrongPass123!")
        self.department = Department.objects.create(name="Engineering", location="Chennai", budget=Decimal("250000.00"))
        self.employee = Employee.objects.create(first_name="Asha", last_name="Raman",
            email="asha@example.com", phone="+919876543210", position="DEV",
            salary=Decimal("65000.00"), hire_date=date(2024, 1, 15), department=self.department)
        self.client = APIClient()

    def test_employee_records_require_authentication(self):
        response = self.client.get("/api/employees/")
        self.assertIn(response.status_code, (401, 403))

    def test_authenticated_employee_list_returns_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_employee_email_uniqueness_is_enforced(self):
        Employee.objects.create(first_name="Bala", last_name="Kumar", email="bala@example.com",
            phone="1234567890", position="HR", salary=Decimal("40000.00"),
            hire_date=date(2024, 2, 1), department=self.department)
        serializer = EmployeeSerializer(self.employee, data={"email": "bala@example.com"}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_monthly_attendance_summary_works_with_sqlite(self):
        Attendance.objects.create(employee=self.employee, date=date(2026, 10, 1),
            check_in=time(9, 0), check_out=time(18, 0), status="PRESENT")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/attendance/monthly_summary/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["present"], 1)
        self.assertEqual(response.data[0]["date__month"], 10)

    def test_performance_reviewer_comes_from_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/performance/", {
            "employee_id": self.employee.id, "review_date": "2026-10-30",
            "rating": 5, "comments": "Strong delivery and collaboration.",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PerformanceRecord.objects.get().reviewer, self.user)

    def test_department_statistics_include_annotated_metrics(self):
        response = self.client.get("/api/departments/stats/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["employee_count"], 1)
        self.assertEqual(Decimal(response.data[0]["total_salary"]), Decimal("65000.00"))

    def test_fake_data_has_unique_attendance_dates_and_valid_time_order(self):
        generate_fake_data()
        generated = Employee.objects.exclude(id=self.employee.id)
        self.assertEqual(generated.count(), 20)
        for employee in generated:
            records = list(Attendance.objects.filter(employee=employee))
            self.assertEqual(len(records), 20)
            self.assertEqual(len({record.date for record in records}), 20)
            self.assertTrue(all(record.check_out > record.check_in for record in records))

    def test_dashboard_route_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "EmpoVision")
