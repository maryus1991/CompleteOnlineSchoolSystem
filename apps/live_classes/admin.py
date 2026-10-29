from django.contrib import admin
from .models import (
    StreamServers,
    LiveClass,
    LiveClassReport,
    LiveClassRequest,
    AdviserLiveSession,
    AdviserLiveSessionReport,
    AdviserLiveSessionRequest,
)


admin.site.register(StreamServers)
admin.site.register(LiveClass)
admin.site.register(LiveClassReport)
admin.site.register(LiveClassRequest)


@admin.register(AdviserLiveSession)
class AdviserLiveSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "adviser",
        "server",
        "status",
        "scheduled_at",
        "is_active",
    )
    list_filter = ("status", "server", "is_active")
    search_fields = (
        "title",
        "adviser__user__first_name",
        "adviser__user__last_name",
        "adviser__user__PhoneNumber",
        "session_code",
    )
    readonly_fields = ("session_code", "created_at", "updated_at")
    filter_horizontal = ("students",)


@admin.register(AdviserLiveSessionReport)
class AdviserLiveSessionReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "live_session",
        "counseling_session",
        "duration_minutes",
        "attendees_count",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "live_session__title",
        "adviser_note",
        "admin_note",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(AdviserLiveSessionRequest)
class AdviserLiveSessionRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "adviser",
        "preferred_at",
        "duration_minutes",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_active")
    search_fields = (
        "title",
        "description",
        "adviser__user__first_name",
        "adviser__user__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("students",)
