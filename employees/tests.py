from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from pathlib import Path

from .forms import EmployeeDocumentForm, PerformanceReviewForm, EmployeeForm
from .models import Employee, EmployeeDocument, PerformanceReview, AuditLog, Attendance, Leave, Task


class EmployeeDocumentFormTests(TestCase):
    def test_rejects_unsupported_file_type(self):
        form = EmployeeDocumentForm(
            data={"title": "Unsafe file", "document_type": "Other"},
            files={"file": SimpleUploadedFile("script.exe", b"content")},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Upload a PDF", form.errors["file"][0])

    def test_accepts_pdf_document(self):
        form = EmployeeDocumentForm(
            data={"title": "Resume", "document_type": "Resume"},
            files={"file": SimpleUploadedFile(
                "resume.pdf", b"%PDF test", content_type="application/pdf"
            )},
        )

        self.assertTrue(form.is_valid())


@override_settings(MEDIA_ROOT=Path(__file__).resolve().parent.parent / ".test_media")
class EmployeeDocumentAccessTests(TestCase):
    def setUp(self):
        self.hr_user = User.objects.create_user("hr_manager", password="test-pass-123")
        self.employee_user = User.objects.create_user("employee_user", password="test-pass-123")
        self.employee = Employee.objects.create(
            user=self.employee_user,
            name="Test Employee",
            email="employee@example.com",
            department="IT",
        )
        self.url = reverse("employee_documents", args=[self.employee.id])

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_hr_can_open_employee_documents(self):
        self.client.force_login(self.hr_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved Documents")

    def test_employee_cannot_open_hr_document_manager(self):
        self.client.force_login(self.employee_user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("employee_dashboard"))

    def test_hr_can_upload_document(self):
        self.client.force_login(self.hr_user)
        response = self.client.post(self.url, {
            "title": "Python Certificate",
            "document_type": "Certificate",
            "file": SimpleUploadedFile(
                "certificate.pdf", b"%PDF test", content_type="application/pdf"
            ),
        })

        self.assertRedirects(response, self.url)
        self.assertTrue(EmployeeDocument.objects.filter(employee=self.employee).exists())


class PerformanceReviewTests(TestCase):
    def setUp(self):
        self.hr_user = User.objects.create_user("review_hr", password="test-pass-123")
        self.employee_user = User.objects.create_user("review_employee", password="test-pass-123")
        self.employee = Employee.objects.create(
            user=self.employee_user,
            name="Review Employee",
            email="review@example.com",
            department="Finance",
        )
        self.url = reverse("performance_reviews", args=[self.employee.id])

    def test_overall_rating_is_automatic_average(self):
        review = PerformanceReview.objects.create(
            employee=self.employee,
            reviewer=self.hr_user,
            review_period="Jan-Jun 2026",
            technical_rating=5,
            communication_rating=4,
            teamwork_rating=3,
            strengths="Reliable delivery",
            improvement_areas="Presentation skills",
        )
        self.assertEqual(review.overall_rating, 4.0)

    def test_form_rejects_rating_above_five(self):
        form = PerformanceReviewForm(data={
            "review_period": "Jan-Jun 2026",
            "review_date": "2026-07-18",
            "technical_rating": 6,
            "communication_rating": 4,
            "teamwork_rating": 4,
            "strengths": "Good coding",
            "improvement_areas": "Communication",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("technical_rating", form.errors)

    def test_hr_can_create_review(self):
        self.client.force_login(self.hr_user)
        response = self.client.post(self.url, {
            "review_period": "Jan-Jun 2026",
            "review_date": "2026-07-18",
            "technical_rating": 5,
            "communication_rating": 4,
            "teamwork_rating": 4,
            "strengths": "Strong Python fundamentals",
            "improvement_areas": "Practice presentations",
        })
        self.assertRedirects(response, self.url)
        self.assertEqual(PerformanceReview.objects.filter(employee=self.employee).count(), 1)

    def test_employee_cannot_manage_reviews(self):
        self.client.force_login(self.employee_user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("employee_dashboard"))


class AuditLogTests(TestCase):
    def setUp(self):
        self.hr_user = User.objects.create_user("audit_hr", password="test-pass-123")
        self.employee = Employee.objects.create(
            name="Audit Employee",
            email="audit@example.com",
            department="HR",
        )

    def test_creating_review_records_audit_entry(self):
        self.client.force_login(self.hr_user)
        response = self.client.post(
            reverse("performance_reviews", args=[self.employee.id]),
            {
                "review_period": "Annual 2026",
                "review_date": "2026-07-18",
                "technical_rating": 4,
                "communication_rating": 4,
                "teamwork_rating": 5,
                "strengths": "Team collaboration",
                "improvement_areas": "Documentation",
            },
        )
        self.assertEqual(response.status_code, 302)
        log = AuditLog.objects.get(module="Performance")
        self.assertEqual(log.actor, self.hr_user)
        self.assertEqual(log.action, "CREATE")
        self.assertIn(self.employee.name, log.description)

    def test_hr_can_filter_activity_log(self):
        AuditLog.objects.create(
            actor=self.hr_user,
            action="CREATE",
            module="Employee",
            object_name=self.employee.name,
            description="Employee created.",
        )
        self.client.force_login(self.hr_user)
        response = self.client.get(reverse("audit_logs"), {"module": "Employee"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Employee created.")

    def test_anonymous_user_cannot_view_activity_log(self):
        response = self.client.get(reverse("audit_logs"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class SecurityFlowTests(TestCase):
    def setUp(self):
        self.hr_user = User.objects.create_user("secure_hr", password="test-pass-123")
        self.employee_user = User.objects.create_user("secure_employee", password="test-pass-123")
        self.employee = Employee.objects.create(
            user=self.employee_user,
            name="Secure Employee",
            email="secure@example.com",
            department="IT",
        )

    def test_attendance_update_rejects_get_and_accepts_valid_post(self):
        url = reverse("mark_attendance_status", args=[self.employee.id, "Present"])
        self.client.force_login(self.hr_user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertTrue(Attendance.objects.filter(employee=self.employee, status="Present").exists())

    def test_attendance_update_rejects_unknown_status(self):
        self.client.force_login(self.hr_user)
        url = reverse("mark_attendance_status", args=[self.employee.id, "Unknown"])
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_leave_decision_requires_post(self):
        leave = Leave.objects.create(
            employee=self.employee,
            leave_type="Casual",
            from_date="2026-08-01",
            to_date="2026-08-02",
            reason="Personal work",
        )
        url = reverse("update_leave_status", args=[leave.id, "Approved"])
        self.client.force_login(self.hr_user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        leave.refresh_from_db()
        self.assertEqual(leave.status, "Approved")

    def test_employee_can_only_update_own_task_by_post(self):
        task = Task.objects.create(
            employee=self.employee,
            title="Security task",
            description="Test task permissions",
            priority="Medium",
            due_date="2026-08-10",
        )
        url = reverse("update_task_status", args=[task.id, "In Progress"])
        self.client.force_login(self.employee_user)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 302)
        task.refresh_from_db()
        self.assertEqual(task.status, "In Progress")

    def test_employee_form_rejects_duplicate_email(self):
        form = EmployeeForm(data={
            "name": "Duplicate",
            "email": "SECURE@example.com",
            "department": "Finance",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_task_delete_confirmation_template_exists(self):
        task = Task.objects.create(
            employee=self.employee,
            title="Delete page task",
            description="Template regression test",
            priority="Low",
            due_date="2026-08-10",
        )
        self.client.force_login(self.hr_user)
        response = self.client.get(reverse("delete_task", args=[task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_task.html")

    def test_employee_tasks_page_exists(self):
        self.client.force_login(self.employee_user)
        response = self.client.get(reverse("employee_tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employee_tasks.html")


class DashboardTests(TestCase):
    def setUp(self):
        self.hr_user = User.objects.create_user("dashboard_hr", password="test-pass-123")
        self.employee = Employee.objects.create(
            name="Dashboard Employee",
            email="dashboard@example.com",
            department="Engineering",
        )

    def test_hr_dashboard_renders_database_backed_widgets(self):
        Attendance.objects.create(employee=self.employee, status="Present")
        Task.objects.create(
            employee=self.employee,
            title="Dashboard task",
            description="Visible in dashboard totals",
            priority="High",
            due_date="2026-08-10",
        )
        self.client.force_login(self.hr_user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Attendance Overview")
        self.assertContains(response, "Employees By Department")
        self.assertEqual(response.context["present_today"], 1)
        self.assertEqual(response.context["pending_tasks"], 1)
        self.assertEqual(response.context["department_labels"], ["Engineering"])
