from django import forms
from apps.progress.models import DailyStudyLog


class DailyLogReviewForm(forms.ModelForm):
    class Meta:
        model = DailyStudyLog
        fields = ["review_status", "adviser_feedback"]
        widgets = {
            "review_status": forms.Select(),
            "adviser_feedback": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "بازخورد، تشویق یا اصلاح روند مطالعاتی این گزارش کار...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adviser_feedback"].required = False
