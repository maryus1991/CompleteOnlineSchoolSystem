from django import forms
from apps.live_classes.models import (
    AdviserLiveSession,
    AdviserLiveSessionReport,
    AdviserLiveSessionRequest,
)
from apps.progress.models import CounselingSession
from apps.users.students.models import Student


def _get_adviser_students_qs(adviser):
    if adviser is None:
        return Student.objects.none()
    qs = Student.objects.filter(adviser=adviser, is_active=True).select_related("user")
    if not qs.exists() and adviser.user.is_superuser:
        qs = Student.objects.filter(is_active=True).select_related("user")
    return qs


def _get_adviser_sessions_qs(adviser):
    if adviser is None:
        return CounselingSession.objects.none()
    return (
        CounselingSession.objects.filter(adviser=adviser, is_active=True)
        .select_related("student", "student__user")
        .order_by("-scheduled_at", "-pk")
    )


class AdviserLiveSessionRequestForm(forms.ModelForm):
    class Meta:
        model = AdviserLiveSessionRequest
        fields = [
            "title",
            "counseling_session",
            "students",
            "preferred_at",
            "duration_minutes",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان درخواست جلسه آنلاین مشاوره"}),
            "counseling_session": forms.Select(),
            "students": forms.SelectMultiple(attrs={"size": "5"}),
            "preferred_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-10 16:00"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "15", "step": "15"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "توضیحات درخواست جلسه آنلاین..."}),
        }

    def __init__(self, *args, adviser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["counseling_session"].required = False
        self.fields["students"].required = False
        self.fields["preferred_at"].required = False
        self.fields["description"].required = False
        if adviser is not None:
            self.fields["students"].queryset = _get_adviser_students_qs(adviser)
            self.fields["counseling_session"].queryset = _get_adviser_sessions_qs(adviser)


class AdviserLiveSessionForm(forms.ModelForm):
    class Meta:
        model = AdviserLiveSession
        fields = [
            "title",
            "status",
            "scheduled_at",
            "counseling_session",
            "students",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان جلسه آنلاین مشاوره"}),
            "status": forms.Select(),
            "scheduled_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-10 16:00"}),
            "counseling_session": forms.Select(),
            "students": forms.SelectMultiple(attrs={"size": "5"}),
        }

    def __init__(self, *args, adviser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scheduled_at"].required = False
        self.fields["counseling_session"].required = False
        self.fields["students"].required = False
        self.fields["status"].choices = [
            (AdviserLiveSession.Status.SCHEDULED, "برنامه‌ریزی‌شده"),
            (AdviserLiveSession.Status.LIVE, "در حال برگزاری"),
            (AdviserLiveSession.Status.COMPLETED, "برگزارشده"),
            (AdviserLiveSession.Status.CANCELLED, "لغوشده"),
        ]
        effective_adviser = adviser or getattr(self.instance, "adviser", None)
        if effective_adviser is not None:
            self.fields["students"].queryset = _get_adviser_students_qs(effective_adviser)
            self.fields["counseling_session"].queryset = _get_adviser_sessions_qs(effective_adviser)


class AdviserLiveSessionReportForm(forms.ModelForm):
    class Meta:
        model = AdviserLiveSessionReport
        fields = [
            "counseling_session",
            "started_at",
            "ended_at",
            "duration_minutes",
            "attendees_count",
            "adviser_note",
            "recording_file",
            "chat_report",
            "attendance_report",
        ]
        widgets = {
            "counseling_session": forms.Select(),
            "started_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-10 16:00"}),
            "ended_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-10 16:45"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "1"}),
            "attendees_count": forms.NumberInput(attrs={"min": "0"}),
            "adviser_note": forms.Textarea(
                attrs={"rows": 4, "placeholder": "یادداشت و جمع‌بندی مشاور از جلسه آنلاین..."}
            ),
        }

    def __init__(self, *args, adviser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["counseling_session"].required = False
        self.fields["started_at"].required = False
        self.fields["ended_at"].required = False
        self.fields["duration_minutes"].required = False
        self.fields["adviser_note"].required = False
        self.fields["recording_file"].required = False
        self.fields["chat_report"].required = False
        self.fields["attendance_report"].required = False
        if adviser is not None:
            self.fields["counseling_session"].queryset = _get_adviser_sessions_qs(adviser)
