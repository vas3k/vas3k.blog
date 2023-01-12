from datetime import datetime
from uuid import uuid4

from django.db import models
from django.urls import reverse

from utils.slug import generate_unique_slug


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    slug = models.CharField(max_length=64, unique=True, db_index=True)
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
    rss_cache = models.TextField(null=True, blank=True)

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

    class Meta:
        db_table = "posts"
        ordering = ("-created_at",)

    def __unicode__(self):
        return f"{self.type}/{self.slug}"

    @classmethod
    def visible_objects(cls):
        return cls.objects.filter(is_visible=True, published_at__lte=datetime.utcnow()).order_by("-published_at")

    def save(self, flush_cache=True, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Post, self.title)

        if not self.published_at and self.is_visible:
            self.published_at = datetime.utcnow()

        if flush_cache:
            self.html_cache = True
            self.rss_cache = True

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

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

    def season_grouper(self):
        groups = {
            1: "Зима",
            2: "Зима",
            3: "Весна",
            4: "Весна",
            5: "Весна",
            6: "Лето",
            7: "Лето",
            8: "Лето",
            9: "Лето",
            10: "Осень",
            11: "Осень",
            12: "Зима",
        }
        month = int(self.created_at.strftime("%-m"))
        year = int(self.created_at.strftime("%Y"))
        if month <= 2:
            # next year's winter is still the same winter
            return f"{groups.get(month)} {year - 1}"
        return f"{groups.get(month)} {year}"
