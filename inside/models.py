import hashlib

from django.db import models


class Subscriber(models.Model):
    email = models.CharField(max_length=256, unique=True)
    secret_hash = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bounces = models.IntegerField(default=0)
    data = models.JSONField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = "subscribers"
        ordering = ("-created_at",)

    @classmethod
    def generate_secret(cls, email):
        return hashlib.sha224(str(email).encode()).hexdigest()
