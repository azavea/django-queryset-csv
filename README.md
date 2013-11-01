django-queryset-csv
===================

a CSV exporter for django querysets.

This tool was created out of repeatedly needing to do the following in django:

1. write CSV data that is based on simple querysets.
2. automatically encode unicode characters to utf-8
3. create a shortcut to render a queryset to a CSV HTTP response
4. add a time/datestamping mechanism to CSV filenames

## usage
Perform all filtering and field authorization in your view using `.filter()` and `.values()`.
Then, use `render_to_csv_response` to turn a queryset into a respone with a CSV attachment.
Pass it a `QuerySet` or `ValuesQuerySet` instance.

```python
from djqscsv import render_to_csv_response

def csv_view(request):
  qs = Foo.objects.filter(bar=True).values('id', 'bar')
  return render_to_csv_response(qs)
```

## foreign keys

Foreign keys are supported natively using `ValuesQuerySet` in Django. Simply use the `__` technique as 
you would in the Django ORM when you pass args to the `.values()` method.

in models.py:

```python
from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=20)

class Person(models.Model):
    name = models.CharField(max_length=20)
    favorite_food = models.ForeignKey(Food)

```
in views.py:
```python
from djqscsv import render_to_csv_response

def csv_view(request):
    people = Person.objects.values('name', 'favorite_food__name')
    return render_to_csv_response(people)
```

## todo

django-queryset-csv will be ready for stable release when the following are complete:

1. unit test coverage reaches 100%
2. test coverage is tracked by a CI server
3. custom column headers are supported (currently column headers are always field names)
4. the package is uploaded to pypi.
