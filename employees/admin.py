from django.contrib import admin
from .models import Employee, EmployeeDocument, PerformanceReview, AuditLog

admin.site.register(Employee)
admin.site.register(EmployeeDocument)
admin.site.register(PerformanceReview)
admin.site.register(AuditLog)
