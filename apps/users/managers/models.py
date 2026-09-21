from django.db import models
from apps.users.accounts.models import User
from apps.categories.models import ProvinceCategories, CityCategories


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")
    province = models.ForeignKey(ProvinceCategories, related_name='manager', null=True, on_delete=models.SET_NULL, verbose_name='استان')
    city = models.ForeignKey(CityCategories, related_name='manager', null=True, on_delete=models.SET_NULL, verbose_name='شهر')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل مدیر'
        verbose_name_plural = 'پروفایل های مدیران'