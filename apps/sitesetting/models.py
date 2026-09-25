from django.db import models
from apps.common.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField

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

    contact_above_tag = models.CharField("تگ تماس با ما", max_length=100, default=" ارتباط با ما")
    contact_title = models.CharField("عنوان تماس با ما", max_length=100, default="پیام خود را ارسال کنید")
    contact_description = models.CharField("توضیحات تماس با ما", max_length=500, default="ما در سریعترین زمان به پیام شما پاسخ خواهیم داد")
    phone_number_contact = PhoneNumberField("شماره تماس صفحه تماس با ما", default="09373061991")
    email_contact = models.EmailField("ایمیل صفحه تماس با ما", default="maryus19915123@gmail.com")
    active_contact = models.BooleanField("فعال صفحه تماس با ما", default=True)

    free_counseling_above_tag = models.CharField("تگ مشاوره رایگان", max_length=100, default=" ارتباط با ما")
    free_counseling_title = models.CharField("عنوان مشاوره رایگان", max_length=100, default="پیام خود را ارسال کنید")
    free_counseling_description = models.CharField("توضیحات مشاوره رایگان", max_length=500, default="ما در سریعترین زمان به پیام شما پاسخ خواهیم داد")
    phone_number_counseling = PhoneNumberField("شماره تماس صفحه صفحه مشاوره رایگان", default="09373061991")
    email_counseling = models.EmailField("ایمیل صفحه صفحه مشاوره رایگان", default="maryus19915123@gmail.com")
    active_counseling = models.BooleanField("فعال صفحه مشاوره رایگان", default=True)


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'


class Contact(BaseModel):
    full_name = models.CharField("نام", max_length=250)
    read = models.BooleanField("خوانده شده", default=False)
    phone_number = PhoneNumberField("شماره تماس ",)
    message = models.TextField("پیام")


    def __str__(self):
        return str(self.full_name) + " " + str(self.phone_number) + " " +str(self.read)

    class Meta:
        ordering = ['pk']
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام ها'


