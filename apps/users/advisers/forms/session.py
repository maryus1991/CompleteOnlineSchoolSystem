from django import forms
from apps.progress.models import CounselingSession
from apps.sitesetting.models import Counseling
from apps.users.students.models import Student


class CounselingSessionForm(forms.ModelForm):
    class Meta:
        model = CounselingSession
        fields = [
            "student",
            "title",
            "session_type",
            "scheduled_at",
            "duration_minutes",
            "meeting_link",
            "status",
            "session_summary",
            "private_adviser_note",
        ]
        widgets = {
            "student": forms.Select(),
            "title": forms.TextInput(attrs={"placeholder": "موضوع جلسه مشاوره"}),
            "session_type": forms.Select(),
            "scheduled_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-05 17:30"}),
            "duration_minutes": forms.NumberInput(attrs={"min": 5}),
            "meeting_link": forms.URLInput(attrs={"placeholder": "https://..."}),
            "status": forms.Select(),
            "private_adviser_note": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "یادداشت محرمانه مشاور (برای دانش‌آموز نمایش داده نمی‌شود)...",
                }
            ),
        }

    def __init__(self, *args, adviser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meeting_link"].required = False
        self.fields["session_summary"].required = False
        self.fields["private_adviser_note"].required = False
        if adviser is not None:
            qs = Student.objects.filter(adviser=adviser, is_active=True).select_related("user")
            if not qs.exists() and adviser.user.is_superuser:
                qs = Student.objects.filter(is_active=True).select_related("user")
            self.fields["student"].queryset = qs


class SiteCounselingFollowUpForm(forms.ModelForm):
    class Meta:
        model = Counseling
        fields = ["status", "read", "adviser_follow_up_note"]
        widgets = {
            "status": forms.Select(),
            "adviser_follow_up_note": forms.Textarea(
                attrs={"rows": 3, "placeholder": "نتیجه تماس و پیگیری مشاور..."}
            ),
        }
