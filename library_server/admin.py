from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User

from library_server.models import Book, BorrowedBook

# admin.site.register(User)
# admin.site.register(admin)
admin.site.register(Book)
admin.site.register(BorrowedBook)
