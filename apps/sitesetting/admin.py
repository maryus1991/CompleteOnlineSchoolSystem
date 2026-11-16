from django.contrib import admin
from .models import Site, Contact, Counseling, FAQ, TestMonomials, TimeLine


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "canonical_base_url", "robots_default", "updated_at")
    search_fields = ("name", "short_description", "seo_title_home")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "هویت برند و اطلاعات پایه",
            {
                "fields": (
                    "is_active",
                    "name",
                    "logo",
                    "logo_svg",
                    "short_description",
                    "description",
                    "copyright",
                    "developer_message",
                    "link_url",
                )
            },
        ),
        (
            "تنظیمات سئو فنی و عمومی (Technical SEO)",
            {
                "fields": (
                    "title_separator",
                    "canonical_base_url",
                    "og_image",
                    "apple_touch_icon",
                    "theme_color",
                    "default_meta_description",
                    "default_meta_keywords",
                    "robots_default",
                    "google_site_verification",
                    "twitter_handle",
                    "organization_type",
                    "price_currency",
                )
            },
        ),
        (
            "سئو اختصاصی صفحات عمومی",
            {
                "classes": ("collapse",),
                "fields": (
                    "seo_title_home",
                    "seo_description_home",
                    "seo_keywords_home",
                    "seo_title_courses",
                    "seo_description_courses",
                    "seo_title_articles",
                    "seo_description_articles",
                    "seo_title_exams",
                    "seo_description_exams",
                    "seo_title_qbank",
                    "seo_description_qbank",
                    "seo_title_teachers",
                    "seo_description_teachers",
                    "seo_title_about",
                    "seo_description_about",
                    "seo_title_faq",
                    "seo_description_faq",
                    "seo_title_contact",
                    "seo_description_contact",
                    "seo_title_counseling",
                    "seo_description_counseling",
                    "seo_title_sitemap",
                    "seo_description_sitemap",
                ),
            },
        ),
        (
            "صفحه اصلی (Hero و آمار)",
            {
                "classes": ("collapse",),
                "fields": (
                    "main_page_badge",
                    "main_page_greeting",
                    "about_img",
                    "main_page_first_button_name",
                    "main_page_first_button_url",
                    "main_page_first_button_svg",
                    "main_page_second_button_name",
                    "main_page_second_button_url",
                    "main_page_second_button_svg",
                    "main_page_first_stats_number",
                    "main_page_first_stats_name",
                    "main_page_first_stats_svg",
                    "main_page_second_stats_number",
                    "main_page_second_stats_name",
                    "main_page_second_stats_svg",
                    "first_stats_card_number",
                    "first_stats_card_symbol",
                    "first_stats_card_name",
                    "first_stats_card_svg",
                    "second_stats_card_number",
                    "second_stats_card_symbol",
                    "second_stats_card_name",
                    "second_stats_card_svg",
                    "third_stats_card_number",
                    "third_stats_card_symbol",
                    "third_stats_card_name",
                    "third_stats_card_svg",
                    "fourth_stats_card_number",
                    "fourth_stats_card_symbol",
                    "fourth_stats_card_name",
                    "fourth_stats_card_svg",
                    "main_page_course_section_active",
                    "main_page_course_name",
                    "main_page_mentors_active",
                    "main_page_mentors_name",
                    "main_page_blog_active",
                    "main_page_blog_name",
                ),
            },
        ),
        (
            "تنظیمات بخش‌های عمومی",
            {
                "classes": ("collapse",),
                "fields": (
                    "list_articles_active",
                    "list_articles_above_tag",
                    "list_articles_title",
                    "list_articles_description",
                    "list_course_active",
                    "list_course_above_tag",
                    "list_course_title",
                    "list_course_description",
                    "count_of_courses_in_course_detail_page",
                    "list_users_active",
                    "list_users_above_tag",
                    "list_users_title",
                    "users_title_url_name",
                    "list_users_description",
                    "list_exam_active",
                    "list_exam_above_tag",
                    "list_exam_title",
                    "list_exam_description",
                    "qbank_active",
                    "qbank_above_tag",
                    "qbank_title",
                    "qbank_description",
                    "about_active",
                    "about_above_tag",
                    "about_title",
                    "faq_active",
                    "faq_above_tag",
                    "faq_title",
                    "faq_description",
                    "active_contact",
                    "contact_above_tag",
                    "contact_title",
                    "contact_description",
                    "phone_number_contact",
                    "email_contact",
                    "active_counseling",
                    "free_counseling_above_tag",
                    "free_counseling_title",
                    "free_counseling_description",
                    "phone_number_counseling",
                    "email_counseling",
                    "auth_title",
                    "login_active",
                    "register_active",
                    "forgot_password_active",
                ),
            },
        ),
        (
            "فوتر، شبکه‌های اجتماعی و سیستم",
            {
                "classes": ("collapse",),
                "fields": (
                    "footer_fast_link_1_name",
                    "footer_fast_link_1_url",
                    "footer_fast_link_2_name",
                    "footer_fast_link_2_url",
                    "footer_fast_link_3_name",
                    "footer_fast_link_3_url",
                    "footer_fast_link_4_name",
                    "footer_fast_link_4_url",
                    "footer_important_1_name",
                    "footer_important_1_url",
                    "footer_important_2_name",
                    "footer_important_2_url",
                    "footer_important_3_name",
                    "footer_important_3_url",
                    "footer_important_4_name",
                    "footer_important_4_url",
                    "instagram_link",
                    "telegram_link",
                    "other_link",
                    "MESSAGE_DURATION",
                    "approve_the_new_comments",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


@admin.register(Counseling)
class CounselingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "status",
        "assigned_adviser",
        "read",
        "created_at",
    )
    list_filter = ("status", "read", "assigned_adviser")
    search_fields = ("full_name", "phone_number", "message", "adviser_follow_up_note")
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Contact)
admin.site.register(FAQ)
admin.site.register(TestMonomials)
admin.site.register(TimeLine)
