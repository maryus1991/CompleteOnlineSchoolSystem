from django.db import models
from apps.common.models import BaseModel

class GradeCategories(BaseModel):
    name = models.CharField(max_length=255, verbose_name='نام پایه')


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'پایه'
        verbose_name_plural = 'پایه ها'

class MajorCategories(BaseModel):

    name = models.CharField(max_length=255, verbose_name='نام رشته')


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'رشته '
        verbose_name_plural = 'رشته ها'

class LessonCategories(BaseModel):

    name = models.CharField(max_length=255, verbose_name='نام درس')


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'درس '
        verbose_name_plural = 'دروس'

class ProvinceCategories(BaseModel):
    name = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'استان'
        verbose_name_plural = 'استان ها'

class CityCategories(BaseModel):
    province = models.ForeignKey(ProvinceCategories, null=True, blank=True, verbose_name="استان", related_name='cities', on_delete=models.PROTECT)

    name = models.CharField(max_length=255, verbose_name='نام')


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'شهر'
        verbose_name_plural = 'شهر ها'

class BlogCategories(BaseModel):
    name = models.CharField(max_length=255, verbose_name='نام')
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'دسته بندی مقاله'
        verbose_name_plural = 'دسته بندی های مقالات'
