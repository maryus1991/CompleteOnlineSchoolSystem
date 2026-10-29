from django import forms
from apps.categories.models import LessonCategories
from apps.progress.models import (
    DailyStudyLog,
    StudyPlan,
    StudyPlanItem,
    CounselingSession,
    AdviserExamPrescription,
)


class StudentDailyStudyLogForm(forms.ModelForm):


    class Meta:
        model = DailyStudyLog
        fields = [
            "study_plan_item",
            "lesson",
            "log_date",
            "actual_duration_minutes",
            "tests_total",
            "tests_correct",
            "tests_wrong",
            "focus_quality",
            "student_note",
            "attachment",
        ]
        widgets = {
            "study_plan_item": forms.Select(),
            "lesson": forms.Select(),
            "log_date": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-03 21:00"}),
            "actual_duration_minutes": forms.NumberInput(attrs={"min": 1, "placeholder": "مثال: 90"}),
            "tests_total": forms.NumberInput(attrs={"min": 0}),
            "tests_correct": forms.NumberInput(attrs={"min": 0}),
            "tests_wrong": forms.NumberInput(attrs={"min": 0}),
            "focus_quality": forms.Select(),
            "student_note": forms.Textarea(
                attrs={"rows": 3, "placeholder": "مباحث مطالعه شده، چالش‌ها یا توضیحات تکمیلی..."}
            ),
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["study_plan_item"].required = False
        self.fields["student_note"].required = False
        self.fields["attachment"].required = False
        self.fields["lesson"].queryset = LessonCategories.objects.filter(is_active=True)

        if student is not None:
            self.fields["study_plan_item"].queryset = (
                StudyPlanItem.objects.filter(
                    study_plan__student=student,
                    study_plan__is_active=True,
                    study_plan__status=StudyPlan.Status.ACTIVE,
                    is_active=True,
                )
                .select_related("study_plan", "lesson")
                .order_by("day_of_week", "sort_number")
            )

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get("tests_total") or 0
        correct = cleaned_data.get("tests_correct") or 0
        wrong = cleaned_data.get("tests_wrong") or 0

        if correct + wrong > total:
            self.add_error(
                "tests_total",
                "مجموع تست‌های صحیح و غلط نمی‌تواند بیشتر از تعداد کل تست‌های زده‌شده باشد.",
            )
        return cleaned_data


class StudentSessionRequestForm(forms.ModelForm):
    class Meta:
        model = CounselingSession
        fields = [
            "title",
            "session_type",
            "scheduled_at",
            "duration_minutes",
            "student_request_note",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "موضوع جلسه مورد نظر"}),
            "session_type": forms.Select(),
            "scheduled_at": forms.TextInput(attrs={"placeholder": "زمان پیشنهادی (مثال: 1404-08-06 18:00)"}),
            "duration_minutes": forms.NumberInput(attrs={"min": 15, "max": 120}),
            "student_request_note": forms.Textarea(
                attrs={"rows": 4, "placeholder": "علت درخواست جلسه و سوالاتی که می‌خواهید بررسی شود..."}
            ),
        }


class StudentPrescriptionReflectionForm(forms.ModelForm):
    class Meta:
        model = AdviserExamPrescription
        fields = ["student_reflection"]
        widgets = {
            "student_reflection": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "تعهد و برنامه شما پس از مطالعه نسخه مشاور برای آزمون بعدی...",
                }
            )
        }
