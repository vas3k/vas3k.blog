import random
from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from users.avatars import AVATARS
from utils.strings import random_string


class UserAccountManager(BaseUserManager):
    def create_superuser(self, username, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            **other_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email, password=None, **other_fields):
        if not email:
            raise ValueError("Email address is required!")

        email = self.normalize_email(email)
        if password is not None:
            user = self.model(
                username=username,
                email=email,
                password=password,
                **other_fields
            )
            user.save()
        else:
            user = self.model(
                username=username,
                email=email,
                password=password,
                **other_fields
            )
            user.set_unusable_password()
            user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=128, null=False)
    avatar = models.URLField(null=True, blank=True)
    secret_hash = models.CharField(max_length=24, unique=True)

    city = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    vas3k_club_slug = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    patreon_id = models.CharField(max_length=64, db_index=True, null=True, blank=True)
    telegram_id = models.CharField(max_length=64, db_index=True, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_banned = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def save(self, *args, **kwargs):
        if not self.secret_hash:
            self.secret_hash = random_string(length=18)

        if not self.avatar:
            self.avatar = self.get_avatar()

        self.updated_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def update_last_activity(self):
        now = datetime.utcnow()
        if self.last_activity_at < now - timedelta(minutes=5):
            return User.objects.filter(id=self.id).update(last_activity_at=now)

    def get_avatar(self):
        if not self.avatar:
            return random.choice(AVATARS)
        return self.avatar
