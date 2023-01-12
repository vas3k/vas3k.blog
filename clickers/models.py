from django.db import models


class Clicker(models.Model):
    post = models.ForeignKey("posts.Post", related_name="clickers", on_delete=models.CASCADE)
    comment = models.ForeignKey("comments.Comment", related_name="clickers", null=True, on_delete=models.SET_NULL)
    block = models.TextField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ipaddress = models.GenericIPAddressField(db_index=True)
    useragent = models.CharField(max_length=256)

    class Meta:
        db_table = "clickers"
