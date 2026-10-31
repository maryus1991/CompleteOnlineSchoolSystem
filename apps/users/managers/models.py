from django.db import models
from apps.users.accounts.models import User
from apps.common.models import BaseModel


class Manager(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="manager_profile", verbose_name="حساب")
    province = models.CharField(null=True, blank=True, max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True, max_length=255, verbose_name='شهر')

    # مجوزهای مدیریتی مدیر مدرسه
    can_manage_users = models.BooleanField("اجازه مدیریت کاربران مدرسه", default=True)
    can_change_teacher_permissions = models.BooleanField("اجازه تغییر مجوزهای معلمان مدرسه", default=True)
    can_change_adviser_permissions = models.BooleanField("اجازه تغییر مجوزهای مشاوران مدرسه", default=True)
    can_manage_classes = models.BooleanField("اجازه مدیریت کلاس‌ها و جلسات", default=True)
    can_manage_exams = models.BooleanField("اجازه مدیریت آزمون‌ها و تمرین‌ها", default=True)
    can_manage_live_classes = models.BooleanField("اجازه مدیریت کلاس‌ها و جلسات آنلاین", default=True)
    can_manage_tickets = models.BooleanField("اجازه مدیریت و ارجاع تیکت‌ها", default=True)
    can_view_reports = models.BooleanField("اجازه مشاهده گزارش‌های پیشرفته و صدور کارنامه", default=True)
    can_manage_school_settings = models.BooleanField("اجازه ویرایش تنظیمات و اعلان‌های مدرسه", default=True)
    can_manage_articles = models.BooleanField("اجازه مدیریت پست‌ها و مقالات", default=True)
    can_change_account = models.BooleanField("اجازه ویرایش اطلاعات حساب", default=True)

    def __str__(self):
        return self.user.get_full_name() or str(self.user)

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل مدیر'
        verbose_name_plural = 'پروفایل های مدیران'
