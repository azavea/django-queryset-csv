django-queryset-csv
===================
[![Build Status](https://travis-ci.org/azavea/django-queryset-csv.png)](https://travis-ci.org/azavea/django-queryset-csv)
[![Coverage Status](https://coveralls.io/repos/azavea/django-queryset-csv/badge.png)](https://coveralls.io/r/azavea/django-queryset-csv)
[![Version](https://pypip.in/v/django-queryset-csv/badge.png)](http://pypi.python.org/pypi/django-queryset-csv/)
[![Downloads](https://pypip.in/d/django-queryset-csv/badge.png)](http://pypi.python.org/pypi/django-queryset-csv/)
[![License](https://pypip.in/license/django-queryset-csv/badge.png)](http://www.gnu.org/licenses/gpl.html)


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

Planned development items are logged on the github issues page.
