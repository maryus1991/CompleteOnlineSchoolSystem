
from apps.common.models import BaseModel
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from apps.categories.models import GradeCategories, MajorCategories, LessonCategories
from apps.users.teachers.models import Teacher
from apps.users.students.models import Student
from apps.exams.models import Exam
from apps.content.models import ClassPractice
from apps.common.file_storage_script_for_model import UploadPath


def photo_path_upload_to(*args, **kwargs): return ""

class Question(BaseModel):

    class TypeOfQuestions(models.TextChoices):
        MULTIPLE_CHOICE = 'تستی چند گزینه‌ای', 'تستی چند گزینه‌ای'
        SHORT_ANSWER = 'پاسخ کوتاه', 'پاسخ کوتاه'
        LONG_ANSWER = 'پاسخ تشریحی', 'پاسخ تشریحی'
        IMAGE_BASED = 'مبتنی بر تصویر', 'مبتنی بر تصویر'
        PDF_BASED = 'سوال از فایل PDF', 'سوال از فایل PDF'

    description = CKEditor5Field(blank=True, null=True, verbose_name='متن سوال')
    image = models.ImageField(upload_to=UploadPath("questions"), blank=True, null=True, verbose_name='تصویر سوال')
    pdf_file = models.FileField(upload_to=UploadPath("questions"), blank=True, null=True, verbose_name='فایل PDF سوال')
    name = models.CharField(max_length=255, verbose_name='عنوان سوال')
    type_of_question = models.CharField(max_length=100, choices=TypeOfQuestions.choices, verbose_name='نوع سوال')
    score = models.FloatField(default=1, verbose_name='حداکثر نمره سوال')
    is_for_qbank = models.BooleanField("سوال جزو بانک سوال ؟", default=False)

    exam = models.ForeignKey(Exam, related_name='question', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ازمون")
    practice = models.ForeignKey(ClassPractice, related_name='question', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تمرین")
    grade = models.ForeignKey(GradeCategories, related_name='question', on_delete=models.SET_NULL, null=True , verbose_name='پایه', blank=True)
    major = models.ForeignKey(MajorCategories, related_name='question', on_delete=models.SET_NULL, null=True ,verbose_name='رشته', blank=True)
    lesson = models.ForeignKey(LessonCategories, related_name='question', on_delete=models.SET_NULL, null=True ,verbose_name='درس' , blank=True)



    class Meta:
        ordering = ["-sort_number", '-id']
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'

    def __str__(self):
        return f" {self.name}"


class QuestionOption(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='سوال', db_index=True)
    text = models.CharField(max_length=500, verbose_name='متن گزینه')
    is_correct = models.BooleanField(default=False, verbose_name='گزینه صحیح')

    class Meta:
        ordering = ['-sort_number', "pk"]
        verbose_name = ' گزینه سوال تست'
        verbose_name_plural = 'گزینه‌ها سوالات تستی'

    def __str__(self):
        return f"{self.question.name} - {self.text}"


class QuestionAnswerKey(BaseModel):
    class TypeOfAnswer(models.TextChoices):
        TEXT_BASED = 'پاسخ تشریحی', 'پاسخ تشریحی'
        IMAGE_BASED = 'پاسخ تصویری', 'پاسخ تصویری'
        PDF_BASED = 'پاسخ PDF', 'پاسخ PDF'

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer_key', verbose_name='سوال')
    type_of_answer = models.CharField(max_length=50, choices=TypeOfAnswer.choices, verbose_name='نوع پاسخ صحیح')
    description = CKEditor5Field(blank=True, null=True, verbose_name='متن پاسخ')
    image = models.ImageField(upload_to=UploadPath("questions/key/"), blank=True, null=True, verbose_name='تصویر پاسخ')
    pdf_file = models.FileField(upload_to=UploadPath("questions/key/"), blank=True, null=True, verbose_name='فایل PDF پاسخ')

    class Meta:
        verbose_name = 'پاسخ صحیح (ادمین)'
        verbose_name_plural = 'پاسخ‌های صحیح (ادمین)'

    def __str__(self):
        return f"کلید سوال  - {self.question.name}"


class StudentAnswer(BaseModel):
    class TypeOfCorrect(models.TextChoices):
        not_corrected = 'تصحیح نشده', 'تصحیح نشده'
        wrong = 'کاملا اشتباه', 'کاملا اشتباه'
        weak = 'نیاز به تلاش بیشتر', 'نیاز به تلاش بیشتر'
        average = 'قابل قبول', 'قابل قبول'
        good = 'نسبتا درست', 'نسبتا درست'
        excellent = 'کاملا درست', 'کاملا درست'

    class TypeOfAnswer(models.TextChoices):
        OPTION = 'انتخاب گزینه', 'انتخاب گزینه'
        TEXT_BASED = 'پاسخ متنی', 'پاسخ متنی'
        IMAGE_BASED = 'پاسخ تصویری', 'پاسخ تصویری'
        PDF_BASED = 'پاسخ PDF', 'پاسخ PDF'
        SKIPPED = 'رد شده', 'رد شده'
        NOT_ANSWERED = 'جواب داده نشده', 'جواب داده نشده'

    type_of_answer = models.CharField(max_length=50, choices=TypeOfAnswer.choices, verbose_name='نوع پاسخ', default=TypeOfAnswer.NOT_ANSWERED)
    image = models.ImageField(upload_to=UploadPath("student-answers"), blank=True, null=True, verbose_name='تصویر پاسخ')
    pdf_file = models.FileField(upload_to=UploadPath("student-answers"), blank=True, null=True, verbose_name='فایل PDF پاسخ')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, null=True, blank=True,verbose_name='گزینه انتخاب‌شده')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers', null=True,blank=True, verbose_name='سوال')
    description = models.TextField(blank=True, null=True, verbose_name='متن پاسخ')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answers', verbose_name='دانش‌آموز')

    sanatorium_message = CKEditor5Field(blank=True, null=True, verbose_name='نظر مصصح')
    corrected = models.CharField(max_length=100, choices=TypeOfCorrect.choices, verbose_name='کیفیت جواب',default=TypeOfCorrect.not_corrected )
    corrected_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان تصحیح')
    score = models.FloatField(default=0, verbose_name='نمره داده شده')
    corrected_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True,related_name='corrected_answers', verbose_name='تصحیح‌کننده')

    class Meta:
        ordering = ['student']
        verbose_name = 'پاسخ دانش‌آموز'
        verbose_name_plural = 'پاسخ‌های دانش‌آموزان'
        unique_together = ('student', "question")

    def __str__(self):
        return f"{self.id} - {str(self.student.PhoneNumber).replace(' ', '')} - {self.quiz.name} - {self.score}"

