from django.db import models
from apps.common.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.file_storage_script_for_model import UploadPath
from django_resized import ResizedImageField


class Site(BaseModel):
    name = models.CharField("نام سایت", max_length=100, default='بنیاد اموزشی فراسو')
    description = CKEditor5Field("توضیحات", default="")

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

    free_counseling_above_tag = models.CharField("تگ مشاوره رایگان", max_length=100, default="آماده‌ای که شروع کنیم؟")
    free_counseling_title = models.CharField("عنوان مشاوره رایگان", max_length=100, default=" مشاوره رایگان")
    free_counseling_description = models.CharField("توضیحات مشاوره رایگان", max_length=500, default="برای مشاوره رایگان فرم رو پر کن. کمتر از ۲۴ ساعت تماس می‌گیریم.")
    phone_number_counseling = PhoneNumberField("شماره تماس صفحه صفحه مشاوره رایگان", default="09373061991")
    email_counseling = models.EmailField("ایمیل صفحه صفحه مشاوره رایگان", default="maryus19915123@gmail.com")
    active_counseling = models.BooleanField("فعال صفحه مشاوره رایگان", default=True)

    faq_above_tag = models.CharField("تگ پرسش پاسخ", max_length=100, default="سوالی داری؟ ")
    faq_title = models.CharField("عنوان پرسش پاسخ", max_length=100, default=" سوالات متداول")
    faq_description = models.CharField("توضیحات پرسش پاسخ", max_length=500, default="پاسخ به سوالات متداول")
    faq_active = models.BooleanField("فعال صفحه پرسش پاسخ", default=True)

    about_above_tag = models.CharField("تگ درباره ما", max_length=100, default="با ما اشنا شوید")
    about_title = models.CharField("عنوان درباره ما", max_length=100, default="درباره ما")
    about_active = models.BooleanField("فعال صفحه درباره ما", default=True)

    auth_title = models.CharField("عنوان احراز هویت", max_length=100, default="خوش امدید")
    logo_svg = models.CharField("svg لوگو سایت", max_length=500, default="""
        <svg width="45" height="45" viewBox="0 0 100 100" fill="none">
            <defs><linearGradient id="smallGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#00f2fe"/><stop offset="100%" stop-color="#4facfe"/></linearGradient></defs>
            <circle cx="50" cy="50" r="46" stroke="url(#smallGrad)" stroke-width="4" fill="none"/>
            <circle cx="50" cy="50" r="14" fill="url(#smallGrad)"/>
        </svg>
    """)
    login_active = models.BooleanField("فعال کردن ورود", default=True)
    register_active = models.BooleanField("فعال کردن ثبت نام", default=True)
    forgot_password_active = models.BooleanField("فعال کردن فراموشی رمز", default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pk']
        verbose_name = 'تنظیمات'
        verbose_name_plural = 'تنظیمات'


class TestMonomials(BaseModel):

    name = models.CharField("نام", max_length=255)
    text = models.CharField("توضیحات", max_length=255)
    image = ResizedImageField("عکس", upload_to=UploadPath("test-monomials"))
    behave = models.CharField("سابقه", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-sort_number", '-pk']
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'


class TimeLine(BaseModel):
    svq=models.TextField("svg ایکون", default="""
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
    """)
    name=models.CharField("نام", max_length=255)
    description=models.CharField("توضیحات", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-sort_number", 'pk']
        verbose_name = 'تایم لاین'
        verbose_name_plural = 'تایم لاین ها'

class Contact(BaseModel):
    full_name = models.CharField("نام", max_length=250)
    read = models.BooleanField("خوانده شده", default=False)
    phone_number = PhoneNumberField("شماره تماس ",)
    message = models.TextField("پیام")


    def __str__(self):
        return str(self.full_name) + " " + str(self.phone_number) + " " +str(self.read)

    class Meta:
        ordering = ["-read", 'pk']
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام ها'


class Counseling(BaseModel):
    full_name = models.CharField("نام", max_length=250)
    read = models.BooleanField("خوانده شده", default=False)
    phone_number = PhoneNumberField("شماره تماس ",)
    message = models.TextField("پیام")


    def __str__(self):
        return str(self.full_name) + " " + str(self.phone_number) + " " +str(self.read)

    class Meta:
        ordering = ["-read", 'pk']
        verbose_name = 'درخواست مشاوره'
        verbose_name_plural = 'درخواست های مشاوره'


class FAQ(BaseModel):
    question =  models.CharField("سوال", max_length=500)
    answer = CKEditor5Field("پاسخ")
    class Meta:
        ordering = ["-sort_number", '-pk']
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'

    def __str__(self):
        return self.question
