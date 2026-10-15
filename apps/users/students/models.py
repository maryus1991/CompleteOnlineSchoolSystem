from django.db import models
from apps.users.accounts.models import User
from apps.categories.models import GradeCategories, MajorCategories
from phonenumber_field.modelfields import PhoneNumberField
from apps.schools.models import School
from apps.common.models import BaseModel

class Student(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")
    grade = models.ForeignKey(GradeCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='پایه', blank=True)
    major = models.ForeignKey(MajorCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='رشته تحصیلی', blank=True)
    province = models.CharField(null=True, blank=True , max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True ,  max_length=255, verbose_name='شهر')
    parent_phone_number = PhoneNumberField(verbose_name="شماره والدین", null=True, blank=True)
    school =  models.ForeignKey(School, verbose_name='مدرسه', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل دانش اموز'
        verbose_name_plural = 'پروفایل های دانش اموزان'