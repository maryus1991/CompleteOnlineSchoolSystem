from django.db import models
from apps.users.accounts.models import User
from apps.categories.models import GradeCategories, MajorCategories, ProvinceCategories, CityCategories
from phonenumber_field.modelfields import PhoneNumberField


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")
    grade = models.ForeignKey(GradeCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='پایه')
    major = models.ForeignKey(MajorCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='رشته تحصیلی')
    province = models.ForeignKey(ProvinceCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='استان')
    city = models.ForeignKey(CityCategories, related_name='student', null=True, on_delete=models.SET_NULL, verbose_name='شهر')
    parent_phone_number = PhoneNumberField(verbose_name="شماره والدین")
    school =  models.CharField(max_length=255, verbose_name='نام مدرسه', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل دانش اموز'
        verbose_name_plural = 'پروفایل های دانش اموزان'