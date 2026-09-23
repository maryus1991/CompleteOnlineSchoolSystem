from django.db import models
from django_jalali.db import models as jalali_models
from .models_fields import BaseJalaliDateTimeField

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="فعال / غیر فعال")
    created_at = BaseJalaliDateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    updated_at = BaseJalaliDateTimeField(auto_now=True, verbose_name="تاریخ اخرین بروزرسانی")
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    jalali_object = jalali_models.jManager()
    objects = models.Manager()

    class Meta:
        abstract = True
