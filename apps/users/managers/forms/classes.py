from django import forms
from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.classes.models import Class
from apps.content.models import ClassArticle, ClassFile, Section
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


class ManagerClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = [
            "name",
            "teacher",
            "grade",
            "major",
            "lesson",
            "student",
            "summery",
            "text",
            "image",
            "is_public",
            "is_free",
            "price",
            "first_tag",
            "second_tag",
            "third_tag",
            "is_active",
        ]
        widgets = {
            "student": forms.SelectMultiple(attrs={"size": 8}),
            "summery": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        self.fields["image"].required = False
        self.fields["grade"].queryset = GradeCategories.objects.filter(is_active=True)
        self.fields["major"].queryset = MajorCategories.objects.filter(is_active=True)
        self.fields["lesson"].queryset = LessonCategories.objects.filter(is_active=True)
        if school is not None:
            self.fields["teacher"].queryset = Teacher.objects.filter(
                school=school, is_active=True
            ).select_related("user")
            self.fields["student"].queryset = Student.objects.filter(
                school=school, is_active=True
            ).select_related("user", "grade", "major")


class ManagerSectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["name", "is_publish", "sort_number", "is_active"]


class ManagerClassArticleForm(forms.ModelForm):
    class Meta:
        model = ClassArticle
        fields = ["name", "content", "sort_number", "is_active"]


class ManagerClassFileForm(forms.ModelForm):
    class Meta:
        model = ClassFile
        fields = ["name", "file", "content", "sort_number", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["file"].required = False
