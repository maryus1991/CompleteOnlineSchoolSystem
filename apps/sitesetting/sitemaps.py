from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.article.models import Article
from apps.categories.models import BlogCategories
from apps.classes.models import Class
from apps.exams.models import Exam
from apps.questions.models import Question
from apps.sitesetting.models import Site


def _to_gregorian(dt):
    if dt is None:
        return None
    if hasattr(dt, "togregorian"):
        return dt.togregorian()
    return dt


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        names = ["site:main"]
        if not site or site.list_course_active:
            names.append("class:list")
        if not site or site.list_articles_active:
            names.append("article:article-list")
        if not site or site.list_exam_active:
            names.append("exam:list")
        if not site or site.qbank_active:
            names.append("question:list")
        if not site or site.list_users_active:
            names.append("user:list")
        if not site or site.about_active:
            names.append("site:about")
        if not site or site.faq_active:
            names.append("site:faq")
        if not site or site.active_contact:
            names.append("site:contact")
        if not site or site.active_counseling:
            names.append("site:counseling")
        names.append("site:sitemap")
        return names

    def location(self, item):
        return reverse(item)


class BlogCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        if site and not site.list_articles_active:
            return BlogCategories.objects.none()
        return BlogCategories.objects.filter(is_active=True)

    def lastmod(self, obj):
        return _to_gregorian(obj.updated_at)


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.85

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        if site and not site.list_articles_active:
            return Article.objects.none()
        return Article.objects.filter(is_active=True, publish=True, is_public=True)

    def lastmod(self, obj):
        return _to_gregorian(obj.updated_at)


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        if site and not site.list_course_active:
            return Class.objects.none()
        return Class.objects.filter(is_active=True, is_public=True)

    def lastmod(self, obj):
        return _to_gregorian(obj.updated_at)


class ExamSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        if site and not site.list_exam_active:
            return Exam.objects.none()
        return Exam.objects.filter(is_active=True, is_public=True)

    def lastmod(self, obj):
        return _to_gregorian(obj.updated_at)


class QuestionBankSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        site = Site.objects.filter(is_active=True).first()
        if site and not site.qbank_active:
            return Question.objects.none()
        return Question.objects.filter(is_active=True, is_for_qbank=True)

    def lastmod(self, obj):
        return _to_gregorian(obj.updated_at)


SITEMAPS = {
    "static": StaticViewSitemap,
    "categories": BlogCategorySitemap,
    "articles": ArticleSitemap,
    "courses": CourseSitemap,
    "exams": ExamSitemap,
    "qbank": QuestionBankSitemap,
}
