from django.db import models
from apps.users.accounts.models import User

from apps.common.models import BaseModel


class Manager(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="حساب")
    province = models.CharField(null=True, blank=True , max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True ,  max_length=255, verbose_name='شهر')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        ordering = ['-pk']
        verbose_name = 'پروفایل مدیر'
        verbose_name_plural = 'پروفایل های مدیران'