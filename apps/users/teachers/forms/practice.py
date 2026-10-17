from django import forms

from apps.practice.models import Practice, PracticeStudentDetails
from apps.content.models import Section


class PracticeForm(forms.ModelForm):
    class Meta:
        model = Practice
        fields = [
            "section",
            "name",
            "description",
            "type_of_practice",
            "start_at",
            "deadline",
            "sort_number",
        ]
        widgets = {
            "section": forms.Select(),
            "name": forms.TextInput(attrs={"placeholder": "عنوان تمرین"}),

            "type_of_practice": forms.Select(),
            "start_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 10:00"}),
            "deadline": forms.TextInput(attrs={"placeholder": "مهلت انجام"}),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, teacher=None, section=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["start_at"].required = False
        self.fields["deadline"].required = False
        self.fields["sort_number"].required = False

        if teacher is not None:
            qs = (
                Section.objects.filter(
                    is_active=True,
                    klass__teacher=teacher,
                    klass__is_active=True,
                )
                .select_related("klass")
                .order_by("klass__name", "sort_number", "pk")
            )
            self.fields["section"].queryset = qs
            self.fields["section"].label_from_instance = (
                lambda obj: f"{obj.klass.name} — {obj.name}"
            )

        if section is not None:
            self.fields["section"].initial = section.pk
            self.fields["section"].queryset = Section.objects.filter(pk=section.pk)
            self.fields["section"].widget = forms.HiddenInput()


class PracticeGradeForm(forms.ModelForm):
    class Meta:
        model = PracticeStudentDetails
        fields = ["score", "teacher_feedback", "status"]
        widgets = {
            "score": forms.NumberInput(attrs={"step": "0.25", "min": "0", "placeholder": "نمره"}),
            "teacher_feedback": forms.Textarea(
                attrs={"rows": 4, "placeholder": "نظر و بازخورد معلم..."}
            ),
            "status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher_feedback"].required = False
        self.fields["score"].required = True

        self.fields["status"].choices = [
            (PracticeStudentDetails.Status.CORRECTING, "در حال تصحیح"),
            (PracticeStudentDetails.Status.CORRECTED, "تصحیح‌شده"),
            (PracticeStudentDetails.Status.SUBMITTED, "ارسال‌شده"),
        ]
