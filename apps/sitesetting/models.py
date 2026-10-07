from django.db import models
from apps.common.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.file_storage_script_for_model import UploadPath
from django_resized import ResizedImageField


class Site(BaseModel):
    name = models.CharField("نام سایت", max_length=100, default='بنیاد اموزشی فراسو')
    description = CKEditor5Field("توضیحات", default="")
    short_description = models.CharField("توضیحات کوتاه", default="بنیادی که برای تضمین اینده شما به وجود امده است", max_length=255)

    list_articles_above_tag = models.CharField("تگ لیست مقالات", max_length=100, default=" مقالات آموزشی ")
    list_articles_title = models.CharField("عنوان لیست مقالات", max_length=100, default=" مقالات امورشی فراسو")
    list_articles_description = models.CharField("توضیحات لیست مقالات", max_length=500, default="اگاهی و دانایی بیشتر با مطالعه بیشتر")
    list_articles_active = models.BooleanField("فعال صفحه لیست مقالات", default=True)

    list_course_above_tag = models.CharField("تگ لیست دوره ها", max_length=100, default=" دوره‌های تخصصی ")
    list_course_title = models.CharField("عنوان لیست دوره ها", max_length=100, default=" دورهای امورشی فراسو")
    list_course_description = models.CharField("توضیحات لیست دوره ها", max_length=500, default="دوره‌هایی که آینده شما را می‌سازند")
    list_course_active = models.BooleanField("فعال صفحه لیست دوره ها", default=True)
    count_of_courses_in_course_detail_page = models.IntegerField("تعداد نمایشی دوره ها در صفحه جزییات ", default=6)

    list_users_above_tag = models.CharField("تگ لیست کاربران", max_length=100, default="اعضایی گرامی")
    list_users_title = models.CharField("عنوان لیست کاربران", max_length=100, default=" اعضای سایت امورشی فراسو")
    users_title_url_name = models.CharField("عنوان لیست کاربران", max_length=100, default="برترین ها")
    list_users_description = models.CharField("توضیحات لیست کاربران", max_length=500, default="افرادی که اینده را میسازند")
    list_users_active = models.BooleanField("فعال صفحه لیست کاربران", default=True)

    list_exam_above_tag = models.CharField("تگ لیست ازمون ها", max_length=100, default="سنجش و یادگیری")
    list_exam_title = models.CharField("عنوان لیست ازمون ها", max_length=100, default=" ازمون های امورشی فراسو")
    list_exam_description = models.CharField("توضیحات لیست ازمون ها", max_length=500, default="داشن خود را به چالش بکشید")
    list_exam_active = models.BooleanField("فعال صفحه لیست ازمون ها", default=True)

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

    qbank_above_tag = models.CharField("تگ بانک سوال", max_length=100, default="سوال نیاز داری")
    qbank_title = models.CharField("عنوان بانک سوال", max_length=100, default="بانک سوال")
    qbank_description = models.CharField("توضیحات بانک سوال", max_length=500, default="بانک سوال رایگان فراسو")
    qbank_active = models.BooleanField("فعال صفحه بانک سوال", default=True)

    about_above_tag = models.CharField("تگ درباره ما", max_length=100, default="با ما اشنا شوید")
    about_title = models.CharField("عنوان درباره ما", max_length=100, default="درباره ما")
    about_active = models.BooleanField("فعال صفحه درباره ما", default=True)

    auth_title = models.CharField("عنوان احراز هویت", max_length=100, default="خوش امدید")
    logo_svg = models.TextField("svg لوگو سایت", default="""
        <svg width="45" height="45" viewBox="0 0 100 100" fill="none">
            <defs><linearGradient id="smallGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#00f2fe"/><stop offset="100%" stop-color="#4facfe"/></linearGradient></defs>
            <circle cx="50" cy="50" r="46" stroke="url(#smallGrad)" stroke-width="4" fill="none"/>
            <circle cx="50" cy="50" r="14" fill="url(#smallGrad)"/>
        </svg>
    """)
    login_active = models.BooleanField("فعال کردن ورود", default=True)
    register_active = models.BooleanField("فعال کردن ثبت نام", default=True)
    forgot_password_active = models.BooleanField("فعال کردن فراموشی رمز", default=True)

    footer_fast_link_1_url = models.CharField("لینک شماره ۱ سریع فوتر", default="/", max_length=255)
    footer_fast_link_2_url = models.CharField(" لینک شماره ۲ سریع فوتر", default="/courses/", max_length=255)
    footer_fast_link_3_url = models.CharField(" لینک شماره ۳ سریع فوتر", default="/posts/", max_length=255)
    footer_fast_link_4_url = models.CharField(" لینک شماره ۴ سریع فوتر", default="/exams/", max_length=255)
    footer_fast_link_1_name = models.CharField("نام لینک شماره ۱ سریع فوتر", default="خانه", max_length=50)
    footer_fast_link_2_name = models.CharField("نام لینک شماره ۲ سریع فوتر", default="دورها", max_length=50)
    footer_fast_link_3_name = models.CharField("نام لینک شماره ۳ سریع فوتر", default="مقالات", max_length=50)
    footer_fast_link_4_name = models.CharField("نام لینک شماره ۴ سریع فوتر", default="ازمون ها", max_length=50)

    footer_important_1_url = models.CharField("لینک مهم شماره ۱ فوتر", default="/users/auth/", max_length=255)
    footer_important_2_url = models.CharField(" لینک مهم شماره ۲ فوتر", default="/about/", max_length=255)
    footer_important_3_url = models.CharField(" لینک مهم شماره ۳ فوتر", default="/contact/", max_length=255)
    footer_important_4_url = models.CharField(" لینک مهم شماره ۴ فوتر", default="/free-counseling/", max_length=255)
    footer_important_1_name = models.CharField("نام لینک مهم شماره ۱ فوتر", default="ورود یا ثبت نام", max_length=50)
    footer_important_2_name = models.CharField("نام لینک مهم شماره ۲ فوتر", default="درباره ما", max_length=50)
    footer_important_3_name = models.CharField("نام لینک مهم شماره ۳ فوتر", default="تماس با ما", max_length=50)
    footer_important_4_name = models.CharField("نام لینک مهم شماره ۴ فوتر", default="درخواست مشاوره رایگان", max_length=50)

    copyright = models.CharField("کپی رایت", default="© ۲۰۲۶ آکادمی فراسو برای اینده ای بهتر", max_length=150)
    developer_message = models.CharField("پیام طراح", default="نوشته شده با ❤️ توسط maryus", max_length=50)
    link_url = models.CharField("لینک طراح", default="https://github.com/maryus1991/CompleteOnlineSchoolSystem", max_length=255)

    instagram_link = models.CharField("لینک اینستاگرام", default="#", max_length=255)
    telegram_link = models.CharField("لینک تلرام", default="#", max_length=255)
    other_link = models.CharField("لینک های دیگر", default="#", max_length=255)

    main_page_first_button_url = models.CharField("لینک دکمه شماره یک صفحه اصلی", default="/free-counseling/", max_length=255)
    main_page_first_button_name = models.CharField("نام دکمه شماره یک صفحه اصلی", default="درخواست مشاوره", max_length=50)
    main_page_first_button_svg = models.TextField("svg دکمه شماره یک صفحه اصلی",  default="""
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline>
        </svg>
    """)

    main_page_second_button_url = models.CharField(" لینک دکمه شماره دو صفحه اصلی", default="/qbank/", max_length=255)
    main_page_second_button_name = models.CharField("نام دکمه شماره دو صفحه اصلی", default="بانک سوال", max_length=50)
    main_page_second_button_svg = models.TextField("svg دکمه شماره دو صفحه اصلی",  default="""
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
    """)

    main_page_badge = models.CharField("بگ صفحه اصلی", default="ظرفیت محدود ترم تابستان ۱۴۰۵", max_length=50)
    main_page_greeting = models.CharField("گریتینگ صفحه اصلی", default="وجود شما باعث افتخار ماست", max_length=50)

    about_img = ResizedImageField("عکس صفحه اصلی", upload_to=UploadPath("about-image"), null=True, blank=True)

    main_page_first_stats_number = models.CharField("عدد اول روی تصویر صفحه اصلی ", max_length=50, default="درصد قبولی")
    main_page_first_stats_name = models.CharField("نام اول روی تصویر صفحه اصلی ", default="۸۵٪", max_length=50)
    main_page_first_stats_svg = models.TextField("svg اول روی تصویر صفحه اصلی",  default="""
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
        </svg>
    """)

    main_page_second_stats_number =  models.CharField("عدد دوم روی تصویر صفحه اصلی ", default="۸,۵۰۰+", max_length=50)
    main_page_second_stats_name = models.CharField("نام دوم روی تصویر صفحه اصلی ", default="تعداد انش اموزان", max_length=50)
    main_page_second_stats_svg = models.TextField("svg دوم روی تصویر صفحه اصلی",  default="""
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
    """)

    first_stats_card_svg = models.TextField("svg نماد امار اول",  default="""
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
    """)
    first_stats_card_number =  models.CharField("عدد نماد امار اول", default="8500", max_length=50)
    first_stats_card_symbol =  models.CharField("علامت نماد امار اول", default="+", max_length=50)
    first_stats_card_name = models.CharField("نام نماد امار اول", default="دانش اموزان", max_length=50)


    second_stats_card_svg = models.TextField("svg نماد امار دوم",  default="""
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
        </svg>
    """)
    second_stats_card_number =  models.CharField("عدد نماد امار دوم", default="42", max_length=50)
    second_stats_card_symbol =  models.CharField("علامت نماد امار دوم", default=" ",null=True, blank=True , max_length=50)
    second_stats_card_name = models.CharField("نام نماد امار دوم", default="مدرسه", max_length=50)


    third_stats_card_svg = models.TextField("svg نماد امار سوم",  default="""
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
        </svg>
    """)
    third_stats_card_number =  models.CharField("عدد نماد امار سوم", default="98", max_length=50)
    third_stats_card_symbol =  models.CharField("علامت نماد امار سوم", default="%", max_length=50)
    third_stats_card_name = models.CharField("نام نماد امار سوم", default="رضایت", max_length=50)


    fourth_stats_card_svg = models.TextField("svg نماد امار چهار",  default="""
        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline>
        </svg>
    """)
    fourth_stats_card_number =  models.CharField("عدد نماد امار چهار", default="120", max_length=50)
    fourth_stats_card_symbol =  models.CharField("علامت نماد امار چهار", default="+", max_length=50)
    fourth_stats_card_name = models.CharField("نام نماد امار چهار", default="پروژه عملی", max_length=50)

    main_page_course_section_active = models.BooleanField("فعال کردن قسمت دوره ها در صفحه اصلی", default=True)
    main_page_course_name =  models.CharField("نام قسمت دوره ها در صفحه اصلی", default="بهترین دوره ها", max_length=100)

    main_page_mentors_active = models.BooleanField("فعال کردن قسمت افراد در صفحه اصلی", default=True)
    main_page_mentors_name =  models.CharField("نام قسمت افراد در صفحه اصلی", default="برترین ها", max_length=100)

    main_page_blog_active = models.BooleanField("فعال کردن قسمت مقالات در صفحه اصلی", default=True)
    main_page_blog_name =  models.CharField("نام قسمت مقالات در صفحه اصلی", default="مقالات آموزشی", max_length=100)


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
