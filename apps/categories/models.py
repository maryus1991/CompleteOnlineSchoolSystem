from django.db import models

class GradeCategories(models.Model):
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    name = models.CharField(max_length=255, verbose_name='نام پایه')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'پایه'
        verbose_name_plural = 'پایه ها'

class MajorCategories(models.Model):
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    name = models.CharField(max_length=255, verbose_name='نام رشته')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'رشته '
        verbose_name_plural = 'رشته ها'

class ProvinceCategories(models.Model):
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    name = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'استان'
        verbose_name_plural = 'استان ها'

class CityCategories(models.Model):
    province = models.ForeignKey(ProvinceCategories, null=True, blank=True, verbose_name="استان", related_name='cities', on_delete=models.PROTECT)
    sort_number = models.PositiveIntegerField(default=1, verbose_name='ترتیب')
    name = models.CharField(max_length=255, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number']
        verbose_name = 'شهر'
        verbose_name_plural = 'شهر ها'
