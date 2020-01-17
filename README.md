# MDN LocalLibrary 

Django walkthrough by the Mozilla Developer Network to create a simulated library interface web application

## Learning points

- [get_absolute_url](https://docs.djangoproject.com/en/3.0/ref/models/instances/#get-absolute-url)

    ```python
    def get_absolute_url(self):  
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])
    ```
    Used in the template to refer to individual records i.e. used in a list view to go to a detailed view

    In the template:
    ```html
    {% for book in book_list %}
        {{ book.get_absolute_url }}
    {% endfor %}
    ```

- [django.views.generic](https://docs.djangoproject.com/en/3.0/ref/class-based-views/generic-display/)

    ```python 
    from django.views import generic
    
    class AuthorListView(generic.ListView):
        # List view
        model = Author
        template_name = 'author_list.html'

    class AuthorDetailView(generic.DetailView):
        # Detail view
        model = Author
        template_name = 'author_detail.html'
        # queryset = Author.objects.filter(first_name__contains='sun')
    ```


    Generic views from `django.views` that define common functionality such as lists and individual record details so you don't have to implement that

    Within the generic views, can also change functionality such as `queryset`, `template_name`, pagination (`paginate_by`) and `context_data`

- [Following relationships 'backwards'](https://docs.djangoproject.com/en/3.0/topics/db/queries/#following-relationships-backward) (reverse lookup) with `FOO_set.all` where `FOO` is the source model name (model with the foreign key)

    Reverse lookup can be done using `_set` on the table that has the foreign key, `_set` returns a QuerySet that can be used with `all()`, `filter()`, etc

    ```python
    # Blog has one-to-many relationship with Entry
    b = Blog.objects.get(id=1)
    b.entry_set.all() # Returns all Entry objects related to Blog
    ```


- When updating `request.session`, if you are updating some information within session data, then Django willl not recognise that you've made a change to the session data, therefore you have to explicitly mark the session as having been modified
    
    ```python
    # Session object not directly modified, only data within the session. Session changes not saved!
    request.session['my_car']['wheels'] = 'alloy'

    # Set session as modified to force data updates/cookie to be saved.
    request.session.modified = True
    ```

- [Limiting access to logged-in users](https://docs.djangoproject.com/en/3.0/topics/auth/default/#limiting-access-to-logged-in-users)

    Can use `@login_required` decorator for function-based views, or `LoginRequiredMixin` for class-based views, which is passed as an argument to the class definition