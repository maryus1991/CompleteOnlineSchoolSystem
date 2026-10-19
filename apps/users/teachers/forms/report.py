from django import forms

from apps.reports.models import ExamReport


class ExamReportForm(forms.ModelForm):
    """
    معلم می‌تواند فیلدهای کارنامه را ویرایش کند
    ولی exam و student غیرقابل تغییر هستند.
    """

    class Meta:
        model = ExamReport
        fields = [
            "status",
            "total_questions",
            "correct_count",
            "wrong_count",
            "unanswered_count",
            "skipped_count",
            "uncorrected_count",
            "score",
            "max_score",
            "percentage",
            "answered_percentage",
            "rank",
            "teraze",
            "calculated_at",
            "published_at",
        ]
        widgets = {
            "status": forms.Select(),
            "total_questions": forms.NumberInput(attrs={"min": 0}),
            "correct_count": forms.NumberInput(attrs={"min": 0}),
            "wrong_count": forms.NumberInput(attrs={"min": 0}),
            "unanswered_count": forms.NumberInput(attrs={"min": 0}),
            "skipped_count": forms.NumberInput(attrs={"min": 0}),
            "uncorrected_count": forms.NumberInput(attrs={"min": 0}),
            "score": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
            "max_score": forms.NumberInput(attrs={"step": "0.01", "min": 0}),
            "percentage": forms.NumberInput(attrs={"step": "0.01", "min": 0, "max": 100}),
            "answered_percentage": forms.NumberInput(attrs={"step": "0.01", "min": 0, "max": 100}),
            "rank": forms.NumberInput(attrs={"min": 1}),
            "teraze": forms.NumberInput(attrs={"step": "0.01"}),
            "calculated_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 10:00"}),
            "published_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 12:00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        optional = [
            "rank", "teraze", "calculated_at", "published_at",
            "uncorrected_count", "skipped_count",
        ]
        for f in optional:
            if f in self.fields:
                self.fields[f].required = False