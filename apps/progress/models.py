from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.models import BaseModel
from apps.common.models_fields import BaseJalaliDateTimeField
from apps.common.file_storage_script_for_model import UploadPath


class StudyPlan(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        ACTIVE = "active", "فعال و در حال اجرا"
        COMPLETED = "completed", "پایان‌یافته"
        ARCHIVED = "archived", "آرشیو شده"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="study_plans",
        verbose_name="دانش‌آموز",
    )
    adviser = models.ForeignKey(
        "advisers.Adviser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_study_plans",
        verbose_name="مشاور",
    )
    title = models.CharField(max_length=255, verbose_name="عنوان برنامه")
    start_date = BaseJalaliDateTimeField(verbose_name="تاریخ شروع برنامه")
    end_date = BaseJalaliDateTimeField(verbose_name="تاریخ پایان برنامه")
    adviser_description = CKEditor5Field(
        blank=True,
        null=True,
        verbose_name="توضیحات و استراتژی کلی مشاور",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت",
    )

    def completion_percentage(self):
        total = self.items.count()
        if total == 0:
            return 0
        done = self.items.filter(is_completed_by_student=True).count()
        return round((done / total) * 100)

    def __str__(self):
        return f"{self.title} - {self.student}"

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'برنامه مطالعاتی'
        verbose_name_plural = 'برنامه‌های مطالعاتی'


class StudyPlanItem(BaseModel):
    class DayOfWeek(models.IntegerChoices):
        SATURDAY = 0, "شنبه"
        SUNDAY = 1, "یکشنبه"
        MONDAY = 2, "دوشنبه"
        TUESDAY = 3, "سه‌شنبه"
        WEDNESDAY = 4, "چهارشنبه"
        THURSDAY = 5, "پنج‌شنبه"
        FRIDAY = 6, "جمعه"

    class StudyType(models.TextChoices):
        READING = "reading", "مطالعه تشریحی/مفهومی"
        TESTING = "testing", "تست‌زنی آموزشی/زمان‌دار"
        REVIEW = "review", "مرور و جمع‌بندی"
        EXAM_ANALYSIS = "exam_analysis", "تحلیل آزمون"
        CLASS_PRACTICE = "class_practice", "کلاس و حل تمرین"

    class Priority(models.TextChoices):
        LOW = "low", "عادی"
        MEDIUM = "medium", "مهم"
        HIGH = "high", "حیاتی/فوری"

    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="برنامه مطالعاتی",
    )
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        verbose_name="روز هفته",
    )
    lesson = models.ForeignKey(
        "categories.LessonCategories",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_plan_items",
        verbose_name="درس",
    )
    topic = models.CharField(max_length=255, verbose_name="مبحث / سرفصل")
    study_type = models.CharField(
        max_length=20,
        choices=StudyType.choices,
        default=StudyType.READING,
        verbose_name="نوع مطالعه",
    )
    target_duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name="زمان هدف (دقیقه)",
    )
    target_test_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد تست هدف",
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="اولویت",
    )
    is_completed_by_student = models.BooleanField(
        default=False,
        verbose_name="انجام‌شده توسط دانش‌آموز",
    )
    completed_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان تکمیل",
    )
    adviser_tip = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="نکته مشاور برای این باکس",
    )

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.topic}"

    class Meta:
        ordering = ['day_of_week', 'sort_number']
        verbose_name = 'آیتم برنامه مطالعاتی'
        verbose_name_plural = 'آیتم‌های برنامه مطالعاتی'


