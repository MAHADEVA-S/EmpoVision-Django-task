from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from .models import Department, Employee, Attendance, PerformanceRecord
from .serializers import DepartmentSerializer, EmployeeSerializer, AttendanceSerializer, PerformanceRecordSerializer, UserSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle]
    search_fields = ["name", "location"]
    ordering_fields = ["name", "budget"]

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def employees(self, request, pk=None):
        records = Employee.objects.filter(department=self.get_object()).select_related("department")
        return Response(EmployeeSerializer(records, many=True).data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request):
        records = Department.objects.annotate(employee_count=Count("employee"),
            avg_salary=Avg("employee__salary"), total_salary=Sum("employee__salary"))
        return Response(self.get_serializer(records, many=True).data)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("department", "user").all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ["position", "department"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["first_name", "last_name", "hire_date", "salary"]

    @action(detail=True, methods=["get"])
    def attendance(self, request, pk=None):
        records = self.get_object().attendance_set.select_related("employee").order_by("-date")
        return Response(AttendanceSerializer(records, many=True).data)

    @action(detail=True, methods=["get"])
    def performance(self, request, pk=None):
        records = self.get_object().performancerecord_set.select_related("employee", "reviewer").order_by("-review_date")
        return Response(PerformanceRecordSerializer(records, many=True).data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        data = {
            "total_employees": Employee.objects.count(),
            "avg_salary": Employee.objects.aggregate(avg=Avg("salary"))["avg"],
            "positions": list(Employee.objects.values("position").annotate(count=Count("id")).order_by("position")),
            "departments": Department.objects.count(),
        }
        return Response(data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related("employee", "employee__department").all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ["employee", "date", "status"]
    ordering_fields = ["date", "check_in", "status"]

    @action(detail=False, methods=["get"])
    def monthly_summary(self, request):
        summary = Attendance.objects.values("date__year", "date__month").annotate(
            present=Count("id", filter=Q(status="PRESENT")),
            absent=Count("id", filter=Q(status="ABSENT")),
            late=Count("id", filter=Q(status="LATE")),
            on_leave=Count("id", filter=Q(status="ON_LEAVE")),
        ).order_by("date__year", "date__month")
        return Response(list(summary))

class PerformanceRecordViewSet(viewsets.ModelViewSet):
    queryset = PerformanceRecord.objects.select_related("employee", "reviewer").all()
    serializer_class = PerformanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filterset_fields = ["employee", "rating"]
    ordering_fields = ["review_date", "rating"]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @action(detail=False, methods=["get"])
    def average_ratings(self, request):
        ratings = PerformanceRecord.objects.values("employee__department__name").annotate(
            avg_rating=Avg("rating"), review_count=Count("id")
        ).order_by("employee__department__name")
        return Response(list(ratings))

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related("employee", "employee__department").all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [UserRateThrottle]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def current_user(self, request):
        return Response(self.get_serializer(request.user).data)
