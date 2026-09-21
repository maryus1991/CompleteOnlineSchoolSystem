from django.db import models
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher
from django_ckeditor_5.fields import CKEditor5Field
from apps.categories.models import GradeCategories, MajorCategories, LessonCategories
from apps.common.models import BaseModel
from apps.schools.models import School

class Exam(BaseModel):
    class ExamStatus(models.TextChoices):
        ALL_STATUS = 'همه وضعیت ها ', 'همه وضعیت ها '
        WAITING_START = 'در انتظار شروع', 'در انتظار شروع'
        STARTED = 'شروع شده', 'شروع شده'
        FINISHED = 'پایان یافته', 'پایان یافته'
        WAITING_CORRECTION = 'در انتظار تصحیح', 'در انتظار تصحیح'
        RESULTS_PUBLISHED = 'اعلام نتایج', 'اعلام نتایج'
        DEACTIVATED = 'غیرفعال', 'غیرفعال'
        CANCELED = 'کنسل شده', 'کنسل شده'

    name = models.CharField(verbose_name='عنوان', max_length=255)
    section = models.CharField(verbose_name='مبحث', max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, verbose_name=' نام استان محل برگذاری', null=True, blank=True)
    city = models.CharField(max_length=255, verbose_name='نام شهر محل برگذاری', null=True, blank=True)
    type_of_quiz = models.CharField(max_length=255, verbose_name='محل و نحوه برگذاری', null=True, blank=True)
    price = models.PositiveBigIntegerField(default=0, verbose_name='هزینه')
    time_minutes = models.PositiveIntegerField(default=0, verbose_name='(دقیقه) تایمر')
    start_at = models.DateTimeField(verbose_name='زمان برگذاری')
    stop_at = models.DateTimeField(verbose_name='زمان پایان')
    last_enter = models.DateTimeField(verbose_name='اخرین زمان ورود')
    corrected_at = models.DateTimeField(verbose_name='زمان تصحیح', null=True, blank=True)
    max_score = models.PositiveSmallIntegerField(verbose_name='حداکثر نمره', default=100)
    score = models.FloatField(verbose_name='ضریب', default=1)
    capacity = models.PositiveSmallIntegerField(verbose_name='ظرفیت', default=1)
    filled_capacity = models.PositiveSmallIntegerField(verbose_name=' ظرفیت پر شده', default=0)
    is_online = models.BooleanField(default=True, verbose_name='انلاین')
    change_the_order = models.BooleanField(default=True, verbose_name=' عوض کردن ترتیب سوالات')
    have_negative_score = models.BooleanField(default=True, verbose_name='دارای نمره منفی')
    start_set_report = models.BooleanField(default=False, verbose_name='شروع به تصحیح')
    allow_to_edit_the_answered_questions = models.BooleanField(default=True,verbose_name='امکان ویرایش سوالات پاسخ داده شده')
    allow_return_to_questions = models.BooleanField(default=True, verbose_name='برگشتن به عقب')
    allow_to_edit_the_question_after_the_user_finish = models.BooleanField(default=True,verbose_name='اجازه به ویرایش پاسخ بعد از اتمام کاربر و قبل از اتمام وقت')
    status = models.CharField(verbose_name='وضعیت', choices=ExamStatus, default=ExamStatus.WAITING_START, max_length=55,null=True, blank=True)
    entered_student = models.ManyToManyField(Student, blank=True, related_name='exam_entered_student',editable=False, verbose_name='دانش اموز شرکت کرده')
    selected_student = models.ManyToManyField(Student, blank=True, related_name='exam', verbose_name='دانش اموز انتخاب شده')
    teacher = models.ManyToManyField(Teacher, related_name='exam', verbose_name='معلم' )
    grade = models.ForeignKey(GradeCategories, related_name='exam', on_delete=models.SET_NULL, null=True , verbose_name='پایه')
    school = models.ForeignKey(School, related_name='exam', on_delete=models.SET_NULL, null=True , verbose_name='مدرسه')
    major = models.ForeignKey(MajorCategories, related_name='exam', on_delete=models.SET_NULL, null=True ,verbose_name='رشته')
    lesson = models.ForeignKey(LessonCategories, related_name='exam', on_delete=models.SET_NULL, null=True ,verbose_name='درس' )
    reduce_percent_of_negative_score = models.SmallIntegerField(default=30,verbose_name="درصد کم کردن از نمره در ازای هر سوال اشتباه")
    description = CKEditor5Field("توضیحات")

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'ازمون جامع'
        verbose_name_plural = 'ازمون های جامع'

    def __str__(self):
        return f"{self.id} - {self.name}"


