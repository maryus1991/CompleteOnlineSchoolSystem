from django.contrib import admin
from .models import Site, Contact, Counseling, FAQ, TestMonomials, TimeLine


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


admin.site.register(Site)
admin.site.register(Contact)
admin.site.register(FAQ)
admin.site.register(TestMonomials)
admin.site.register(TimeLine)
