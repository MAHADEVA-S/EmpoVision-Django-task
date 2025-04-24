from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Department, Employee, Attendance, PerformanceRecord

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'budget')
    search_fields = ('name', 'location')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'position', 'department')
    list_filter = ('position', 'department')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name')

@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'review_date', 'rating', 'reviewer')
    list_filter = ('rating', 'review_date')
    search_fields = ('employee__first_name', 'employee__last_name')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
