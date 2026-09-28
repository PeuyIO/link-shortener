import secrets
import string

from django.conf import settings
from django.db import models
# Create your models here.
ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length=7):
    return "".join(
        secrets.choice(ALPHABET)
        for _ in range(length)
    )


class Link(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="links",
    )

    original_url = models.URLField(max_length=2048)

    short_code = models.CharField(
        max_length=12,
        unique=True,
        default=generate_short_code,
        db_index=True,
    )

    clicks_count = models.PositiveBigIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code