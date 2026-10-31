from django import forms
from apps.schools.models import School, SchoolAnnouncement


class SchoolInfoForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "name",
            "province",
            "city",
            "phone",
            "address",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "logo",
            "primary_color",
            "secondary_color",
            "welcome_message",
            "phone",
            "address",
            "description",
            "enable_live_classes",
            "enable_exams",
            "enable_advising",
            "enable_tickets",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }


class SchoolAnnouncementForm(forms.ModelForm):
    class Meta:
        model = SchoolAnnouncement
        fields = [
            "title",
            "content",
            "target_audience",
            "is_important",
            "is_active",
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4}),
        }


class AcademicCategoryQuickForm(forms.Form):
    CATEGORY_TYPES = [
        ("grade", "پایه تحصیلی"),
        ("major", "رشته تحصیلی"),
        ("lesson", "درس آموزشی"),
    ]
    category_type = forms.ChoiceField(label="نوع دسته‌بندی", choices=CATEGORY_TYPES)
    name = forms.CharField(label="عنوان", max_length=255)
    sort_number = forms.IntegerField(label="ترتیب نمایش", initial=1, min_value=1, required=False)
