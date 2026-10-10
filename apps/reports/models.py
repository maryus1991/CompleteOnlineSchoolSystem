from django.db import models
from django.db.models import Q

from apps.common.models import BaseModel
from apps.common.models_fields import BaseJalaliDateTimeField
from apps.exams.models import Exam
from apps.users.students.models import Student


class ExamReport(BaseModel):

    class ReportStatus(models.TextChoices):
        PENDING = "pending", "در انتظار محاسبه"
        CALCULATED = "calculated", "محاسبه شده"
        PUBLISHED = "published", "منتشر شده"

    exam = models.ForeignKey(
        Exam,
        on_delete=models.PROTECT,
        related_name="reports",
        verbose_name="آزمون",
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="exam_reports",
        verbose_name="دانش‌آموز",
    )

    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
        verbose_name="وضعیت کارنامه",
    )

    total_questions = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد کل سوالات",
    )

    correct_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد پاسخ‌های صحیح",
    )

    wrong_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد پاسخ‌های غلط",
    )

    unanswered_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد سوالات بی‌پاسخ",
    )

    skipped_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد سوالات ردشده",
    )

    uncorrected_count = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد پاسخ‌های تصحیح‌نشده",
    )


    score = models.FloatField(
        default=0,
        verbose_name="نمره کسب‌شده",
    )

    max_score = models.FloatField(
        default=0,
        verbose_name="حداکثر نمره",
    )

    percentage = models.FloatField(
        default=0,
        verbose_name="درصد نهایی",
    )

    answered_percentage = models.FloatField(
        default=0,
        verbose_name="درصد پاسخ‌گویی",
    )

    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="رتبه در آزمون",
    )

    teraze = models.FloatField(
        null=True,
        blank=True,
        verbose_name="تراز",
    )

    calculated_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان محاسبه کارنامه",
    )

    published_at = BaseJalaliDateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان انتشار کارنامه",
    )

    class Meta:
        verbose_name = "کارنامه آزمون"
        verbose_name_plural = "کارنامه‌های آزمون"

        constraints = [
            models.UniqueConstraint(
                fields=["exam", "student"],
                name="unique_exam_report_student",
            ),
            models.CheckConstraint(
                condition=Q(percentage__gte=0) & Q(percentage__lte=100),
                name="exam_report_percentage_range",
            ),
            models.CheckConstraint(
                condition=Q(
                    answered_percentage__gte=0,
                    answered_percentage__lte=100,
                ),
                name="exam_report_answered_percentage_range",
            ),
        ]

        indexes = [
            models.Index(
                fields=["exam", "status", "rank"],
                name="report_exam_status_rank_idx",
            ),
            models.Index(
                fields=["student", "-created_at"],
                name="report_student_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.exam.name} - {self.student} - {self.score}"
