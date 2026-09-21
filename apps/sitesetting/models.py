from django.db import models
from apps.common.models import BaseModel

class Site(BaseModel):


    class Meta:
        ordering = ['pk']
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'
