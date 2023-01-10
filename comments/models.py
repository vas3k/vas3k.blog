import random
from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import date as django_date
from django.db import models
from django.db.models import F

from posts.models import Post
from users.avatars import AVATARS
from users.models import User
from vas3k_blog.exceptions import BadRequest


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    author = models.ForeignKey(User, related_name="comments", null=True, on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=128, null=True, blank=True)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)

    reply_to = models.ForeignKey("self", related_name="replies", null=True, on_delete=models.CASCADE)
    block = models.CharField(max_length=128, null=True, blank=True)

    text = models.TextField(null=False)
    html_cache = models.TextField(null=True)

    metadata = models.JSONField(null=True)

    ipaddress = models.GenericIPAddressField(null=True)
    useragent = models.CharField(max_length=512, null=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    upvotes = models.IntegerField(default=0, db_index=True)

    is_visible = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    deleted_by = models.UUIDField(null=True)

    class Meta:
        db_table = "comments"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.reply_to and self.reply_to.reply_to and self.reply_to.reply_to.reply_to_id:
            raise BadRequest(message="3 уровня комментариев это максимум")

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def delete(self, deleted_by=None, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def undelete(self, *args, **kwargs):
        self.is_deleted = False
        self.save()

    def increment_vote_count(self):
        return Comment.objects.filter(id=self.id).update(upvotes=F("upvotes") + 1)

    def decrement_vote_count(self):
        return Comment.objects.filter(id=self.id).update(upvotes=F("upvotes") - 1)

    def is_deletable_by(self, user):
        return user == self.author or user.is_admin()

    @classmethod
    def visible_objects(cls, show_deleted=False):
        comments = cls.objects\
            .filter(is_visible=True)\
            .select_related("author", "post", "reply_to")

        if not show_deleted:
            comments = comments.filter(is_deleted=False)

        return comments

    def natural_created_at(self):
        if self.created_at > datetime.utcnow() - timedelta(days=7):
            return naturaltime(self.created_at)
        return django_date(self.created_at, "d E Y в H:i")

    def get_avatar(self):
        if self.author:
            return self.author.get_avatar()
        return random.choice(AVATARS)
