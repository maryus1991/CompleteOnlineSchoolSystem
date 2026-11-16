from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.contrib.sitemaps.views import sitemap
from apps.sitesetting.sitemaps import SITEMAPS
from django.db import connections
from django.core.cache import caches


def healthz_view(request):
    db_ok = True
    cache_ok = True

    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_ok = False

    try:
        caches["default"].set("healthcheck_ping", "ok", timeout=10)
        cache_ok = caches["default"].get("healthcheck_ping") == "ok"
    except Exception:
        cache_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {
            "status": "ok" if db_ok else "degraded",
            "database": db_ok,
            "cache": cache_ok,
            "orm_cache_enabled": getattr(settings, "CACHALOT_ENABLED", False),
        },
        status=status_code,
    )


def robots_txt_view(request):
    site = getattr(request, "site", None)
    base_url = (getattr(site, "canonical_base_url", "") or "").strip().rstrip("/")
    sitemap_url = f"{base_url}/sitemap.xml" if base_url else request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /student/",
        "Disallow: /teacher/",
        "Disallow: /adviser/",
        "Disallow: /manager/",
        "Disallow: /users/auth/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


urlpatterns = [
    path('healthz/', healthz_view, name='healthz'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('admin/', admin.site.urls),
    path('', include('apps.sitesetting.urls')),
    path('posts/', include('apps.article.urls')),
    path('courses/', include('apps.classes.urls')),
    path('users/', include('apps.users.accounts.urls')),
    path('exams/', include('apps.exams.urls')),
    path('qbank/', include('apps.questions.urls')),
    path('student/', include('apps.users.students.urls')),
    path('teacher/', include('apps.users.teachers.urls')),
    path('adviser/', include('apps.users.advisers.urls')),
    path('manager/', include('apps.users.managers.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

if settings.ENABLE_DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns = debug_toolbar_urls() + urlpatterns


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)