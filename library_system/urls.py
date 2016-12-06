"""library_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views

from library_server import views

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^main_page/', views.main_page, name='main_page'),
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout'),
    url(r'^borrow/([0-9]+)/$', views.borrow, name='borrow_page'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^books/([0-9]+)/$', views.get_book, name='book_page'),
    url(r'^', views.main_page, name='empty_url'),
]
