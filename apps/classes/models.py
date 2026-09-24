from django.db import models
from apps.schools.models import School
from apps.users.students.models import Student
from apps.users.teachers.models import Teacher
from apps.categories.models import GradeCategories, MajorCategories, LessonCategories
from apps.common.models import BaseModel
from apps.common.file_storage_script_for_model import UploadPath
from django_resized import ResizedImageField
from django.urls import reverse_lazy

class Class(BaseModel):
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE, related_name='classes', verbose_name="مدرسه")
    student = models.ManyToManyField(Student, related_name='classes', verbose_name="دانش اموزان", null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='classes', verbose_name="معلم")
    grade = models.ForeignKey(GradeCategories,   null=True, blank=True, on_delete=models.CASCADE, related_name='classes', verbose_name="پایه")
    major = models.ForeignKey(MajorCategories,   null=True, blank=True, on_delete=models.CASCADE, related_name='classes', verbose_name="رشته")
    lesson = models.ForeignKey(LessonCategories, null=True, blank=True, on_delete=models.CASCADE, related_name='classes', verbose_name="درس")
    name = models.CharField("نام", max_length=100)
    summery = models.CharField("توضیحات کوتاه", max_length=500, null=True, blank=True)
    is_public = models.BooleanField("عمومی", default=False)
    is_free = models.BooleanField("رایگان", default=False)
    image = ResizedImageField("عکس", upload_to=UploadPath("classes/"))
    price = models.BigIntegerField("قیمت", default=0)
    first_tag = models.CharField("تگ اول", max_length=50, null=True, blank=True, default="پشتیبانی ۲۴/۷")
    second_tag = models.CharField("تگ دوم", max_length=50, null=True, blank=True, default="گواهی معتبر")
    third_tag = models.CharField("تگ سوم", max_length=50, null=True, blank=True, default="پروژه محور")

    def get_absolute_url(self):
        return reverse_lazy("class:details", kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def get_price(self):
        return f"{self.price:,}"

    class Meta:
        ordering = ['-pk']
        verbose_name = 'کلاس'
        verbose_name_plural = 'کلاس ها'