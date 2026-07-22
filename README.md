# Employee Management System

A fresher-friendly Django HR project with separate HR and employee workflows.

## Main features

- Employee management with profile photos
- Attendance tracking and history
- Leave request and approval workflow
- Task assignment and employee status updates
- Announcements, dashboard charts, Excel export and PDF profiles
- Employee document management with file validation
- Performance reviews with three skill ratings and automatic overall score
- Audit log with actor, module, action type and timestamp
- Simple role separation: linked users are Employees; unlinked authenticated users are HR

## Employee Documents flow

1. HR opens an employee profile and selects **Documents**.
2. HR enters a title, selects Resume/ID Proof/Certificate/Other, and uploads a file.
3. The ModelForm accepts PDF, DOC, DOCX, JPG and PNG files up to 5 MB.
4. Django stores the document against the employee through a ForeignKey.
5. HR can view, download or delete the document.

This is intentionally built with standard Django models, ModelForms, authentication,
templates and media storage so it is easy to explain in an interview.

## Performance Review flow

1. HR opens an employee profile and selects **Reviews**.
2. HR rates technical skills, communication and teamwork from 1 to 5.
3. HR adds strengths, improvement feedback, a period and review date.
4. The model calculates the overall rating as the average of all three ratings.
5. HR can edit/delete reviews, while employees see recent feedback read-only on their dashboard.

## Audit Log flow

1. A reusable `record_audit()` helper runs after important HR changes succeed.
2. It stores the logged-in HR user, Create/Update/Delete action, module, object and description.
3. The dashboard shows the six latest activities.
4. The Activity Log page provides module/action filters and pagination.
5. Employee accounts cannot access the HR activity history.

## Run locally

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

## Tests

```powershell
py manage.py test
```

## Security choices

- HR and Employee pages use role-aware authentication decorators.
- Attendance, leave decisions and task status changes require POST + CSRF.
- Status values are checked against explicit model choices on the server.
- Employee forms reject duplicate emails/usernames and oversized profile images.
- Secret key, debug mode, hosts and trusted origins come from environment variables.
- Copy `.env.example` values into your hosting provider's environment configuration.

## Interview demo flow

1. Log in as HR and show the workforce dashboard and filters.
2. Open an employee profile, upload a document and add a performance review.
3. Mark attendance, approve a leave request and assign a task.
4. Log in as the employee to show personal tasks, feedback and attendance.
5. Return as HR and open Activity Log to prove that important changes were recorded.
6. Run `py manage.py test` to demonstrate automated validation and access-control tests.

## GitHub checklist

- Do not commit `.env`, `db.sqlite3`, uploaded `media/`, logs or `staticfiles/`.
- Add dashboard, documents, reviews and activity-log screenshots to the repository description.
- Configure production values using `.env.example` as the reference.
- Run `py manage.py check --deploy` with production environment values before deployment.
