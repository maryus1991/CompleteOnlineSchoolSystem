from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from apps.content.models import Section
from apps.users.students.models import Student
from apps.common.models import BaseModel
from apps.common.models_fields import BaseJalaliDateTimeField
from apps.common.file_storage_script_for_model import UploadPath
from apps.users.accounts.models import User



class Practice(BaseModel):

    class TypeOfQuestions(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "تستی چندگزینه‌ای"
        LONG_ANSWER = "long_answer", "تشریحی"
        IMAGE_BASED = "image_based", "مبتنی بر تصویر"
        PDF_BASED = "pdf_based", "سوال از فایل PDF"

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="practices", verbose_name="جلسه", db_index=True, null=True, blank=True)
    description = CKEditor5Field(blank=True, null=True, verbose_name='متن سوال')
    name = models.CharField(max_length=255, verbose_name="نام تمرین")
    type_of_practice = models.CharField(max_length=30, choices=TypeOfQuestions.choices,  default=TypeOfQuestions.LONG_ANSWER, verbose_name="نوع تمرین",)
    selected_students = models.ManyToManyField(Student, blank=True, related_name="assigned_practices", verbose_name="دانش‌آموزان انتخاب‌شده", )
    start_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان شروع", )
    deadline = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="مهلت انجام تمرین", )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="practices", verbose_name="سازنده", db_index=True, null=True, blank=True)


    class Meta:
        ordering = ["-sort_number", "-pk"]
        verbose_name = "تمرین"
        verbose_name_plural = "تمرین‌ها"

    def __str__(self):
        return self.name

class PracticeStudentDetails(BaseModel):

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "شروع‌نشده"
        IN_PROGRESS = "in_progress", "در حال انجام"
        SUBMITTED = "submitted", "ارسال‌شده"
        CORRECTING = "correcting", "در حال تصحیح"
        CORRECTED = "corrected", "تصحیح‌شده"

    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name="student_details", verbose_name="تمرین")
    question = models.ForeignKey("questions.Question",on_delete=models.CASCADE, related_name="practice_student_details", verbose_name="سوال" )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="practice_details",verbose_name="دانش‌آموز")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED,verbose_name="وضعیت")
    started_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان شروع")
    student_finished_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان ارسال نهایی")
    corrected_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان تصحیح")
    score = models.FloatField(null=True, blank=True, verbose_name="نمره")
    teacher_feedback = models.TextField(blank=True, verbose_name="نظر معلم" )
    answer_text = models.TextField(blank=True, verbose_name="پاسخ متنی")
    answer_image = models.ImageField(upload_to=UploadPath("practice_answers"), blank=True, null=True, verbose_name="تصویر پاسخ")
    answer_pdf = models.FileField(upload_to=UploadPath("practice_answers"), blank=True, null=True, verbose_name="فایل PDF پاسخ")
    submitted_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان ارسال")

    class Meta:
        ordering = ["-pk"]
        verbose_name = "پاسخ دانش‌آموز"
        verbose_name_plural = "پاسخ های دانش‌آموزان"
        constraints = [
            models.UniqueConstraint(
                fields=["practice", "student"],
                name="unique_practice_student",
            ),
        ]

    def __str__(self):
        return f"{self.practice.name} - {self.student}"
