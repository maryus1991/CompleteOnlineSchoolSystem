from django.contrib import admin
from .models import Manager


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "province",
        "city",
        "can_manage_users",
        "can_change_teacher_permissions",
        "can_change_adviser_permissions",
        "can_view_reports",
        "is_active",
    )
    list_filter = (
        "is_active",
        "can_manage_users",
        "can_change_teacher_permissions",
        "can_change_adviser_permissions",
        "can_manage_classes",
        "can_manage_exams",
        "can_manage_live_classes",
        "can_view_reports",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__PhoneNumber",
        "province",
        "city",
    )
