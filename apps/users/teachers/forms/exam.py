from django import forms
from django_ckeditor_5.fields import CKEditor5Field

from apps.exams.models import Exam
from apps.categories.models import GradeCategories, MajorCategories, LessonCategories


class ExamForm(forms.ModelForm):
    description = CKEditor5Field()

    class Meta:
        model = Exam
        fields = [
            "name",
            "section",
            "type_of_quiz",
            "summery",
            "description",
            "price",
            "time_minutes",
            "start_at",
            "stop_at",
            "last_enter",
            "max_score",
            "score",
            "capacity",
            "have_negative_score",
            "reduce_percent_of_negative_score",
            "allow_to_edit_the_answered_questions",
            "allow_return_to_questions",
            "change_the_order",
            "use_js_image_converter_to_pdf",
            "grade",
            "major",
            "lesson",
            "is_public",
            "is_free",
            "is_online",
            "image",
            "status",
            "sort_number",
            # فیلدهای آماری (فقط نمایش)
            "average_percentage",
            "std_percentage",
            "average_score",
            "std_score",
            "participants_count",
            "stats_calculated_at",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "عنوان آزمون"}),
            "section": forms.TextInput(attrs={"placeholder": "مبحث"}),
            "type_of_quiz": forms.TextInput(attrs={"placeholder": "محل و نحوه برگزاری"}),
            "summery": forms.TextInput(attrs={"placeholder": "توضیح کوتاه"}),
            "price": forms.NumberInput(attrs={"min": "0"}),
            "time_minutes": forms.NumberInput(attrs={"min": "0"}),
            "max_score": forms.NumberInput(attrs={"min": "0"}),
            "score": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
            "capacity": forms.NumberInput(attrs={"min": "1"}),
            "reduce_percent_of_negative_score": forms.NumberInput(attrs={"min": "0", "max": "100"}),
            "start_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 10:00"}),
            "stop_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 12:00"}),
            "last_enter": forms.TextInput(attrs={"placeholder": "آخرین زمان ورود"}),
            "status": forms.Select(),
            "grade": forms.Select(),
            "major": forms.Select(),
            "lesson": forms.Select(),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),

            # فیلدهای آماری - فقط خواندنی
            "average_percentage": forms.NumberInput(attrs={"readonly": "readonly", "class": "bg-light"}),
            "std_percentage": forms.NumberInput(attrs={"readonly": "readonly", "class": "bg-light"}),
            "average_score": forms.NumberInput(attrs={"readonly": "readonly", "class": "bg-light"}),
            "std_score": forms.NumberInput(attrs={"readonly": "readonly", "class": "bg-light"}),
            "participants_count": forms.NumberInput(attrs={"readonly": "readonly", "class": "bg-light"}),
            "stats_calculated_at": forms.TextInput(attrs={"readonly": "readonly", "class": "bg-light"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["grade"].queryset = GradeCategories.objects.filter(is_active=True)
        self.fields["major"].queryset = MajorCategories.objects.filter(is_active=True)
        self.fields["lesson"].queryset = LessonCategories.objects.filter(is_active=True)

        optional = [
            "section", "type_of_quiz", "summery", "description", "image",
            "grade", "major", "lesson", "status",
        ]
        for f in optional:
            if f in self.fields:
                self.fields[f].required = False

        if self.instance and self.instance.pk:
            self.fields["image"].required = False
        else:
            # در حالت ساخت آزمون جدید، فیلدهای آماری را اصلاً نشان نده
            for field_name in [
                "average_percentage", "std_percentage",
                "average_score", "std_score",
                "participants_count", "stats_calculated_at",
            ]:
                self.fields.pop(field_name, None)

        # اطمینان از غیرقابل ویرایش بودن
        for field_name in [
            "average_percentage", "std_percentage",
            "average_score", "std_score",
            "participants_count", "stats_calculated_at",
        ]:
            if field_name in self.fields:
                self.fields[field_name].disabled = True
                self.fields[field_name].required = False