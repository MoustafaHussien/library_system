from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context_processors import csrf

from library_server.forms import RegistrationForm
from .models import Book, BorrowedBook


def main_page(request):
    try:
        book_list = Book.objects.all()
        context = {'book_list': book_list, }
        template = loader.get_template('library_server/index.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404


@login_required
def get_book(request, book_id):
    try:
        book_list = Book.objects.filter(id=book_id)
        if len(book_list) == 0:
            raise Http404
        else:
            context = {'book_list': book_list, }
            template = loader.get_template('library_server/book.html')
            return HttpResponse(template.render(context, request))
    except:
        raise Http404


@login_required
def borrow(request, book_id):
    try:
        if_exist = BorrowedBook.objects.filter(user=request.user.id).filter(book=book_id).exists()
        book_to_borrow = Book.objects.filter(id=book_id)
        if not if_exist:  # create a save a new BorrowedBook
            BorrowedBook.objects.create(user=request.user, book=book_to_borrow[0])
        context = {'if_exist': if_exist, }
        template = loader.get_template('library_server/borrow_page.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404


def registration(request):
    try:
        if request.user.is_authenticated:
            return HttpResponseRedirect('/main_page')
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/main_page')
        else:
            form = RegistrationForm()
        token = {}
        token.update(csrf(request))
        token['form'] = form
        return render_to_response('library_server/registration.html', token)
    except:
        raise Http404


@login_required
def profile(request):
    try:
        join_query = BorrowedBook.objects.filter(user=request.user.id).select_related('book')
        book_list = []
        for join_query_row in join_query:
            book_list.append(join_query_row.book)
        context = {'book_list': book_list, }
        template = loader.get_template('library_server/index.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404
