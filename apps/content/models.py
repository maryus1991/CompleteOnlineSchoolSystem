from django.db import models
from apps.classes.models import Class
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.models import BaseModel

class Section(BaseModel):
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections', verbose_name="کلاس")
    is_publish = models.BooleanField("انتشار", default=False)

    class Meta:
        ordering = ["-sort_number", 'pk']
        verbose_name = 'جلسه'
        verbose_name_plural = 'جلسه ها'


class ClassArticle(BaseModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='article', verbose_name="مقاله")
    content = CKEditor5Field("توضیحات")

    class Meta:
        ordering = ["-sort_number", 'pk']
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'


class ClassFile(BaseModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='file', verbose_name="فایل")
    file = models.FileField("فایل")
    content = CKEditor5Field("توضیحات")

    class Meta:
        ordering = ["-sort_number", 'pk']
        verbose_name = 'فایل کلاس'
        verbose_name_plural = 'فایل های کلاس'

class ClassPractice(BaseModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='practice', verbose_name="تمرین")
    content = CKEditor5Field("توضیحات")

    class Meta:
        ordering = ["-sort_number", 'pk']
        verbose_name = 'تمرین'
        verbose_name_plural = 'تمرینات'

