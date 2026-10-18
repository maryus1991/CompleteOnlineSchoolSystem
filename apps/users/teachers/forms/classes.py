from django import forms

from apps.content.models import Section, ClassArticle, ClassFile
from apps.live_classes.models import LiveClassRequest , LiveClass, LiveClassReport


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

            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sort_number"].required = False



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

            "title",
            "description",
            "preferred_at",
            "duration_minutes",
        ]
        widgets = {

            "title": forms.TextInput(attrs={"placeholder": "عنوان درخواست"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "توضیحات درخواست..."}),
            "preferred_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 10:00"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "15", "step": "15"}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["preferred_at"].required = False




class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ["status"]
        widgets = {

            "status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"].choices = [
            (LiveClass.Status.SCHEDULED, "برنامه‌ریزی‌شده"),
            (LiveClass.Status.LIVE, "در حال برگزاری"),
            (LiveClass.Status.COMPLETED, "برگزارشده"),
            (LiveClass.Status.CANCELLED, "لغوشده"),
        ]




class LiveClassReportForm(forms.ModelForm):
    class Meta:
        model = LiveClassReport
        fields = [
            "started_at",
            "ended_at",
            "duration_minutes",
            "attendees_count",
            "teacher_note",
            "recording_file",
            "chat_report",
            "attendance_report",
        ]
        widgets = {
            "started_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 10:00"}),
            "ended_at": forms.TextInput(attrs={"placeholder": "مثال: 1404-07-20 11:30"}),
            "duration_minutes": forms.NumberInput(attrs={"min": "1"}),
            "attendees_count": forms.NumberInput(attrs={"min": "0"}),
            "teacher_note": forms.Textarea(attrs={"rows": 4, "placeholder": "یادداشت معلم..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["started_at"].required = False
        self.fields["ended_at"].required = False
        self.fields["duration_minutes"].required = False
        self.fields["teacher_note"].required = False
        # files optional on update
        if self.instance and self.instance.pk:
            self.fields["recording_file"].required = False
            self.fields["chat_report"].required = False
            self.fields["attendance_report"].required = False