from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context_processors import csrf

from library_server.forms import RegistrationForm
from .models import Book, BorrowedBook, BookRequest


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


def handle_new_copies_availability(book_to_return):
    request_list = BookRequest.objects.filter(book=book_to_return).order_by('request_date')
    request_list_count = request_list.count()
    available_copies = Book.objects.filter(id=book_to_return.id)[0].available_copies
    for i in range(0, min(available_copies, request_list.count())):
        BorrowedBook.objects.create(user=request_list[i].user, book=book_to_return)
        BookRequest.objects.filter(user=request_list[i].user, book=book_to_return).delete()
    Book.objects.filter(id=book_to_return.id).update(available_copies=(available_copies - min(available_copies, request_list_count)))


@login_required()
def return_(request, book_id):
    try:
        already_borrowed = BorrowedBook.objects.filter(user=request.user.id).filter(book=book_id).exists()
        book_to_return = Book.objects.filter(id=book_id)[0]
        if already_borrowed:  # delete the BorrowedBook
            BorrowedBook.objects.filter(user=request.user, book=book_to_return).delete()
            Book.objects.filter(id=book_id).update(available_copies=book_to_return.available_copies + 1)
            handle_new_copies_availability(book_to_return)
        context = {'already_borrowed': already_borrowed, }
        template = loader.get_template('library_server/return_page.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404


@login_required
def borrow(request, book_id):
    try:
        already_borrowed = BorrowedBook.objects.filter(user=request.user.id).filter(book=book_id).exists()
        book_to_borrow = Book.objects.filter(id=book_id)[0]
        is_queued = True
        if not already_borrowed:  # create and save a new BorrowedBook
            if book_to_borrow.available_copies > 0:
                BorrowedBook.objects.create(user=request.user, book=book_to_borrow)
                Book.objects.filter(id=book_id).update(available_copies=book_to_borrow.available_copies - 1)
                is_queued = False
            else:
                if not BookRequest.objects.filter(user=request.user, book=book_to_borrow).exists():
                    BookRequest.objects.create(user=request.user, book=book_to_borrow)
                is_queued = True
        context = {'already_borrowed': already_borrowed, 'is_queued': is_queued}
        template = loader.get_template('library_server/borrow_page.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404


def search_(request):
    try:
        query_list = request.GET.get('search_box', None).split()
        book_list = Book.objects.none()
        for query in query_list:
            result = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(publisher__icontains=query) | Q(isbn__icontains=query))
            book_list = book_list | result
        context = {'book_list': book_list.distinct(), }
        template = loader.get_template('library_server/index.html')
        return HttpResponse(template.render(context, request))
    except:
        raise Http404
