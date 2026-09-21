from django.db import models


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="فعال / غیر فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ اخرین بروزرسانی")
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')

    class Meta:
        abstract = True
