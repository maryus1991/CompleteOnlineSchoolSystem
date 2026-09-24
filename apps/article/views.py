from unicodedata import category

from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, DetailView


from .models import Article, BlogCategories


class ArticleListView(ListView):
    """listing view for articles"""

    template_name = "main/blog/list.html"
    context_object_name = "items"
    paginate_by = 100

    def get_queryset(self):
        if q:=self.request.GET.get("q"):
            print(q)
            return Article.objects.filter(is_active=True).filter(
                Q(name__icontains=q) |
                Q(summery__icontains=q) |
                Q(text__icontains=q) |
                Q(name_for_file__icontains=q) |
                Q(category__name__icontains=q)
            ).select_related("category").distinct()
        else:
            return Article.objects.filter(is_active=True).select_related("category")

    def get_context_data( self, *args, **kwargs ) :
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

    def get_queryset(self):

        try:
            if q := self.request.GET.get("q"):
                return BlogCategories.objects.get(is_active=True, pk=self.kwargs.get("pk")).posts.filter(is_active=True).filter(
                Q(name__icontains=q) |
                Q(summery__icontains=q) |
                Q(text__icontains=q) |
                Q(name_for_file__icontains=q) |
                Q(category__name__icontains=q)
            ).select_related("category").distinct()
            else:
                return BlogCategories.objects.get(is_active=True, pk=self.kwargs.get("pk")).posts.filter(is_active=True).select_related("category")

        except BlogCategories.DoesNotExist:
            raise Http404()

    def get_context_data( self, *args, **kwargs ) :
        data = super().get_context_data(*args, **kwargs)
        data.update({
            "categories": BlogCategories.objects.filter(is_active=True).all(),
            "pk": self.kwargs.get("pk"),
        })

        return data

class ArticleDetailView(DetailView):
    """detail view for articles"""

    queryset = Article.objects.filter(is_active=True).select_related("category", "user").prefetch_related("tags")
    template_name = "main/blog/details.html"
    context_object_name = "item"

    def get_context_data( self, *args, **kwargs ) :
        data = super().get_context_data(*args, **kwargs)

        data.update({
            "related_posts" :  self.object.category.posts.filter(is_active=True).all(),
        })
        return data