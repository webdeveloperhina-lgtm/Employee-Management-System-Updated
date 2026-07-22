from django.db import migrations


def normalize_departments(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    abbreviations = {"HR", "IT", "QA"}

    for employee in Employee.objects.only("id", "department").iterator():
        value = " ".join(employee.department.split())
        normalized = value.upper() if value.upper() in abbreviations else value.title()
        if normalized != employee.department:
            Employee.objects.filter(pk=employee.pk).update(department=normalized)


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0012_auditlog"),
    ]

    operations = [
        migrations.RunPython(normalize_departments, migrations.RunPython.noop),
    ]
