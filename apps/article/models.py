from django.db import models
from apps.common.models import BaseModel
from apps.users.accounts.models import User
from apps.categories.models import BlogCategories
from django_ckeditor_5.fields import CKEditor5Field
from apps.common.file_storage_script_for_model import UploadPath
from django_resized import ResizedImageField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Q
from django.urls import reverse_lazy

class Article(BaseModel):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE, verbose_name="نویسنده")
    school = models.ForeignKey(
        "schools.School",
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مدرسه",
    )
    is_public = models.BooleanField(default=True, verbose_name="مقاله عمومی")
    category = models.ForeignKey(BlogCategories, related_name="posts", on_delete=models.CASCADE, verbose_name="دسته بندی")
    reading_time = models.IntegerField("زمان مطالعه (دقیقه)", default=10)
    name = models.CharField(max_length=255, verbose_name='عنوان')
    summery = models.CharField(max_length=500, verbose_name='خلاصه')
    text = CKEditor5Field("توضیحات")
    image = ResizedImageField("عکس", upload_to=UploadPath("articles-images"))
    file = models.FileField("فایل", upload_to=UploadPath("article-files"), null=True, blank=True)
    name_for_file = models.CharField(max_length=255, verbose_name='عنوان فایل', null=True, blank=True)
    publish = models.BooleanField(default=False, verbose_name="انتشار")

    def __str__(self):
        return self.name


    class Meta:
        ordering = ['-sort_number', "-pk"]
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'

    def get_absolute_url(self):
        return reverse_lazy("article:article-details", kwargs={"pk": self.pk})

    def get_average_rating(self):
        avg = self.ratings.filter(is_active=True).aggregate(avg=Avg("score"))["avg"]
        return round(avg, 1) if avg else 0

    def get_rating_count(self):
        return self.ratings.filter(is_active=True).count()


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


class ArticleRating(BaseModel):
    article = models.ForeignKey(
        Article,
        related_name="ratings",
        on_delete=models.CASCADE,
        verbose_name="مقاله",
    )
    user = models.ForeignKey(
        User,
        related_name="article_ratings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="کاربر",
    )
    session_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شناسه نشست",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز (۱ تا ۵)",
    )

    class Meta:
        ordering = ["-updated_at", "-pk"]
        verbose_name = "امتیاز مقاله"
        verbose_name_plural = "امتیازهای مقالات"
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"],
                condition=Q(user__isnull=False),
                name="unique_article_user_rating",
            ),
            models.UniqueConstraint(
                fields=["article", "session_key"],
                condition=Q(session_key__isnull=False),
                name="unique_article_session_rating",
            ),
        ]

    def __str__(self):
        who = self.user or self.session_key or "ناشناس"
        return f"{self.article.name} - {self.score}/5 ({who})"


class ArticleComment(BaseModel):
    article = models.ForeignKey(
        Article,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="مقاله",
    )
    user = models.ForeignKey(
        User,
        related_name="article_comments",
        on_delete=models.CASCADE,
        verbose_name="نویسنده دیدگاه",
    )
    parent = models.ForeignKey(
        "self",
        related_name="replies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="پاسخ به دیدگاه",
    )
    text = models.TextField(max_length=1500, verbose_name="متن دیدگاه")
    is_approved = models.BooleanField(default=True, verbose_name="تایید انتشار")

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "دیدگاه مقاله"
        verbose_name_plural = "دیدگاه‌های مقالات"

    def clean(self):
        if self.parent_id and self.parent and self.parent.parent_id is not None:
            raise ValidationError("پاسخ‌دهی به دیدگاه‌ها فقط در یک سطح مجاز است.")

    def __str__(self):
        return f"{self.user} - {self.article.name}"
