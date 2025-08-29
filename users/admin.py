from django.contrib import admin
from .models import CustomUser, Genre, Book

# Register your models here
admin.site.register(CustomUser)
admin.site.register(Genre)
admin.site.register(Book)