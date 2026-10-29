import secrets
import string
from apps.common.models_fields import BaseJalaliDateTimeField
from apps.content.models import Section
from apps.users.teachers.models import Teacher
from apps.users.advisers.models import Adviser
from apps.users.students.models import Student
from apps.progress.models import CounselingSession
from apps.common.models import BaseModel
from apps.classes.models import Class
from apps.common.file_storage_script_for_model import UploadPath
from urllib.parse import urlsplit, urlunsplit, urlencode, urljoin
from django.db import models
from django.core.exceptions import ValidationError


def generate_session_code():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(72))


class StreamServers(BaseModel):
    name = models.CharField(verbose_name='عنوان', max_length=255)
    base_url = models.URLField("لینک")
    server_stats_check = models.CharField(verbose_name='مسیر چک کردن منابع', max_length=255, default='/monitor/stats')
    teacher_url_name = models.CharField(verbose_name='مسیر لینک برای استاد', max_length=255, default='/teacher.html')
    TEACHER_KEY = models.CharField(verbose_name='کلید ورود استاد', max_length=255)
    student_url_name = models.CharField(verbose_name='مسیر لینک برای دانش اموز', max_length=255, default='/student.html')
    MONITOR_TOKEN = models.CharField(verbose_name='توکن مانیتور کردن سرور', max_length=255)

    @property
    def monitor_url(self):
        return urljoin(f'{self.base_url.rstrip("/")}/', self.server_stats_check.lstrip('/') ) + f'?token={self.MONITOR_TOKEN}'

    def build_meeting_url(self, page, **params):
        base_url = urljoin(
            f"{self.base_url.rstrip('/')}/",
            page.lstrip("/"),
        )
        parts = urlsplit(base_url)

        return urlunsplit((
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(params),
            parts.fragment,
        ))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'سرور کلاس انلاین'
        verbose_name_plural = 'سرور های کلاس های انلاین'


class LiveClass(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "برنامه‌ریزی‌شده"
        LIVE = "live", "در حال برگزاری"
        COMPLETED = "completed", "برگزارشده"
        CANCELLED = "cancelled", "لغوشده"

    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="live", verbose_name="کلاس" )
    server = models.ForeignKey(StreamServers, on_delete=models.CASCADE, related_name="live", verbose_name="سرور" )
    status = models.CharField("وضعیت", max_length=20, choices=Status.choices, default=Status.SCHEDULED, db_index=True, )
    session_code = models.CharField("کد اختصاصی کلاس", max_length=72, unique=True, default=generate_session_code, editable=False, )

    class Meta:
        ordering = ["pk"]
        verbose_name = "کلاس آنلاین"
        verbose_name_plural = "کلاس‌های آنلاین"

    def __str__(self):
        return f"{self.klass.name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_code = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list("session_code", flat=True)
                .first()
            )
            if old_code and self.session_code != old_code:
                raise ValidationError("کد اختصاصی کلاس قابل تغییر نیست.")

        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return (
            self.status == self.Status.LIVE
            and bool(self.session_code)
            and bool(self.server_id)
        )

    def get_student_meeting_url(self, student):
        if not self.is_available:
            return None

        return self.server.build_meeting_url(
            self.server.student_url_name,
            room=self.session_code,
            name=student.get_full_name(),
        )

    @property
    def teacher_meeting_url(self):
        if not self.is_available:
            return None

        teacher = self.klass.teacher

        return self.server.build_meeting_url(
            self.server.teacher_url_name,
            room=self.session_code,
            name=teacher.user.get_full_name(),
            title=self.klass.name,
            key=self.server.TEACHER_KEY,
        )


