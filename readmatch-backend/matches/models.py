from django.db import models
from django.conf import settings
# Create your models here.

class Match(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches"
    )
    match_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matched_with"
    )
    previous_matches = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="past_matches_for"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_match_row_per_user')
        ]

    def __str__(self):
        return f"Match(user={self.user.username}, match_user={getattr(self.match_user, 'username', None)})"
