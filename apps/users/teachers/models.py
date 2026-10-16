from django.db import models
from apps.users.accounts.models import User
from apps.schools.models import School
from apps.common.models import BaseModel


class Teacher( BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")

    province = models.CharField(null=True, blank=True , max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True ,  max_length=255, verbose_name='شهر')
    school =  models.ForeignKey(School, verbose_name='مدرسه', null=True, blank=True, on_delete=models.CASCADE)

    can_add_exam = models.BooleanField("اجاره افزودن ازمون", default=True)
    can_add_practice = models.BooleanField("اجازه افزودن تمرین", default=True)
    can_add_qbank = models.BooleanField("اجازه افزودن سوال به بانک سوال", default=False)
    can_add_class_section = models.BooleanField("اجازه افزودن جلسه برای کلاس", default=True)
    can_add_class_article = models.BooleanField("اجازه افزودن مقاله کلاسی", default=True)
    can_add_class_file = models.BooleanField("اجازه افزودن فایل کلاسی", default=True)
    can_start_live_class = models.BooleanField("اجازه شروع جلسه انلاین", default=True)
    can_issuing_report = models.BooleanField("اجازه صدور کارنامه", default=True)
    can_site_article = models.BooleanField("اجازه افزودن مقاله برای سایت", default=False)


    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل معلم'
        verbose_name_plural = 'پروفایل های معلمان'


