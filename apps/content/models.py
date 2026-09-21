from django.db import models
from apps.classes.models import Class
from django_ckeditor_5.fields import CKEditor5Field


class ClassArticle(models.Model):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='article', verbose_name="کلاس")
    content = CKEditor5Field("توضیحات")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'


class ClassFile(models.Model):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='file', verbose_name="کلاس")
    file = models.FileField("فایل")
    content = CKEditor5Field("توضیحات")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'فایل کلاس'
        verbose_name_plural = 'فایل های کلاس'

