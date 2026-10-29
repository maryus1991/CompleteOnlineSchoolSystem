from django import forms
from django.forms import inlineformset_factory
from apps.categories.models import LessonCategories
from apps.progress.models import StudyPlan, StudyPlanItem
from apps.users.students.models import Student


class StudyPlanForm(forms.ModelForm):
    class Meta:
        model = StudyPlan
        fields = [
            "student",
            "title",
            "start_date",
            "end_date",
            "status",
            "adviser_description",
            "sort_number",
        ]
        widgets = {
            "student": forms.Select(),
            "title": forms.TextInput(attrs={"placeholder": "مثال: برنامه مطالعاتی هفته دوم آبان"}),
            "start_date": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-01 08:00"}),
            "end_date": forms.TextInput(attrs={"placeholder": "مثال: 1404-08-07 23:00"}),
            "status": forms.Select(),
            "sort_number": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, adviser=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adviser_description"].required = False
        self.fields["sort_number"].required = False
        if adviser is not None:
            qs = Student.objects.filter(adviser=adviser, is_active=True).select_related("user")
            if not qs.exists() and adviser.user.is_superuser:
                qs = Student.objects.filter(is_active=True).select_related("user")
            self.fields["student"].queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "تاریخ پایان برنامه نمی‌تواند قبل از تاریخ شروع باشد.")
        return cleaned_data


class StudyPlanItemForm(forms.ModelForm):
    class Meta:
        model = StudyPlanItem
        fields = [
            "day_of_week",
            "lesson",
            "topic",
            "study_type",
            "target_duration_minutes",
            "target_test_count",
            "priority",
            "adviser_tip",
            "sort_number",
        ]
        widgets = {
            "day_of_week": forms.Select(),
            "lesson": forms.Select(),
            "topic": forms.TextInput(attrs={"placeholder": "مبحث یا فصل مورد نظر"}),
            "study_type": forms.Select(),
            "target_duration_minutes": forms.NumberInput(attrs={"min": 0}),
            "target_test_count": forms.NumberInput(attrs={"min": 0}),
            "priority": forms.Select(),
            "adviser_tip": forms.TextInput(attrs={"placeholder": "نکته کلیدی مشاور برای این باکس"}),
            "sort_number": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lesson"].queryset = LessonCategories.objects.filter(is_active=True)
        self.fields["lesson"].required = False
        self.fields["adviser_tip"].required = False
        self.fields["sort_number"].required = False


StudyPlanItemFormSet = inlineformset_factory(
    StudyPlan,
    StudyPlanItem,
    form=StudyPlanItemForm,
    extra=2,
    can_delete=True,
    min_num=0,
    validate_min=False,
)