class LiveClassReport(BaseModel):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name="report", verbose_name="کلاس آنلاین", )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="report", verbose_name="جلسه", )
    started_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان شروع واقعی")
    ended_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان پایان واقعی")
    duration_minutes = models.PositiveIntegerField("مدت واقعی (دقیقه)", null=True, blank=True)
    attendees_count = models.PositiveIntegerField("تعداد حاضرین", default=0)
    teacher_note = models.TextField("یادداشت معلم", blank=True)
    admin_note = models.TextField("یادداشت ادمین", blank=True)
    recording_file = models.FileField("فایل ضبط‌شده کلاس", upload_to=UploadPath("live_classes/recordings/"), blank=True, null=True, )
    chat_report = models.FileField("گزارش چت (PDF)", upload_to=UploadPath("live_classes/chat_reports/"), blank=True, null=True, )
    attendance_report = models.FileField("گزارش حضور کاربران (PDF)", upload_to=UploadPath("live_classes/attendance_reports/"), blank=True, null=True, )

    class Meta:
        ordering = ["-pk"]
        verbose_name = "گزارش برگزاری کلاس آنلاین"
        verbose_name_plural = "گزارش‌های برگزاری کلاس آنلاین"

    def __str__(self):
        return f"گزارش {self.live_class}"


class LiveClassRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"
        CANCELLED = "cancelled", "لغو شده"

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="live_class_requests", verbose_name="معلم", db_index=True)
    title = models.CharField("عنوان درخواست", max_length=255)
    description = models.TextField("توضیحات", blank=True)
    preferred_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان پیشنهادی برگزاری", )
    duration_minutes = models.PositiveIntegerField("مدت پیشنهادی (دقیقه)", default=60, )
    status = models.CharField("وضعیت", max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True, )
    admin_note = models.TextField("یادداشت ادمین", blank=True, )

    class Meta:
        ordering = ["-pk"]
        verbose_name = "درخواست کلاس آنلاین"
        verbose_name_plural = "درخواست‌های کلاس آنلاین"
        indexes = [
            models.Index(fields=["teacher", "is_active"]),
            models.Index(fields=["status", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.teacher} - {self.get_status_display()}"


class AdviserLiveSession(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "برنامه‌ریزی‌شده"
        LIVE = "live", "در حال برگزاری"
        COMPLETED = "completed", "برگزارشده"
        CANCELLED = "cancelled", "لغوشده"

    adviser = models.ForeignKey(
        Adviser,
        on_delete=models.CASCADE,
        related_name="live_sessions",
        verbose_name="مشاور",
        db_index=True,
    )
    students = models.ManyToManyField(
        Student,
        related_name="adviser_live_sessions",
        verbose_name="دانش‌آموزان جلسه",
        blank=True,
    )
    counseling_session = models.ForeignKey(
        CounselingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="live_sessions",
        verbose_name="جلسه مشاوره مرتبط",
    )
    title = models.CharField("عنوان جلسه آنلاین مشاوره", max_length=255)
    server = models.ForeignKey(
        StreamServers,
        on_delete=models.CASCADE,
        related_name="adviser_live_sessions",
        verbose_name="سرور",
    )
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )
    session_code = models.CharField(
        "کد اختصاصی جلسه مشاوره",
        max_length=72,
        unique=True,
        default=generate_session_code,
        editable=False,
    )
    scheduled_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان برنامه‌ریزی‌شده",
    )

    class Meta:
        ordering = ["-pk"]
        verbose_name = "جلسه آنلاین مشاوره"
        verbose_name_plural = "جلسات آنلاین مشاوره"
        indexes = [
            models.Index(fields=["adviser", "is_active"]),
            models.Index(fields=["status", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.adviser} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if (
            self.counseling_session_id
            and self.adviser_id
            and self.counseling_session.adviser_id != self.adviser_id
        ):
            raise ValidationError("جلسه مشاوره انتخاب‌شده متعلق به این مشاور نیست.")

    def save(self, *args, **kwargs):
        if self.pk:
            old_code = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list("session_code", flat=True)
                .first()
            )
            if old_code and self.session_code != old_code:
                raise ValidationError("کد اختصاصی جلسه مشاوره قابل تغییر نیست.")

        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return (
            self.status == self.Status.LIVE
            and bool(self.session_code)
            and bool(self.server_id)
        )

    def get_student_meeting_url(self, student):
        if not self.is_available:
            return None

        if hasattr(student, "get_full_name"):
            student_name = student.get_full_name()
        elif hasattr(student, "user") and hasattr(student.user, "get_full_name"):
            student_name = student.user.get_full_name()
        else:
            student_name = str(student)

        return self.server.build_meeting_url(
            self.server.student_url_name,
            room=self.session_code,
            name=student_name,
        )

    @property
    def adviser_meeting_url(self):
        if not self.is_available:
            return None

        adviser_name = self.adviser.user.get_full_name() or str(self.adviser.user)

        return self.server.build_meeting_url(
            self.server.teacher_url_name,
            room=self.session_code,
            name=adviser_name,
            title=self.title,
            key=self.server.TEACHER_KEY,
        )


class AdviserLiveSessionReport(BaseModel):
    live_session = models.ForeignKey(
        AdviserLiveSession,
        on_delete=models.CASCADE,
        related_name="report",
        verbose_name="جلسه آنلاین مشاوره",
    )
    counseling_session = models.ForeignKey(
        CounselingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="live_report",
        verbose_name="جلسه مشاوره مرتبط",
    )
    started_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان شروع واقعی")
    ended_at = BaseJalaliDateTimeField(null=True, blank=True, verbose_name="زمان پایان واقعی")
    duration_minutes = models.PositiveIntegerField("مدت واقعی (دقیقه)", null=True, blank=True)
    attendees_count = models.PositiveIntegerField("تعداد حاضرین", default=0)
    adviser_note = models.TextField("یادداشت و خلاصه مشاور", blank=True)
    admin_note = models.TextField("یادداشت ادمین", blank=True)
    recording_file = models.FileField(
        "فایل ضبط‌شده جلسه",
        upload_to=UploadPath("live_classes/adviser_recordings/"),
        blank=True,
        null=True,
    )
    chat_report = models.FileField(
        "گزارش چت (PDF)",
        upload_to=UploadPath("live_classes/adviser_chat_reports/"),
        blank=True,
        null=True,
    )
    attendance_report = models.FileField(
        "گزارش حضور کاربران (PDF)",
        upload_to=UploadPath("live_classes/adviser_attendance_reports/"),
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-pk"]
        verbose_name = "گزارش برگزاری جلسه آنلاین مشاوره"
        verbose_name_plural = "گزارش‌های برگزاری جلسات آنلاین مشاوره"

    def __str__(self):
        return f"گزارش {self.live_session}"

    def clean(self):
        super().clean()
        if (
            self.counseling_session_id
            and self.live_session_id
            and self.counseling_session.adviser_id != self.live_session.adviser_id
        ):
            raise ValidationError("جلسه مشاوره انتخاب‌شده با مشاور این جلسه آنلاین مطابقت ندارد.")


class AdviserLiveSessionRequest(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"
        CANCELLED = "cancelled", "لغو شده"

    adviser = models.ForeignKey(
        Adviser,
        on_delete=models.CASCADE,
        related_name="live_session_requests",
        verbose_name="مشاور",
        db_index=True,
    )
    students = models.ManyToManyField(
        Student,
        related_name="adviser_live_requests",
        verbose_name="دانش‌آموزان جلسه",
        blank=True,
    )
    counseling_session = models.ForeignKey(
        CounselingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="live_requests",
        verbose_name="جلسه مشاوره مرتبط",
    )
    title = models.CharField("عنوان درخواست جلسه آنلاین", max_length=255)
    description = models.TextField("توضیحات", blank=True)
    preferred_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان پیشنهادی برگزاری",
    )
    duration_minutes = models.PositiveIntegerField(
        "مدت پیشنهادی (دقیقه)",
        default=45,
    )
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    admin_note = models.TextField("یادداشت ادمین", blank=True)

    class Meta:
        ordering = ["-pk"]
        verbose_name = "درخواست جلسه آنلاین مشاوره"
        verbose_name_plural = "درخواست‌های جلسه آنلاین مشاوره"
        indexes = [
            models.Index(fields=["adviser", "is_active"]),
            models.Index(fields=["status", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.adviser} - {self.get_status_display()}"
