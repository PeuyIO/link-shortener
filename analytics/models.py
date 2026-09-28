from django.db import models


class Click(models.Model):
    link = models.ForeignKey(
        "links.Link",
        on_delete=models.CASCADE,
        related_name="clicks",
    )

    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click {self.id} — {self.link}"
