from django.db import models
from apps.common.models import BaseModel

class Site(BaseModel):
    name = models.CharField("نام سایت", max_length=100, default='بنیاد اموزشی فراسو')

    list_articles_above_tag = models.CharField("تگ لیست مقالات", max_length=100, default=" مقالات آموزشی ")
    list_articles_title = models.CharField("عنوان لیست مقالات", max_length=100, default=" مقالات آموزشی امورشی فراسو")
    list_articles_description = models.CharField("توضیحات لیست مقالات", max_length=500, default="اگاهی و دانایی بیشتر با مطالعه بیشتر")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'
