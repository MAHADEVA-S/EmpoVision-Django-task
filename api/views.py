from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum
from .models import Department, Employee, Attendance, PerformanceRecord
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    AttendanceSerializer,
    PerformanceRecordSerializer,
    UserSerializer
)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle]

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        department = self.get_object()
        employees = department.employee_set.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = Department.objects.annotate(
            employee_count=Count('employee'),
            avg_salary=Avg('employee__salary'),
            total_salary=Sum('employee__salary')
        )
        serializer = self.get_serializer(stats, many=True)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ['position', 'department']

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        employee = self.get_object()
        attendance = employee.attendance_set.all()
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        employee = self.get_object()
        performance = employee.performancerecord_set.all()
        serializer = PerformanceRecordSerializer(performance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats = {
            'total_employees': Employee.objects.count(),
            'avg_salary': Employee.objects.aggregate(avg=Avg('salary'))['avg'],
            'positions': Employee.objects.values('position').annotate(count=Count('id'))
        }
        return Response(stats)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ['employee', 'date', 'status']

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        summary = Attendance.objects.extra(
            {'month': "date_trunc('month', date)"}
        ).values('month').annotate(
            present=Count('id', filter=models.Q(status='PRESENT')),
            absent=Count('id', filter=models.Q(status='ABSENT')),
            late=Count('id', filter=models.Q(status='LATE'))
        )
        return Response(summary)

class PerformanceRecordViewSet(viewsets.ModelViewSet):
    queryset = PerformanceRecord.objects.all()
    serializer_class = PerformanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ['employee', 'rating']

    @action(detail=False, methods=['get'])
    def average_ratings(self, request):
        ratings = PerformanceRecord.objects.values(
            'employee__department__name'
        ).annotate(
            avg_rating=Avg('rating')
        )
        return Response(ratings)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [UserRateThrottle]

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
