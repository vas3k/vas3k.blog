from django.db import models


class TranslationState(models.Model):
    source = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="translation_states")
    language = models.CharField(max_length=2)
    target = models.ForeignKey("posts.Post", null=True, blank=True, on_delete=models.SET_NULL, related_name="translation_sources")
    source_fields = models.JSONField(default=dict)
    target_fields = models.JSONField(default=dict)
    pending = models.BooleanField(default=True, db_index=True)
    error = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "language"], name="unique_post_translation_state"),
        ]
