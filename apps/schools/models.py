from django.db import models
from apps.categories.models import ProvinceCategories, CityCategories
from apps.users.managers.models import Manager
from apps.common.models import BaseModel


class School(BaseModel):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='schools', verbose_name="مدرسه")
    name = models.CharField("نام", max_length=100)
    province = models.ForeignKey(ProvinceCategories, related_name='schools',blank=True, null=True, on_delete=models.SET_NULL, verbose_name='استان')
    city = models.ForeignKey(CityCategories, related_name='schools', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='شهر')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'مدرسه'
        verbose_name_plural = 'مدارس'