from django.contrib import admin

from .models import Article, ArticleTags


admin.site.register(Article)
admin.site.register(ArticleTags)