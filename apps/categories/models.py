from django.db import models
from apps.common.models import BaseModel
from django.urls import reverse_lazy

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

class BlogCategories(BaseModel):
    name = models.CharField(max_length=255, verbose_name='نام')
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'دسته بندی مقاله'
        verbose_name_plural = 'دسته بندی های مقالات'

    def get_absolute_url(self):
        return reverse_lazy("article:article-category-list", kwargs={"pk": self.pk})