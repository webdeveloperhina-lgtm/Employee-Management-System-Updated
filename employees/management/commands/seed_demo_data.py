from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from employees.models import (
    Announcement,
    Attendance,
    AuditLog,
    Employee,
    EmployeeDocument,
    Leave,
    PerformanceReview,
    Task,
)


class Command(BaseCommand):
    help = "Create demo records for interview/demo presentation."

    def handle(self, *args, **options):
        today = timezone.localdate()

        hr_user = User.objects.filter(is_superuser=True).order_by("id").first()
        if not hr_user:
            hr_user, _ = User.objects.get_or_create(
                username="jignesh",
                defaults={"is_staff": True, "is_superuser": True},
            )
            hr_user.set_password("Admin@123")
            hr_user.save()

        employees = self._seed_employees()
        self._seed_attendance(employees, today)
        self._seed_leaves(employees, today)
        self._seed_tasks(employees, today)
        self._seed_announcements()
        self._seed_documents(employees)
        self._seed_reviews(employees, hr_user, today)
        self._seed_audit_logs(hr_user)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(
            "Counts: "
            f"employees={Employee.objects.count()}, "
            f"attendance={Attendance.objects.count()}, "
            f"leaves={Leave.objects.count()}, "
            f"tasks={Task.objects.count()}, "
            f"announcements={Announcement.objects.count()}, "
            f"documents={EmployeeDocument.objects.count()}, "
            f"reviews={PerformanceReview.objects.count()}, "
            f"audit_logs={AuditLog.objects.count()}"
        )

    def _seed_employees(self):
        demo_rows = [
            {
                "name": "Aarav Mehta",
                "email": "aarav.mehta@demo.com",
                "department": "IT",
                "username": "aarav",
            },
            {
                "name": "Priya Shah",
                "email": "priya.shah@demo.com",
                "department": "HR",
                "username": "priya",
            },
            {
                "name": "Karan Patel",
                "email": "karan.patel@demo.com",
                "department": "Finance",
                "username": "karan",
            },
            {
                "name": "Neha Verma",
                "email": "neha.verma@demo.com",
                "department": "Marketing",
                "username": "neha",
            },
        ]

        employees = list(Employee.objects.order_by("id")[:4])

        for row in demo_rows:
            user, _ = User.objects.get_or_create(
                username=row["username"],
                defaults={"email": row["email"]},
            )
            if not user.has_usable_password():
                user.set_password("Employee@123")
                user.save()

            employee, _ = Employee.objects.get_or_create(
                email=row["email"],
                defaults={
                    "name": row["name"],
                    "department": row["department"],
                    "status": "Active",
                    "user": user,
                },
            )
            changed = False
            for field in ("name", "department", "status"):
                if getattr(employee, field) != row[field] if field in row else False:
                    setattr(employee, field, row[field])
                    changed = True
            if not employee.user_id:
                employee.user = user
                changed = True
            if changed:
                employee.save()
            employees.append(employee)

        unique = []
        seen = set()
        for employee in employees:
            if employee.id not in seen:
                unique.append(employee)
                seen.add(employee.id)
        return unique

    def _seed_attendance(self, employees, today):
        statuses = ["Present", "Present", "Absent", "Leave", "Present", "Present", "Present"]
        for index, employee in enumerate(employees[:8]):
            for day_offset in range(7):
                status = statuses[(index + day_offset) % len(statuses)]
                Attendance.objects.update_or_create(
                    employee=employee,
                    date=today - timedelta(days=day_offset),
                    defaults={"status": status},
                )

    def _seed_leaves(self, employees, today):
        leave_rows = [
            (0, "Casual", 3, 4, "Family function", "Pending"),
            (1, "Sick", 6, 6, "Medical appointment", "Approved"),
            (2, "Paid", 12, 14, "Planned vacation", "Rejected"),
            (3, "Casual", 18, 18, "Personal work", "Approved"),
        ]
        for employee_index, leave_type, start, end, reason, status in leave_rows:
            if employee_index >= len(employees):
                continue
            employee = employees[employee_index]
            Leave.objects.update_or_create(
                employee=employee,
                from_date=today + timedelta(days=start),
                to_date=today + timedelta(days=end),
                defaults={
                    "leave_type": leave_type,
                    "reason": reason,
                    "status": status,
                },
            )

    def _seed_tasks(self, employees, today):
        task_rows = [
            (0, "Update employee onboarding checklist", "Review joining steps and keep checklist ready for new hires.", "High", 2, "In Progress"),
            (1, "Prepare monthly attendance summary", "Verify attendance records and share summary with HR.", "Medium", 4, "Pending"),
            (2, "Review payroll data", "Check salary inputs and mark missing employee details.", "High", 6, "Pending"),
            (3, "Create announcement draft", "Prepare a short announcement for the new leave policy.", "Low", 8, "Completed"),
            (0, "Clean employee document records", "Check uploaded documents and rename titles consistently.", "Medium", 10, "Pending"),
        ]
        for employee_index, title, description, priority, due_in_days, status in task_rows:
            if employee_index >= len(employees):
                continue
            Task.objects.update_or_create(
                employee=employees[employee_index],
                title=title,
                defaults={
                    "description": description,
                    "priority": priority,
                    "due_date": today + timedelta(days=due_in_days),
                    "status": status,
                },
            )

    def _seed_announcements(self):
        rows = [
            ("Updated Leave Policy", "All employees can apply leave from the employee portal before the planned date."),
            ("Monthly Review Reminder", "Team leads should complete performance reviews by the end of this week."),
            ("Attendance Regularization", "Please contact HR if today's attendance status is incorrect."),
        ]
        for title, message in rows:
            Announcement.objects.get_or_create(title=title, defaults={"message": message})

    def _seed_documents(self, employees):
        if not employees:
            return

        rows = [
            (employees[0], "Resume", "Resume", "Demo resume content for interview presentation."),
            (employees[0], "Python Certificate", "Certificate", "Demo certificate content."),
            (employees[min(1, len(employees) - 1)], "ID Proof", "ID Proof", "Demo ID proof content."),
        ]
        for employee, title, document_type, content in rows:
            document, created = EmployeeDocument.objects.get_or_create(
                employee=employee,
                title=title,
                defaults={"document_type": document_type},
            )
            if created or not document.file:
                filename = f"{employee.name.lower().replace(' ', '_')}_{title.lower().replace(' ', '_')}.pdf"
                document.file.save(filename, ContentFile(content.encode("utf-8")), save=True)

    def _seed_reviews(self, employees, hr_user, today):
        rows = [
            (0, "Jan-Jun 2026", 4, 4, 5, "Consistent delivery and ownership.", "Can improve documentation discipline."),
            (1, "Jan-Jun 2026", 4, 5, 4, "Strong communication with employees.", "Can use more automation in reporting."),
            (2, "Jan-Jun 2026", 5, 3, 4, "Good analytical thinking.", "Can improve cross-team updates."),
        ]
        for employee_index, period, tech, communication, teamwork, strengths, improvements in rows:
            if employee_index >= len(employees):
                continue
            PerformanceReview.objects.update_or_create(
                employee=employees[employee_index],
                review_period=period,
                defaults={
                    "reviewer": hr_user,
                    "review_date": today - timedelta(days=10 + employee_index),
                    "technical_rating": tech,
                    "communication_rating": communication,
                    "teamwork_rating": teamwork,
                    "strengths": strengths,
                    "improvement_areas": improvements,
                },
            )

    def _seed_audit_logs(self, hr_user):
        rows = [
            ("CREATE", "Employee", "Aarav Mehta", "Created demo employee profile."),
            ("CREATE", "Task", "Prepare monthly attendance summary", "Assigned demo task to HR team."),
            ("UPDATE", "Attendance", "Daily Attendance", "Updated attendance records for demo week."),
            ("UPDATE", "Leave", "Priya Shah", "Approved sick leave request."),
            ("CREATE", "Announcement", "Updated Leave Policy", "Published demo announcement."),
        ]
        for action, module, object_name, description in rows:
            AuditLog.objects.get_or_create(
                action=action,
                module=module,
                object_name=object_name,
                defaults={"actor": hr_user, "description": description},
            )
