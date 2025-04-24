from rest_framework import serializers
from .models import Department, Employee, Attendance, PerformanceRecord
from django.contrib.auth.models import User

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source='department',
        write_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'position', 'salary', 'hire_date', 'department', 'department_id'
        ]
        extra_kwargs = {
            'email': {'validators': []},  # Disable unique validator for updates
        }

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = '__all__'
        extra_kwargs = {
            'check_out': {'required': False}
        }

class PerformanceRecordSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )
    reviewer = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False,
        allow_null=True
    )

    class Meta:
        model = PerformanceRecord
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'employee']