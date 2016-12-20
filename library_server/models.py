from __future__ import unicode_literals

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    pub_date = models.DateField()
    title = models.CharField(max_length=200, default="")
    author = models.CharField(max_length=200, default="")
    publisher = models.CharField(max_length=200, default="")
    isbn = models.CharField(max_length=200, default="")
    img = models.CharField(max_length=1000, default="http://placehold.it/700x400")
    available_copies = models.IntegerField(default=0)

    def __str__(self):  # __unicode__ on Python 2
        return self.title + ' ' + self.author


class BorrowedBook(models.Model):
    class Meta:
        unique_together = (('user', 'book'),)

    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    borrow_date = models.DateField(default=datetime.now)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.user.id) + ' ' + str(self.book)


class BookRequest(models.Model):
    class Meta:
        unique_together = (('user', 'book'),)

    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    request_date = models.DateField(default=datetime.now)

    def __str__(self):  # __unicode__ on Python 2
        return str(self.user.id) + ' ' + str(self.book)
