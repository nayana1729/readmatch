from django.contrib import admin
from .models import CustomUser, Book, UserBook, UserMatch

# Register your models here
admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(UserBook)
admin.site.register(UserMatch)
