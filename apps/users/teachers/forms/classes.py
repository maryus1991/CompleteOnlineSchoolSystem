from django import forms

from apps.content.models import Section, ClassArticle, ClassFile
from apps.live_classes.models import LiveClassRequest  # پس از افزودن مدل


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["name", "is_publish", "sort_number"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "نام جلسه"}),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sort_number"].required = False


class ClassArticleForm(forms.ModelForm):
    class Meta:
        model = ClassArticle
        fields = ["name", "content", "sort_number"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "عنوان مقاله"}),
            "content": forms.Textarea(attrs={"rows": 8, "placeholder": "متن مقاله..."}),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sort_number"].required = False
        self.fields["content"].required = False


class ClassFileForm(forms.ModelForm):
    class Meta:
        model = ClassFile
        fields = ["name", "file", "content", "sort_number"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "نام فایل"}),
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "توضیحات فایل..."}),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].required = False
        self.fields["sort_number"].required = False
        if self.instance and self.instance.pk:
            self.fields["file"].required = False


class LiveClassRequestForm(forms.ModelForm):
    class Meta:
        model = LiveClassRequest
        fields = [
            "section",
            "title",
            "description",
            "preferred_at",
            "duration_minutes",
        ]
        widgets = {
            "section": forms.Select(),
            "title": forms.TextInput(attrs={"placeholder": "عنوان درخواست"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "توضیحات درخواست..."}),
            "preferred_at": forms.TextInput(attrs={"placeholder": "مثال: 1404/07/20 10:00"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "15", "step": "15"}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["preferred_at"].required = False
        if teacher is not None:
            self.fields["section"].queryset = (
                Section.objects.filter(
                    is_active=True,
                    klass__teacher=teacher,
                    klass__is_active=True,
                )
                .select_related("klass")
                .order_by("klass__name", "sort_number", "pk")
            )
            self.fields["section"].label_from_instance = (
                lambda obj: f"{obj.klass.name} — {obj.name}"
            )
