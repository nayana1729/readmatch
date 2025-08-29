from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
	favorite_genres = models.ManyToManyField('Genre', blank=True)
	books_read = models.ManyToManyField('Book', blank=True)
	quiz_answers = models.JSONField(blank=True, null=True)

	def __str__(self):
		return self.username

class Genre(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.name

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	genres = models.ManyToManyField('Genre', blank=True)
	external_id = models.CharField(max_length=100, blank=True, null=True)

	def __str__(self):
		return f"{self.title} by {self.author}"