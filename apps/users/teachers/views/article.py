from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.article.models import Article
from apps.users.teachers.mixins import TeacherMixin



class ArticleListView(TeacherMixin, ListView):
    model = Article
    permission_field = "can_site_article"
    context_object_name = "articles"
    template_name = "teacher/article/article_list.html"

    def get_queryset(self):
        return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )




class ArticleCreateView(TeacherMixin, CreateView):
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
        "publish",
    )
    template_name = "teacher/article/article_form.html"
    permission_field = "can_site_article"
    success_url = reverse_lazy("teacher:article-list")
    message_info = "برای اضافه کردن دسته بندی جدید با ادمین یا پشتیبانی در ارتباط باشید"

    def form_valid(self, form):

        form.instance.user = self.request.user
        messages.success(self.request, "مقاله ثبت شد")

        return super().form_valid(form)

    def form_invalid(self, form) :
        messages.error(self.request, form.errors)
        return super().form_valid(form)


class ArticleUpdateView(TeacherMixin, UpdateView):
    model = Article
    fields = (
        "category",
        "reading_time",
        "name",
        "summery",
        "text",
        "image",
        "publish",
        "file",
        "name_for_file",
    )
    template_name = "teacher/article/article_form.html"
    permission_field = "can_site_article"
    message_info = "برای اضافه کردن دسته بندی جدید با ادمین یا پشتیبانی در ارتباط باشید"

    success_url = reverse_lazy("teacher:article-list")

    def get_queryset(self):
         return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )

    def form_valid(self, form) :
        messages.success(self.request, "تغییرات ثبت شد")
        return super().form_valid(form)

    def form_invalid(self, form) :
        messages.error(self.request, form.errors)
        return super().form_valid(form)


class ArticleDeleteView(TeacherMixin, DeleteView):
    model = Article
    template_name = "teacher/article/article_confirm_delete.html"
    success_url = reverse_lazy("teacher:article-list")
    permission_field = "can_site_article"
    message_error= "تا می توانید از حذف مقاله جلوگیری کنید"
    def get_queryset(self):

        return Article.objects.filter(
            user=self.request.user,
            is_active=True,
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.error(request,
                       "مقاله حذف شد"
                       )

        return HttpResponseRedirect(self.get_success_url())


