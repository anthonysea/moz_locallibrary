import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.models import Book, Author, BookInstance, Genre
from django.db.models import Q
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.forms import RenewBookForm

def index(request):
    """View function for home page of the site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    num_fictional_books = Book.objects.filter(~Q(genre__name__contains='Non-fiction')).count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_fictional_books': num_fictional_books,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    ## Can define context_object, queryset, and template_name
    # context_object_name = 'my_book_list' # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location
    template_name = 'book_list.html'
    paginate_by = 10

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

class BookDetailView(generic.DetailView):
    """Generic view to view the details of a single book."""
    model = Book
    template_name = 'book_detail.html'

class AuthorListView(generic.ListView):
    """Generic view to list all of the authors in the database."""
    model = Author
    template_name = 'author_list.html'
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    """Generic view to view the details of an author."""
    model = Author
    template_name = 'author_detail.html'

class LoanedBooksView(LoginRequiredMixin, UserPassesTestMixin,  generic.ListView):
    """Generic view that lists all the books that are currently on loan. Only available to librarian users."""
    model = BookInstance
    template_name = 'loanedbooks_list.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

    def test_func(self):
        return self.request.user.groups.filter(name="Librarian").exists()

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """Function-based view to manage the renewal of books out on loan."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'book_renew_librarian.html', context)


class AuthorCreate(CreateView, PermissionRequiredMixin):
    """Generic view to add an author to the database."""
    model = Author
    fields = '__all__'
    #initial = {'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'
    template_name = 'author_form.html'

class AuthorUpdate(UpdateView, PermissionRequiredMixin):
    """Generic view to update the fields of a given author."""
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'
    template_name = 'author_form.html'

class AuthorDelete(DeleteView, PermissionRequiredMixin):
    """Generic view to confirm deletion of an author."""
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'
    template_name = 'author_confirm_delete.html'

class BookCreate(CreateView, PermissionRequiredMixin):
    """Generic view to add a book to the database."""
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    template_name = 'book_form.html'

class BookUpdate(UpdateView, PermissionRequiredMixin):
    """Generic view to update the fields of a book."""
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'
    template_name = 'book_form.html'

class BookDelete(DeleteView, PermissionRequiredMixin):
    """Generic view to confirm deletion of a book."""
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
    template_name = 'book_confirm_delete.html'