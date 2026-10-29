from django.core.exceptions import ValidationError
from django.db import models
from apps.users.accounts.models import User
from apps.categories.models import GradeCategories, MajorCategories
from phonenumber_field.modelfields import PhoneNumberField
from apps.schools.models import School
from apps.common.models import BaseModel


class Student(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")
    grade = models.ForeignKey(
        GradeCategories,
        related_name='student',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='پایه',
        blank=True,
    )
    major = models.ForeignKey(
        MajorCategories,
        related_name='student',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='رشته تحصیلی',
        blank=True,
    )
    province = models.CharField(null=True, blank=True, max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True, max_length=255, verbose_name='شهر')
    parent_phone_number = PhoneNumberField(verbose_name="شماره والدین", null=True, blank=True)
    school = models.ForeignKey(
        School,
        verbose_name='مدرسه',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    adviser = models.ForeignKey(
        "advisers.Adviser",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        verbose_name="مشاور تحصیلی",
    )
    target_major_rank = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="هدف تحصیلی / رشته و رتبه هدف",
    )
    counseling_notes_summary = models.TextField(
        null=True,
        blank=True,
        verbose_name="پرونده و شناخت کلی مشاور از دانش‌آموز",
    )

    def clean(self):
        super().clean()
        if self.adviser_id and self.is_active:
            qs = Student.objects.filter(adviser_id=self.adviser_id, is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= self.adviser.max_students_capacity:
                raise ValidationError(
                    {
                        "adviser": (
                            f"ظرفیت دانش‌آموزان این مشاور ({self.adviser.max_students_capacity} نفر) تکمیل شده است."
                        )
                    }
                )

    def __str__(self):
        return self.user.get_full_name() or str(self.user)

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل دانش اموز'
        verbose_name_plural = 'پروفایل های دانش اموزان'
