from django.db import models
from apps.users.managers.models import Manager as UserManager
from apps.common.models import BaseModel


class School(BaseModel):
    user_manager = models.ForeignKey(UserManager, on_delete=models.CASCADE, related_name='schools', verbose_name="مدیر مدرسه")
    name = models.CharField("نام", max_length=100)

    province = models.CharField(null=True, blank=True , max_length=255, verbose_name='استان')
    city = models.CharField(null=True, blank=True ,  max_length=255, verbose_name='شهر')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'مدرسه'
        verbose_name_plural = 'مدارس'