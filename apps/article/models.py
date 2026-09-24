from django.db import models
from apps.common.models import BaseModel
from apps.users.accounts.models import User
from apps.categories.models import BlogCategories
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.file_storage_script_for_model import UploadPath
from django_resized import ResizedImageField
from django.urls import reverse_lazy

class Article(BaseModel):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE, verbose_name="نویسنده")
    category = models.ForeignKey(BlogCategories, related_name="posts", on_delete=models.CASCADE, verbose_name="دسته بندی")
    reading_time = models.IntegerField("زمان مطالعه (دقیقه)", default=10)
    name = models.CharField(max_length=255, verbose_name='عنوان')
    summery = models.CharField(max_length=500, verbose_name='خلاصه')
    text = CKEditor5Field("توضیحات")
    image = ResizedImageField("عکس", upload_to=UploadPath("articles-images"))
    file = models.FileField("فایل", upload_to=UploadPath("article-files"), null=True, blank=True)
    name_for_file = models.CharField(max_length=255, verbose_name='عنوان فایل', null=True, blank=True)

    def __str__(self):
        return self.name


    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

    def get_absolute_url(self):
        return reverse_lazy("article:article-details", kwargs={"pk": self.pk})


class ArticleTags(BaseModel):

    post = models.ForeignKey(Article, related_name="tags", on_delete=models.CASCADE, verbose_name="تگ ها")
    name = models.CharField(max_length=255, verbose_name='عنوان')
    url = models.URLField(default="#", verbose_name="لینک")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'تگ مقاله'
        verbose_name_plural = 'تگ های مقاله'