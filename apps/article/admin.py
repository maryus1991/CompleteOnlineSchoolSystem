from django.contrib import admin
from .models import Article, ArticleComment, ArticleRating, ArticleTags

admin.site.register(Article)
admin.site.register(ArticleTags)


@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "session_key", "score", "updated_at", "is_active")
    list_filter = ("score", "is_active")
    search_fields = ("article__name", "user__first_name", "user__last_name", "user__PhoneNumber")


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "parent", "is_approved", "is_active", "created_at")
    raw_id_fields = ("parent",)
    list_filter = ("is_approved", "is_active")
    search_fields = ("article__name", "user__first_name", "user__last_name", "text")
