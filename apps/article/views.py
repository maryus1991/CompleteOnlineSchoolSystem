from django.contrib import messages
from django.db.models import Avg, Count, Prefetch, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import ArticleCommentForm, ArticleRatingForm
from .models import Article, ArticleComment, ArticleRating, BlogCategories

from django.contrib.auth.mixins import LoginRequiredMixin

def _is_comment_moderator(user):
    return bool(
        user
        and user.is_authenticated
        and user.is_superuser

    )


def _build_rating_summary(article, request):
    qs = article.ratings.filter(is_active=True)
    agg = qs.aggregate(avg=Avg("score"), total=Count("id"))
    total = agg["total"] or 0
    avg = round(agg["avg"], 1) if agg["avg"] else 0.0

    counts = {item["score"]: item["c"] for item in qs.values("score").annotate(c=Count("id"))}
    distribution = []
    for star in (5, 4, 3, 2, 1):
        count = counts.get(star, 0)
        percent = round((count / total) * 100) if total else 0
        distribution.append({"stars": star, "count": count, "percent": percent})

    user_rating = None
    if request.user.is_authenticated:
        own = qs.filter(user=request.user).first()
        if own:
            user_rating = own.score
    elif request.session.session_key:
        own = qs.filter(session_key=request.session.session_key).first()
        if own:
            user_rating = own.score

    return {
        "rating_avg": avg,
        "rating_count": total,
        "rating_distribution": distribution,
        "user_rating": user_rating,
    }


class ArticleListView(ListView):
    """listing view for articles"""
    template_name = "main/blog/list.html"
    context_object_name = "items"
    paginate_by = 100

    def dispatch(self, request, *args, **kwargs):
        if not request.site.list_articles_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if tag := self.request.GET.get("tag"):
            return Article.objects.filter(
                is_active=True, publish=True, tags__name__icontains=tag
            ).select_related("category").distinct()
        if q := self.request.GET.get("q"):
            return Article.objects.filter(is_active=True, publish=True).filter(
                Q(name__icontains=q) |
                Q(summery__icontains=q) |
                Q(text__icontains=q) |
                Q(name_for_file__icontains=q) |
                Q(category__name__icontains=q)
            ).select_related("category").distinct()
        return Article.objects.filter(is_active=True, publish=True).select_related("category")

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update({
            "categories": BlogCategories.objects.filter(is_active=True).all(),
            "pk": False,
        })
        return data


class ArticleCategoryListView(ListView):
    """listing view for articles"""
    template_name = "main/blog/list.html"
    context_object_name = "items"
    paginate_by = 100

    def dispatch(self, request, *args, **kwargs):
        if not request.site.list_articles_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        try:
            if q := self.request.GET.get("q"):
                return BlogCategories.objects.get(is_active=True, pk=self.kwargs.get("pk")).posts.filter(
                    is_active=True, publish=True
                ).filter(
                    Q(name__icontains=q) |
                    Q(summery__icontains=q) |
                    Q(text__icontains=q) |
                    Q(name_for_file__icontains=q) |
                    Q(category__name__icontains=q)
                ).select_related("category").distinct()
            return BlogCategories.objects.get(is_active=True, pk=self.kwargs.get("pk")).posts.filter(
                is_active=True, publish=True
            ).select_related("category")
        except BlogCategories.DoesNotExist:
            raise Http404()

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data.update({
            "categories": BlogCategories.objects.filter(is_active=True).all(),
            "pk": self.kwargs.get("pk"),
        })
        return data


class ArticleDetailView(DetailView):
    """detail view for articles"""
    queryset = Article.objects.filter(is_active=True, publish=True).select_related("category", "user").prefetch_related("tags")
    template_name = "main/blog/details.html"
    context_object_name = "item"

    def dispatch(self, request, *args, **kwargs):
        if not request.site.list_articles_active:
            messages.error(request, "این صفحه غیر فعال میباشد")
            return redirect("site:main")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        rating_summary = _build_rating_summary(self.object, self.request)
        replies_qs = ArticleComment.objects.filter(
            is_active=True, is_approved=True
        ).select_related("user").order_by("created_at", "pk")
        comments = self.object.comments.filter(
            is_active=True, is_approved=True, parent__isnull=True
        ).select_related("user").prefetch_related(
            Prefetch("replies", queryset=replies_qs)
        )
        comments_count = self.object.comments.filter(
            is_active=True, is_approved=True
        ).count()
        data.update({
            "related_posts": self.object.category.posts.filter(is_active=True, publish=True).exclude(pk=self.object.pk),
            "comments": comments,
            "comments_count": comments_count,
            "can_moderate_comments": _is_comment_moderator(self.request.user),
            "comment_form": ArticleCommentForm(),
            **rating_summary,
        })
        return data


