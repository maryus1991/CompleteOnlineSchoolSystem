from django.db import models
from apps.users.accounts.models import User
from apps.common.models import BaseModel
from apps.schools.models import School


class Adviser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")

    province = models.CharField(null=True, blank=True, max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True, max_length=255, verbose_name='شهر')

    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL, related_name="advisers", verbose_name="مدرسه", )

    specialization = models.CharField(max_length=255, null=True, blank=True, verbose_name="تخصص مشاوره‌ای" )
    max_students_capacity = models.PositiveIntegerField( default=50, verbose_name="حداکثر ظرفیت دانش‌آموز" )

    can_manage_study_plans = models.BooleanField("اجازه تعریف و ویرایش برنامه مطالعاتی", default=True )
    can_view_student_reports = models.BooleanField("اجازه مشاهده و تحلیل کارنامه دانش‌آموزان", default=True )
    can_manage_sessions = models.BooleanField("اجازه مدیریت جلسات مشاوره", default=True )
    can_start_live_session = models.BooleanField("اجازه شروع جلسه آنلاین مشاوره", default=True )
    can_answer_counseling_requests = models.BooleanField("اجازه پاسخ به درخواست‌های مشاوره سایت", default=False )
    can_send_adviser_notes = models.BooleanField("اجازه ثبت نسخه و بازخورد مشاوره‌ای", default=True )
    can_change_account = models.BooleanField("اجازه ویرایش اطلاعات حساب", default=True )

    def active_students_count(self) -> int:
        return self.students.filter(is_active=True).count()

    def remaining_capacity(self) -> int:
        return max(0, self.max_students_capacity - self.active_students_count())

    def __str__(self):
        return self.user.get_full_name() or str(self.user)

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل مشاور'
        verbose_name_plural = 'پروفایل‌های مشاوران'
