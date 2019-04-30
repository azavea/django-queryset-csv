.. image:: https://travis-ci.org/azavea/django-queryset-csv.png
   :target: https://travis-ci.org/azavea/django-queryset-csv/

.. image:: https://coveralls.io/repos/azavea/django-queryset-csv/badge.svg?branch=master&service=github
   :target: https://coveralls.io/r/azavea/django-queryset-csv/

.. image:: https://img.shields.io/pypi/v/django-queryset-csv.svg
   :target: http://pypi.python.org/pypi/django-queryset-csv/

a CSV exporter for django querysets.

This tool was created out of repeatedly needing to do the following in django:

1. write CSV data that is based on simple querysets.
2. automatically encode unicode characters to utf-8
3. create a shortcut to render a queryset to a CSV HTTP response
4. add a time/datestamping mechanism to CSV filenames

For more detailed documentation, please read `this blog post. <http://www.azavea.com/blogs/labs/2014/03/exporting-django-querysets-to-csv/>`_

Installation
------------

Run::

   pip install django-queryset-csv

Supports Python 2.7 and 3.5, Django >= 1.8.

Usage
-----
Perform all filtering and field authorization in your view using ``.filter()`` and ``.values()``.
Then, use ``render_to_csv_response`` to turn a queryset into a response with a CSV attachment.
Pass it a ``QuerySet`` or ``ValuesQuerySet`` instance::

  from djqscsv import render_to_csv_response

  def csv_view(request):
    qs = Foo.objects.filter(bar=True).values('id', 'bar')
    return render_to_csv_response(qs)

If you need to write the CSV to a file you can use ``write_csv`` instead::

  from djqscsv import write_csv

  qs = Foo.objects.filter(bar=True).values('id', 'bar')
  with open('foo.csv', 'wb') as csv_file:
    write_csv(qs, csv_file)

Foreign keys
------------

Foreign keys are supported natively using ``ValuesQuerySet`` in Django. Simply use the ``__`` technique as you would in the Django ORM when you pass args to the ``.values()`` method.

models.py::

  from django.db import models

  class Food(models.Model):
      name = models.CharField(max_length=20)

  class Person(models.Model):
      name = models.CharField(max_length=20)
      favorite_food = models.ForeignKey(Food)

views.py::

  from djqscsv import render_to_csv_response

  def csv_view(request):
      people = Person.objects.values('name', 'favorite_food__name')
      return render_to_csv_response(people)

Keyword arguments
-----------------

This module exports two functions that write CSVs, ``render_to_csv_response`` and ``write_csv``. Both of these functions require their own positional arguments as documented above. In addition, they both take the following optional keyword arguments:

- ``field_header_map`` - (default: ``None``) A dictionary mapping names of model fields to column header names. If specified, the csv writer will use these column headers. Otherwise, it will use defer to other parameters for rendering column names.
- ``field_serializer_map`` - (default: ``{}``) A dictionary mapping names of model fields to functions that serialize them to text. For example, ``{'created': (lambda x: x.strftime('%Y/%m/%d')) }`` will serialize a datetime field called ``created``.
- ``use_verbose_names`` - (default: ``True``) A boolean determining whether to use the django field's ``verbose_name``, or to use it's regular field name as a column header. Note that if a given field is found in the ``field_header_map``, this value will take precendence.
- ``field_order`` - (default: ``None``) A list of fields to determine the sort order. This list need not be complete: any fields not specified will follow those in the list with the order they would have otherwise used.

In addition to the above arguments, ``render_to_csv_response`` takes the following optional keyword arguments:

- ``filename`` - (default: ``None``) A string used to set a filename in the ``Content-Disposition`` header as part of the returned ``HttpResponse``. If this is not passed, a filename will be automatically generated based on the table name of the QuerySet.
- ``append_datestamp`` - (default: ``False``) A boolean determining whether to append a timestamp as part of the filename set in the ``Content-Disposition`` header.
- ``streaming`` - (default: ``True``) A boolean determining whether to use ``StreamingHttpResponse`` instead of the normal ``HttpResponse``.

The remaining keyword arguments are *passed through* to the csv writer. For example, you can export a CSV with a different delimiter.

views.py::

  from djqscsv import render_to_csv_response

  def csv_view(request):
      people = Person.objects.values('name', 'favorite_food__name')
      return render_to_csv_response(people, delimiter='|')

For more details on possible arguments, see the documentation on `DictWriter <https://docs.python.org/2/library/csv.html#csv.DictWriter>`_.


Development and contributions
-----------------------------

Please read the included ``CONTRIBUTING.rst`` file.