class DailyStudyLog(BaseModel):
    class FocusQuality(models.IntegerChoices):
        ONE = 1, "۱ - خیلی ضعیف"
        TWO = 2, "۲ - ضعیف"
        THREE = 3, "۳ - متوسط"
        FOUR = 4, "۴ - خوب"
        FIVE = 5, "۵ - عالی"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی مشاور"
        APPROVED = "approved", "تایید شده توسط مشاور"
        NEEDS_REVISION = "needs_revision", "نیازمند اصلاح روند"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="daily_logs",
        verbose_name="دانش‌آموز",
    )
    study_plan_item = models.ForeignKey(
        StudyPlanItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
        verbose_name="آیتم برنامه مرتبط",
    )
    lesson = models.ForeignKey(
        "categories.LessonCategories",
        on_delete=models.SET_NULL,
        null=True,
        related_name="daily_logs",
        verbose_name="درس",
    )
    log_date = BaseJalaliDateTimeField(verbose_name="تاریخ مطالعه")
    actual_duration_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="مدت مطالعه واقعی (دقیقه)",
    )
    tests_total = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد کل تست زده‌شده",
    )
    tests_correct = models.PositiveIntegerField(
        default=0,
        verbose_name="تست صحیح",
    )
    tests_wrong = models.PositiveIntegerField(
        default=0,
        verbose_name="تست غلط",
    )
    focus_quality = models.IntegerField(
        choices=FocusQuality.choices,
        default=FocusQuality.THREE,
        verbose_name="کیفیت تمرکز",
    )
    student_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات دانش‌آموز",
    )
    attachment = models.FileField(
        upload_to=UploadPath("progress/daily_logs/"),
        null=True,
        blank=True,
        verbose_name="تصویر گزارش کار یا برگ چک‌لیست",
    )
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        verbose_name="وضعیت بررسی",
    )
    adviser_feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name="بازخورد مشاور روی گزارش کار",
    )
    reviewed_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بررسی مشاور",
    )

    def __str__(self):
        return f"{self.student} - {self.lesson or 'بدون درس'} ({self.actual_duration_minutes} دقیقه)"

    class Meta:
        ordering = ['-log_date']
        verbose_name = 'گزارش کار روزانه'
        verbose_name_plural = 'گزارش‌های کار روزانه'


class AdviserExamPrescription(BaseModel):
    exam_report = models.OneToOneField(
        "reports.ExamReport",
        on_delete=models.CASCADE,
        related_name="adviser_prescription",
        verbose_name="کارنامه آزمون",
    )
    adviser = models.ForeignKey(
        "advisers.Adviser",
        on_delete=models.SET_NULL,
        null=True,
        related_name="exam_prescriptions",
        verbose_name="مشاور تحلیل‌گر",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="exam_prescriptions",
        verbose_name="دانش‌آموز",
    )
    strengths_analysis = CKEditor5Field(verbose_name="نقاط قوت و دروس با تراز مطلوب")
    weaknesses_analysis = CKEditor5Field(verbose_name="علت‌یابی افت و تله‌های آموزشی")
    action_plan_for_next_exam = CKEditor5Field(verbose_name="نسخه عملیاتی برای آزمون بعدی")
    voice_or_file_attachment = models.FileField(
        upload_to=UploadPath("progress/prescriptions/"),
        null=True,
        blank=True,
        verbose_name="فایل صوتی یا PDF تحلیل مشاور",
    )
    is_seen_by_student = models.BooleanField(
        default=False,
        verbose_name="مشاهده‌شده توسط دانش‌آموز",
    )
    student_reflection = models.TextField(
        blank=True,
        null=True,
        verbose_name="پاسخ و تعهد دانش‌آموز پس از مطالعه تحلیل",
    )

    def __str__(self):
        return f"نسخه مشاور - {self.exam_report}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نسخه مشاور روی کارنامه'
        verbose_name_plural = 'نسخه‌های مشاور روی کارنامه‌ها'


class CounselingSession(BaseModel):
    class SessionType(models.TextChoices):
        ONLINE_MEET = "online_meet", "تصویری آنلاین"
        PHONE = "phone", "تلفنی"
        IN_PERSON = "in_person", "حضوری"

    class Status(models.TextChoices):
        REQUESTED_BY_STUDENT = "requested", "درخواست توسط دانش‌آموز"
        SCHEDULED = "scheduled", "تنظیم و تایید شده"
        COMPLETED = "completed", "برگزار شده"
        CANCELLED = "cancelled", "لغو شده"

    adviser = models.ForeignKey(
        "advisers.Adviser",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="مشاور",
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="counseling_sessions",
        verbose_name="دانش‌آموز",
    )
    title = models.CharField(max_length=255, verbose_name="موضوع جلسه")
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.ONLINE_MEET,
        verbose_name="نوع جلسه",
    )
    scheduled_at = BaseJalaliDateTimeField(verbose_name="زمان برگزاری جلسه")
    duration_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="مدت جلسه (دقیقه)",
    )
    meeting_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="لینک ورود به جلسه",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED_BY_STUDENT,
        verbose_name="وضعیت",
    )
    student_request_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="علت درخواست / سوالات دانش‌آموز قبل از جلسه",
    )
    session_summary = CKEditor5Field(
        blank=True,
        null=True,
        verbose_name="صورت‌جلسه و مصوبات جلسه (قابل مشاهده برای دانش‌آموز)",
    )
    private_adviser_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت محرمانه مشاور (غیرقابل مشاهده برای دانش‌آموز)",
    )

    def __str__(self):
        return f"{self.title} - {self.student} ({self.get_status_display()})"

    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'جلسه مشاوره'
        verbose_name_plural = 'جلسات مشاوره'
