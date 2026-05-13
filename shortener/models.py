from django.db import models


class ShortURL(models.Model):
    original_url=models.URLField()
    short_code=models.CharField(max_length=10,unique=True)
    created_at=models.DateTimeField(auto_now=True)
    clicks=models.IntegerField(default=0)

    def __str__(self):
        return self.short_code