class ArticleRateView(View):
    """Rate an article from 1 to 5 stars"""

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk, is_active=True, publish=True)
        form = ArticleRatingForm(request.POST)
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

        if not form.is_valid():
            msg = "امتیاز باید عددی بین ۱ تا ۵ باشد."
            if is_ajax:
                return JsonResponse({"error": msg}, status=400)
            messages.error(request, msg)
            return redirect(f"{article.get_absolute_url()}#article-rating")

        score = form.cleaned_data["score"]
        if request.user.is_authenticated:
            ArticleRating.objects.update_or_create(
                article=article,
                user=request.user,
                defaults={"score": score, "is_active": True},
            )
        else:
            if not request.session.session_key:
                request.session.create()
            ArticleRating.objects.update_or_create(
                article=article,
                session_key=request.session.session_key,
                defaults={"score": score, "is_active": True},
            )

        summary = _build_rating_summary(article, request)
        msg = f"امتیاز {score} از ۵ ستاره با موفقیت ثبت شد."
        if is_ajax:
            return JsonResponse({"message": msg, **summary})
        messages.success(request, msg)
        return redirect(f"{article.get_absolute_url()}#article-rating")


class ArticleCommentCreateView(LoginRequiredMixin, View):
    """Post a comment or 1-level reply on an article (authenticated/registered users only)"""

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk, is_active=True, publish=True)
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

        if not request.user.is_authenticated:
            msg = "برای ثبت دیدگاه ابتدا باید ثبت‌نام کنید یا وارد حساب کاربری خود شوید."
            if is_ajax:
                return JsonResponse({"error": msg}, status=401)
            messages.error(request, msg)
            auth_url = reverse("user:auth")
            return redirect(f"{auth_url}?next={article.get_absolute_url()}#comments")

        form = ArticleCommentForm(request.POST)
        if not form.is_valid():
            err_msg = next(iter(form.errors.values()))[0] if form.errors else "متن دیدگاه معتبر نیست."
            if is_ajax:
                return JsonResponse({"error": err_msg}, status=400)
            messages.error(request, err_msg)
            return redirect(f"{article.get_absolute_url()}#comments")

        parent = None
        parent_id = form.cleaned_data.get("parent_id")
        if parent_id is not None:
            parent = ArticleComment.objects.filter(
                pk=parent_id,
                article=article,
                is_active=True,
                is_approved=True,
            ).first()
            if parent is None:
                err_msg = "دیدگاه مورد نظر برای پاسخ یافت نشد."
                if is_ajax:
                    return JsonResponse({"error": err_msg}, status=404)
                messages.error(request, err_msg)
                return redirect(f"{article.get_absolute_url()}#comments")
            if parent.parent_id is not None:
                err_msg = "پاسخ‌دهی به دیدگاه‌ها فقط در یک سطح مجاز است و امکان پاسخ تو در تو وجود ندارد."
                if is_ajax:
                    return JsonResponse({"error": err_msg}, status=400)
                messages.error(request, err_msg)
                return redirect(f"{article.get_absolute_url()}#comments")

        ArticleComment.objects.create(
            article=article,
            user=request.user,
            parent=parent,
            text=form.cleaned_data["text"],
            is_approved=True if request.site.approve_the_new_comments else False,
        )
        success_msg = "پاسخ شما با موفقیت ثبت شد." if parent else "دیدگاه شما با موفقیت ثبت شد."
        if is_ajax:
            return JsonResponse({"message": success_msg}, status=201)
        messages.success(request, success_msg)
        return redirect(f"{article.get_absolute_url()}#comments")


class ArticleCommentDeleteView(LoginRequiredMixin, View):
    """Delete an article comment or reply (admin / manager only)"""

    def post(self, request, pk, comment_pk):
        article = get_object_or_404(Article, pk=pk, is_active=True, publish=True)
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or "application/json" in request.headers.get("Accept", "")

        if not request.user.is_authenticated:
            msg = "برای حذف دیدگاه ابتدا وارد حساب ادمین شوید."
            if is_ajax:
                return JsonResponse({"error": msg}, status=401)
            messages.error(request, msg)
            auth_url = reverse("user:auth")
            return redirect(f"{auth_url}?next={article.get_absolute_url()}#comments")

        if not _is_comment_moderator(request.user):
            msg = "فقط ادمین (مدیر) مجاز به حذف دیدگاه‌ها است."
            if is_ajax:
                return JsonResponse({"error": msg}, status=403)
            messages.error(request, msg)
            return redirect(f"{article.get_absolute_url()}#comments")

        comment = get_object_or_404(ArticleComment, pk=comment_pk, article=article)
        comment.is_active = False
        comment.save(update_fields=["is_active"])

        msg = "دیدگاه با موفقیت حذف شد."
        if is_ajax:
            return JsonResponse({"deleted": True, "message": msg})
        messages.success(request, msg)
        return redirect(f"{article.get_absolute_url()}#comments")
