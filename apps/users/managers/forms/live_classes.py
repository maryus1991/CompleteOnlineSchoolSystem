from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from apps.classes.models import Class
from apps.live_classes.models import (
    AdviserLiveSession,
    LiveClass,
    StreamServers,
)
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student


class ManagerLiveClassForm(forms.ModelForm):
    """
    فرم ایجاد و ویرایش کلاس آنلاین توسط مدیر مدرسه.
    فقط سرورهای متعلق به این مدرسه (school=manager_school) یا سرورهای عمومی (school=None)
    قابل مشاهده و انتخاب هستند.
    """

    class Meta:
        model = LiveClass
        fields = ["klass", "server", "status", "is_active"]

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        if school is not None:
            self.fields["klass"].queryset = (
                Class.objects.filter(
                    Q(school=school) | Q(teacher__school=school),
                    is_active=True,
                )
                .select_related("teacher__user", "grade", "lesson")
                .distinct()
            )
            self.fields["server"].queryset = StreamServers.objects.filter(
                Q(school=school) | Q(school__isnull=True),
                is_active=True,
            ).select_related("school")

    def clean_server(self):
        server = self.cleaned_data.get("server")
        if server and self.school:
            if server.school_id is not None and server.school_id != self.school.id:
                raise ValidationError(
                    "شما فقط مجاز به انتخاب سرورهای اختصاصی مدرسه خود یا سرورهای عمومی هستید."
                )
        return server


class ManagerAdviserLiveSessionForm(forms.ModelForm):
    class Meta:
        model = AdviserLiveSession
        fields = [
            "title",
            "adviser",
            "students",
            "server",
            "scheduled_at",
            "status",
            "is_active",
        ]
        widgets = {
            "students": forms.SelectMultiple(attrs={"size": 7}),
        }

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        if school is not None:
            self.fields["adviser"].queryset = Adviser.objects.filter(
                school=school, is_active=True
            ).select_related("user")
            self.fields["students"].queryset = Student.objects.filter(
                school=school, is_active=True
            ).select_related("user", "grade")
            self.fields["server"].queryset = StreamServers.objects.filter(
                Q(school=school) | Q(school__isnull=True),
                is_active=True,
            ).select_related("school")

    def clean_server(self):
        server = self.cleaned_data.get("server")
        if server and self.school:
            if server.school_id is not None and server.school_id != self.school.id:
                raise ValidationError(
                    "شما فقط مجاز به انتخاب سرورهای اختصاصی مدرسه خود یا سرورهای عمومی هستید."
                )
        return server


class ManagerLiveRequestReviewForm(forms.Form):
    STATUS_CHOICES = [
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
        ("cancelled", "لغو شده"),
    ]
    status = forms.ChoiceField(label="تصمیم مدیر", choices=STATUS_CHOICES)
    admin_note = forms.CharField(
        label="یادداشت مدیر مدرسه",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
