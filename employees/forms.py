from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Employee, Leave
from .models import Task
from .models import Announcement, EmployeeDocument, PerformanceReview


class EmployeeForm(forms.ModelForm):

    username = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Login username'
            }
        )
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Login password'
            }
        )
    )

    class Meta:
        model = Employee
        fields = ['name', 'email', 'department', 'photo']
        widgets = {

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-lg'
                }
            ),

            'department': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'IT, HR, Finance...'
                }
            ),

            'photo': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),

        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        existing = Employee.objects.filter(email__iexact=email)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise ValidationError("An employee with this email already exists.")
        return email

    def clean_department(self):
        department = " ".join(self.cleaned_data["department"].split())
        if department.upper() in {"HR", "IT", "QA"}:
            return department.upper()
        return department.title()

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            return username
        users = User.objects.filter(username__iexact=username)
        if self.instance.pk and self.instance.user_id:
            users = users.exclude(pk=self.instance.user_id)
        if users.exists():
            raise ValidationError("This username is already in use.")
        return username

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo or not hasattr(photo, "size"):
            return photo
        if photo.size > 3 * 1024 * 1024:
            raise ValidationError("Profile photo cannot exceed 3 MB.")
        content_type = getattr(photo, "content_type", "")
        if content_type and not content_type.startswith("image/"):
            raise ValidationError("Upload a valid image file.")
        return photo

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if not self.instance.user_id and bool(username) != bool(password):
            raise ValidationError("Username and password are both required to create a login account.")
        return cleaned_data


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['leave_type', 'from_date', 'to_date', 'reason']
        widgets = {

            'leave_type': forms.Select(
                attrs={
                    'class': 'form-control form-control-lg'
                }
            ),

            'from_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'date'
                }
            ),

            'to_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'date'
                }
            ),

            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-lg',
                    'rows': 3,
                    'placeholder': 'Reason for leave...'
                }
            ),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date().isoformat()
        self.fields['from_date'].widget.attrs['min'] = today
        self.fields['to_date'].widget.attrs['min'] = today

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        today = timezone.now().date()

        if from_date and from_date < today:
            raise ValidationError("Leave cannot be applied for a past date.")

        if from_date and to_date and to_date < from_date:
            raise ValidationError("To Date cannot be before From Date.")

        return cleaned_data


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            'employee',
            'title',
            'description',
            'priority',
            'due_date',
        ]

        widgets = {

            'description': forms.Textarea(
                attrs={
                    'rows':4,
                    'placeholder':'Enter task details...'
                }
            ),

            'due_date': forms.DateInput(
                attrs={
                    'type':'date'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date().isoformat()
        self.fields['due_date'].widget.attrs['min'] = today
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-select' if isinstance(field.widget, forms.Select) else 'form-control')

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")
        return due_date


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ["title", "document_type", "file"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Python Certificate",
            }),
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
            }),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if not uploaded_file:
            return uploaded_file

        allowed_extensions = {"pdf", "doc", "docx", "jpg", "jpeg", "png"}
        extension = uploaded_file.name.rsplit(".", 1)[-1].lower()

        if extension not in allowed_extensions:
            raise ValidationError("Upload a PDF, DOC, DOCX, JPG or PNG file.")

        if uploaded_file.size > 5 * 1024 * 1024:
            raise ValidationError("Document size cannot exceed 5 MB.")

        return uploaded_file


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = [
            "review_period",
            "review_date",
            "technical_rating",
            "communication_rating",
            "teamwork_rating",
            "strengths",
            "improvement_areas",
        ]
        widgets = {
            "review_period": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Jan–Jun 2026",
            }),
            "review_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "technical_rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "communication_rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "teamwork_rating": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
            "strengths": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "improvement_areas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
