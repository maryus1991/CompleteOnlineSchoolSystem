from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.article.models import ArticleTags
from apps.categories.models import BlogCategories
from apps.users.managers.forms.articles import ManagerArticleForm
from apps.users.managers.mixins import ManagerMixin


class ManagerArticleListView(ManagerMixin, ListView):
    template_name = "manager/articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 20
    permission_field = "can_manage_articles"

    def get_queryset(self):
        qs = (
            self.get_school_articles_queryset()
            .prefetch_related("tags")
            .order_by("-sort_number", "-pk")
        )
        q = (self.request.GET.get("q") or "").strip()
        scope = (self.request.GET.get("scope") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(summery__icontains=q))
        if scope == "public":
            qs = qs.filter(is_public=True)
        elif scope == "school":
            qs = qs.filter(is_public=False)
        if status == "active":
            qs = qs.filter(is_active=True)
        elif status == "inactive":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["blog_categories"] = BlogCategories.objects.filter(is_active=True)
        return ctx


class ManagerArticleCreateView(ManagerMixin, TemplateView):
    template_name = "manager/articles/article_form.html"
    permission_field = "can_manage_articles"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_edit"] = False
        if "form" not in ctx:
            ctx["form"] = ManagerArticleForm(
                initial={"is_public": True, "publish": True, "is_active": True}
            )
        return ctx

    def post(self, request, *args, **kwargs):
        form = ManagerArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.school = self.get_school()
            article.save()

            tags_csv = (form.cleaned_data.get("tags_csv") or "").strip()
            if tags_csv:
                for tag_name in [t.strip() for t in tags_csv.split(",") if t.strip()]:
                    ArticleTags.objects.create(post=article, name=tag_name)

            messages.success(request, f"مقاله «{article.name}» با موفقیت ایجاد شد.")
            return redirect("manager:article-list")
        messages.error(request, "لطفاً اطلاعات فرم مقاله را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form))


class ManagerArticleUpdateView(ManagerMixin, TemplateView):
    template_name = "manager/articles/article_form.html"
    permission_field = "can_manage_articles"

    def get_article(self):
        return get_object_or_404(
            self.get_school_articles_queryset(), pk=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.get_article()
        ctx["article_obj"] = article
        ctx["is_edit"] = True
        if "form" not in ctx:
            existing_tags = ", ".join(
                article.tags.filter(is_active=True).values_list("name", flat=True)
            )
            ctx["form"] = ManagerArticleForm(
                instance=article, initial={"tags_csv": existing_tags}
            )
        return ctx

    def post(self, request, *args, **kwargs):
        article = self.get_article()
        form = ManagerArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.school_id:
                updated.school = self.get_school()
            updated.save()

            tags_csv = (form.cleaned_data.get("tags_csv") or "").strip()
            if tags_csv is not None:
                article.tags.update(is_active=False)
                for tag_name in [t.strip() for t in tags_csv.split(",") if t.strip()]:
                    tag_obj, _ = ArticleTags.objects.get_or_create(
                        post=article, name=tag_name
                    )
                    tag_obj.is_active = True
                    tag_obj.save(update_fields=["is_active"])

            messages.success(request, f"مقاله «{updated.name}» با موفقیت ویرایش شد.")
            return redirect("manager:article-list")
        return self.render_to_response(self.get_context_data(form=form))


class ManagerArticleToggleActiveView(ManagerMixin, View):
    permission_field = "can_manage_articles"

    def post(self, request, pk, *args, **kwargs):
        article = get_object_or_404(self.get_school_articles_queryset(), pk=pk)
        new_state = self.toggle_object_active(article)
        status_label = "فعال" if new_state else "غیرفعال"
        messages.info(
            request,
            f"وضعیت مقاله «{article.name}» به «{status_label}» تغییر یافت.",
        )
        return redirect(request.META.get("HTTP_REFERER") or "manager:article-list")
