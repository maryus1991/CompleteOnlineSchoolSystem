from django.db import models
from apps.users.managers.models import Manager as UserManager
from apps.common.models import BaseModel
from apps.common.file_storage_script_for_model import UploadPath


class School(BaseModel):
    user_manager = models.ForeignKey(
        UserManager,
        on_delete=models.CASCADE,
        related_name='schools',
        verbose_name="مدیر مدرسه",
    )
    name = models.CharField("نام", max_length=100)
    province = models.CharField(null=True, blank=True, max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True, max_length=255, verbose_name='شهر')
    is_active = models.BooleanField(default=True)

    # تنظیمات اختصاصی سایت و هویت بصری مدرسه
    logo = models.ImageField(
        "لوگوی مدرسه",
        upload_to=UploadPath("schools/logos/"),
        null=True,
        blank=True,
    )
    primary_color = models.CharField(
        "رنگ اصلی مدرسه",
        max_length=32,
        default="#4facfe",
        blank=True,
    )
    secondary_color = models.CharField(
        "رنگ دوم مدرسه",
        max_length=32,
        default="#00f2fe",
        blank=True,
    )
    welcome_message = models.CharField(
        "پیام خوش‌آمدگویی مدرسه",
        max_length=500,
        null=True,
        blank=True,
    )
    description = models.TextField(
        "معرفی و توضیحات مدرسه",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        "تلفن تماس مدرسه",
        max_length=50,
        null=True,
        blank=True,
    )
    address = models.CharField(
        "آدرس مدرسه",
        max_length=500,
        null=True,
        blank=True,
    )

    # Feature Toggles مدرسه
    enable_live_classes = models.BooleanField("فعال بودن کلاس‌های آنلاین مدرسه", default=True)
    enable_exams = models.BooleanField("فعال بودن آزمون‌های آنلاین مدرسه", default=True)
    enable_advising = models.BooleanField("فعال بودن بخش مشاوره تحصیلی", default=True)
    enable_tickets = models.BooleanField("فعال بودن سیستم تیکت و پشتیبانی", default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'مدرسه'
        verbose_name_plural = 'مدارس'


class SchoolAnnouncement(BaseModel):
    class TargetAudience(models.TextChoices):
        ALL = "all", "همه اعضای مدرسه"
        STUDENTS = "students", "فقط دانش‌آموزان"
        TEACHERS = "teachers", "فقط معلمان"
        ADVISERS = "advisers", "فقط مشاوران"

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name="مدرسه",
        db_index=True,
    )
    title = models.CharField("عنوان اعلان / خبر", max_length=255)
    content = models.TextField("متن کامل اعلان")
    target_audience = models.CharField(
        "مخاطب هدف",
        max_length=30,
        choices=TargetAudience.choices,
        default=TargetAudience.ALL,
    )
    is_important = models.BooleanField("اعلان مهم و فوری", default=False)

    def __str__(self):
        return f"{self.title} ({self.school.name})"

    class Meta:
        ordering = ["-is_important", "-pk"]
        verbose_name = "اعلان مدرسه"
        verbose_name_plural = "اعلان‌های مدرسه"
