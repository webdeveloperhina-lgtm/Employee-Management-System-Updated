from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('audit-logs/', views.audit_log_list, name='audit_logs'),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'add/',
        views.add_employee,
        name='add_employee'
    ),

    path(
        'employees/',
        views.employee_list,
        name='employee_list'
    ),

    path(
        'edit/<int:id>/',
        views.edit_employee,
        name='edit_employee'
    ),

    path(
        'delete/<int:id>/',
        views.delete_employee,
        name='delete_employee'
    ),

    path(
        'employee/<int:id>/',
        views.employee_detail,
        name='employee_detail'
    ),

    path(
        'employee/<int:employee_id>/documents/',
        views.employee_documents,
        name='employee_documents'
    ),

    path(
        'documents/<int:document_id>/delete/',
        views.delete_employee_document,
        name='delete_employee_document'
    ),

    path(
        'employee/<int:employee_id>/reviews/',
        views.performance_reviews,
        name='performance_reviews'
    ),

    path(
        'reviews/<int:review_id>/delete/',
        views.delete_performance_review,
        name='delete_performance_review'
    ),

    path(
        'export/',
        views.export_employees,
        name='export_employees'
    ),

    path(
        'employee/<int:id>/pdf/',
        views.generate_employee_pdf,
        name='employee_pdf'
    ),

    path(
        'attendance/',
        views.mark_attendance,
        name='mark_attendance'
    ),

    path(
        'attendance/mark/<int:employee_id>/<str:status>/',
        views.mark_attendance_status,
        name='mark_attendance_status'
    ),

    path(
        'attendance/history/<int:employee_id>/',
        views.attendance_history,
        name='attendance_history'
    ),

    path(
        'leave/apply/<int:employee_id>/',
        views.apply_leave,
        name='apply_leave'
    ),

    path(
        'leave/list/',
        views.leave_list,
        name='leave_list'
    ),

    path(
        'leave/update/<int:leave_id>/<str:status>/',
        views.update_leave_status,
        name='update_leave_status'
    ),

    path(
        'leave/history/<int:employee_id>/',
        views.leave_history,
        name='leave_history'
    ),

        path(
        'employee/dashboard/',
        views.employee_dashboard,
        name='employee_dashboard'
    ),

    path(
        'employee/apply-leave/',
        views.employee_apply_leave,
        name='employee_apply_leave'
    ),
    path(
    'employee/update-photo/',
    views.update_profile_photo,
    name='update_profile_photo'
   ),

    path(
       'task/create/',
       views.create_task,
       name='create_task'
    ),

    path(
       'task/list/',
       views.task_list,
       name='task_list'
    ),
    path(
        'task/edit/<int:id>/',
        views.edit_task,
        name='edit_task'
    ),

    path(
        'task/delete/<int:id>/',
        views.delete_task,
        name='delete_task'
    ),

    path(
       'employee/tasks/',
       views.employee_tasks,
       name='employee_tasks'
    ),

    path(
       'task/status/<int:task_id>/<str:status>/',
       views.update_task_status,
       name='update_task_status'
    ),
path(
    'departments/',
    views.department_list,
    name='department_list'
),

path(
    'announcements/',
    views.announcement_list,
    name='announcement_list'
),

path(
    'announcements/delete/<int:id>/',
    views.delete_announcement,
    name='delete_announcement'
),
]
