from django import forms
from django.forms import inlineformset_factory

from apps.questions.models import Question, QuestionOption, QuestionAnswerKey
from apps.categories.models import GradeCategories, MajorCategories, LessonCategories
# from

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "name",
            "description",
            "score",
            "type_of_question",
            "image",
            "pdf_file",
            "grade",
            "major",
            "lesson",
            "sort_number",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "عنوان سوال را وارد کنید",
                }
            ),

            "score": forms.NumberInput(
                attrs={
                    "step": "0.25",
                    "min": "0",
                }
            ),
            "type_of_question": forms.Select(),
            "grade": forms.Select(),
            "major": forms.Select(),
            "lesson": forms.Select(),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["grade"].queryset = GradeCategories.objects.filter(is_active=True)
        self.fields["major"].queryset = MajorCategories.objects.filter(is_active=True)
        self.fields["lesson"].queryset = LessonCategories.objects.filter(is_active=True)
        self.fields["grade"].required = True
        self.fields["major"].required = True
        self.fields["lesson"].required = True
        self.fields["image"].required = False
        self.fields["pdf_file"].required = False
        self.fields["description"].required = False


class QuestionAnswerKeyForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswerKey
        fields = [
            "type_of_answer",
            "description",
            "image",
            "pdf_file",
        ]
        widgets = {
            "type_of_answer": forms.Select(),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type_of_answer"].required = True
        self.fields["description"].required = False
        self.fields["image"].required = False
        self.fields["pdf_file"].required = False

    def clean(self):
        cleaned = super().clean()
        type_of_answer = cleaned.get("type_of_answer")
        description = cleaned.get("description")
        image = cleaned.get("image")
        pdf_file = cleaned.get("pdf_file")

        if type_of_answer == QuestionAnswerKey.TypeOfAnswer.TEXT_BASED:
            if not description or not str(description).strip():
                self.add_error("description", "برای پاسخ تشریحی، متن پاسخ الزامی است.")
        elif type_of_answer == QuestionAnswerKey.TypeOfAnswer.IMAGE_BASED:
            if not image and not (self.instance and self.instance.pk and self.instance.image):
                self.add_error("image", "برای پاسخ تصویری، فایل تصویر الزامی است.")
        elif type_of_answer == QuestionAnswerKey.TypeOfAnswer.PDF_BASED:
            if not pdf_file and not (self.instance and self.instance.pk and self.instance.pdf_file):
                self.add_error("pdf_file", "برای پاسخ PDF، فایل PDF الزامی است.")

        return cleaned


class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ["name", "is_correct", "sort_number"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "متن گزینه",
                }
            ),
            "is_correct": forms.CheckboxInput(),
            "sort_number": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields["sort_number"].required = False


QuestionOptionFormSet = inlineformset_factory(
    Question,
    QuestionOption,
    form=QuestionOptionForm,
    extra=4,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


QuestionOptionUpdateFormSet = inlineformset_factory(
    Question,
    QuestionOption,
    form=QuestionOptionForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
)
