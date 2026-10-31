from django import forms
from apps.article.models import Article
from apps.categories.models import BlogCategories


class ManagerArticleForm(forms.ModelForm):
    tags_csv = forms.CharField(
        label="برچسب‌ها (با کاما جدا کنید)",
        required=False,
        max_length=500,
    )

    class Meta:
        model = Article
        fields = [
            "name",
            "category",
            "reading_time",
            "summery",
            "text",
            "image",
            "file",
            "name_for_file",
            "is_public",
            "publish",
            "is_active",
        ]
        widgets = {
            "summery": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False
        self.fields["category"].queryset = BlogCategories.objects.filter(is_active=True)
