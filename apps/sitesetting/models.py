from django.db import models
from apps.common.models import BaseModel

class Site(BaseModel):
    name = models.CharField("نام سایت", max_length=100, default='بنیاد اموزشی فراسو')

    list_articles_above_tag = models.CharField("تگ لیست مقالات", max_length=100, default=" مقالات آموزشی ")
    list_articles_title = models.CharField("عنوان لیست مقالات", max_length=100, default=" مقالات امورشی فراسو")
    list_articles_description = models.CharField("توضیحات لیست مقالات", max_length=500, default="اگاهی و دانایی بیشتر با مطالعه بیشتر")

    list_course_above_tag = models.CharField("تگ لیست دوره ها", max_length=100, default=" دوره‌های تخصصی ")
    list_course_title = models.CharField("عنوان لیست دوره ها", max_length=100, default=" دورهای امورشی فراسو")
    list_course_description = models.CharField("توضیحات لیست دوره ها", max_length=500, default="دوره‌هایی که آینده شما را می‌سازند")
    count_of_courses_in_course_detail_page = models.IntegerField("تعداد نمایشی دوره ها در صفحه جزییات ", default=6)

    list_users_above_tag = models.CharField("تگ لیست کاربران", max_length=100, default="اعضایی گرامی")
    list_users_title = models.CharField("عنوان لیست کاربران", max_length=100, default=" اعضای سایت امورشی فراسو")
    list_users_description = models.CharField("توضیحات لیست کاربران", max_length=500, default="افرادی که اینده را میسازند")

    list_exam_above_tag = models.CharField("تگ لیست ازمون ها", max_length=100, default="سنجش و یادگیری")
    list_exam_title = models.CharField("عنوان لیست ازمون ها", max_length=100, default=" ازمون های امورشی فراسو")
    list_exam_description = models.CharField("توضیحات لیست ازمون ها", max_length=500, default="داشن خود را به چالش بکشید")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'
