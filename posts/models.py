from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import get_language

from utils.slug import generate_unique_slug


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    slug = models.CharField(max_length=64, db_index=True)
    type = models.CharField(max_length=32, db_index=True)

    author = models.CharField(max_length=64)
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=512, null=True, blank=True)
    subtitle = models.CharField(max_length=512, null=True, blank=True)
    image = models.URLField(null=True, blank=True)

    og_title = models.CharField(max_length=512, null=True, blank=True)
    og_image = models.URLField(null=True, blank=True)
    og_description = models.TextField(null=True, blank=True)
    announce_text = models.TextField(null=True, blank=True)

    text = models.TextField(null=True, blank=True)
    html_cache = models.TextField(null=True, blank=True)

    data = models.JSONField(null=True, blank=True)

    css = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField()
    published_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    word_count = models.PositiveIntegerField(default=0)

    is_raw_html = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_members_only = models.BooleanField(default=False)
    is_commentable = models.BooleanField(default=True)
    is_visible_on_home_page = models.BooleanField(default=False)

    lang = models.CharField(max_length=2, default=settings.LANGUAGE_CODE)

    class Meta:
        db_table = "posts"
        ordering = ("-created_at",)
        unique_together = [["slug", "lang"]]

    def __unicode__(self):
        return f"{self.type}/{self.slug}"

    @classmethod
    def visible_objects(cls):
        return cls.objects.filter(
            is_visible=True,
            published_at__lte=datetime.utcnow(),
            lang=get_language()
        ).order_by("-published_at")

    def save(self, flush_cache=True, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Post, self.title)

        if not self.published_at and self.is_visible:
            self.published_at = datetime.utcnow()

        if flush_cache:
            self.html_cache = None
            self.word_count = strip_tags(self.text).count(" ") if self.text else 0

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def is_published(self):
        return self.is_visible and self.published_at < datetime.utcnow()

    def get_host(self):
        return next((domain for domain, lang in settings.DOMAIN_LANGUAGES.items() if lang == self.lang), None)

    def get_absolute_url(self):
        if self.url:
            return self.url

        return reverse("show_post", kwargs={"post_type": self.type, "post_slug": self.slug})

    def main_image(self):
        if self.image and not self.image.endswith(".mp4"):
            return self.image
        elif self.og_image:
            return self.og_image
        return None
