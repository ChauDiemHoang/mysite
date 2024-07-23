from django.db import models
from django.urls import reverse
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text=_('Enter a book genre (e.g. Science Fiction)'))

    def __str__(self):
        return self.name      
  
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text=_('Enter a brief description of the book'))
    isbn = models.CharField('ISBN', max_length=13, help_text=_('13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'))

    genre = models.ManyToManyField(Genre, help_text=_('Select a genre for this book'))

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for this particular book across whole library'))
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True) 
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    class LOAN_STATUS(models.TextChoices):
        MAINTENANCE = 'm', 'Maintenance'
        ON_LOAN = 'o', 'On loan'
        AVAILABLE = 'a', 'Available'
        RESERVED = 'r', 'Reserved'

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS.choices,
        blank=True,
        default="m",
        help_text=_("Book availability"),
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id} ({self.book.title})'
    
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
  
    def clean(self):
        super().clean()
        if self.date_of_death and self.date_of_birth:
            if self.date_of_death < self.date_of_birth:
                raise ValidationError(_('Death date cannot be before birth date.'))
