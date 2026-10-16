from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.article.models import Article
from apps.users.teachers.mixins import TeacherMixin
from apps.users.teachers.mixins import SiteArticlePermissionMixin

class ArticleCreateView(TeacherMixin, SiteArticlePermissionMixin, CreateView):
    model = Article
    fields = (
        "category",
        "reading_time",
        "name",
        "summery",
        "text",
        "image",
        "file",
        "name_for_file",
    )
    template_name = "teacher/article/article_form.html"

    def form_valid(self, form):
        self.get_teacher()
        form.instance.user = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(TeacherMixin, SiteArticlePermissionMixin, UpdateView):
    model = Article
    fields = (
        "category",
        "reading_time",
        "name",
        "summery",
        "text",
        "image",
        "file",
        "name_for_file",
    )
    template_name = "teacher/article/article_form.html"

    def get_queryset(self):
        self.get_teacher()
        return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )


class ArticleDeleteView(TeacherMixin, SiteArticlePermissionMixin, DeleteView):
    model = Article
    template_name = "teacher/article/article_confirm_delete.html"
    success_url = reverse_lazy("article:teacher-article-list")

    def get_queryset(self):
        self.get_teacher()
        return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )

    def delete(self, request, *args, **kwargs):
        # حذف نرم؛ رکورد از دیتابیس پاک نمی‌شود.
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class ArticleListView(TeacherMixin, SiteArticlePermissionMixin, ListView):
    model = Article
    context_object_name = "articles"
    template_name = "teacher/article/article_list.html"

    def get_queryset(self):
        self.get_teacher()
        return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )
