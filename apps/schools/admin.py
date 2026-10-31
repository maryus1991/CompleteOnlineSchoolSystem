from django.contrib import admin
from .models import School, SchoolAnnouncement


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user_manager",
        "province",
        "city",
        "enable_live_classes",
        "enable_exams",
        "enable_advising",
        "is_active",
    )
    list_filter = (
        "is_active",
        "enable_live_classes",
        "enable_exams",
        "enable_advising",
        "enable_tickets",
    )
    search_fields = ("name", "province", "city", "user_manager__user__PhoneNumber")


@admin.register(SchoolAnnouncement)
class SchoolAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "school", "target_audience", "is_important", "is_active", "created_at")
    list_filter = ("school", "target_audience", "is_important", "is_active")
    search_fields = ("title", "content", "school__name")
