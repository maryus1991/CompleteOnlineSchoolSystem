from django import forms
from django.db.models import Q

from apps.categories.models import GradeCategories, LessonCategories, MajorCategories
from apps.content.models import Section
from apps.exams.models import Exam
from apps.practice.models import Practice
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher


class ManagerExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "name",
            "section",
            "status",
            "grade",
            "major",
            "lesson",
            "teacher",
            "entered_student",
            "start_at",
            "stop_at",
            "last_enter",
            "time_minutes",
            "max_score",
            "score",
            "capacity",
            "have_negative_score",
            "reduce_percent_of_negative_score",
            "allow_to_edit_the_answered_questions",
            "allow_return_to_questions",
            "change_the_order",
            "comprehensive_exam",
            "is_online",
            "is_public",
            "is_free",
            "price",
            "summery",
            "description",
            "image",
            "is_active",
        ]
        widgets = {
            "teacher": forms.SelectMultiple(attrs={"size": 5}),
            "entered_student": forms.SelectMultiple(attrs={"size": 8}),
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
            self.fields["entered_student"].queryset = Student.objects.filter(
                school=school, is_active=True
            ).select_related("user", "grade", "major")


class ManagerExamStatusForm(forms.Form):
    status = forms.ChoiceField(label="وضعیت آزمون", choices=Exam.ExamStatus.choices)
    is_active = forms.BooleanField(label="آزمون فعال باشد", required=False)


class ManagerPracticeForm(forms.ModelForm):
    class Meta:
        model = Practice
        fields = [
            "name",
            "section",
            "type_of_practice",
            "selected_students",
            "start_at",
            "deadline",
            "description",
            "is_active",
        ]
        widgets = {
            "selected_students": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school = school
        if school is not None:
            self.fields["section"].queryset = Section.objects.filter(
                Q(klass__school=school) | Q(klass__teacher__school=school),
                is_active=True,
            ).select_related("klass")
            self.fields["selected_students"].queryset = Student.objects.filter(
                school=school, is_active=True
            ).select_related("user", "grade")
