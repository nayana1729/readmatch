from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    quiz_genres = models.JSONField(blank=True, null=True)
    books_read = models.ManyToManyField('Book', through='UserBook', blank=True)
    previous_matches = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='matched_by'
    )

    def __str__(self):
        return self.username

class Book(models.Model):
    book_id = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    additional_authors = models.TextField(blank=True, null=True)
    average_rating = models.FloatField(default=0)
    num_pages = models.PositiveIntegerField(default=0)
    year_published = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class UserBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    my_rating = models.FloatField(default=0)
    date_read = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"user: {self.user.username}, book: {self.book.title}, rating: {self.my_rating}"

class UserMatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_matches')
    matched_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_matched_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'matched_user')

    def __str__(self):
        return f"{self.user.username} matched with {self.matched_user.username}"