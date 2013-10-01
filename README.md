django-queryset-csv
===================

a CSV exporter for django querysets.

This tool was created out of repeatedly needing to do the following in django:

1. write CSV data that is based on single-table querysets.
2. automatically encode unicode characters to utf-8
3. create a shortcut to render a queryset to a CSV HTTP response

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
## todo

django-queryset-csv will be ready for stable release when the following are complete:

1. unit test coverage reaches 100%
2. test coverage is tracked by a CI server
3. custom column headers are supported (currently column headers are always field names)
4. model methods and foreign key field values are supported (or a decision is made not to)
5. CSV files are viewable in M$ Excel, which may require modifying the first few bytes of the file.
6. the package is uploaded to pypi.
