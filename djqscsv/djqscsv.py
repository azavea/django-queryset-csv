import csv
import datetime
import re
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.http import HttpResponse
from django.db.models.query import ValuesQuerySet
from tempfile import TemporaryFile
from cStringIO import StringIO
""" A simple python package for turning django models into csvs """

########################################
# public functions
########################################

def render_to_csv_response(queryset, filename=None, append_timestamp=False):
    """
    provides the boilerplate for making a CSV http response.
    takes a filename or generates one from the queryset's model.
    """

    if not filename:
        filename = generate_filename(queryset)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s;' % filename
    response['Cache-Control'] = 'no-cache'

    _write_csv_data(queryset, response)

    return response

def create_csv(queryset, in_memory=False):
    """
    Takes a queryset and returns a file-like object of CSV data.
    """
    if in_memory:
        csv_file = StringIO()
    else:
        csv_file = TemporaryFile()

    _write_csv_data(queryset, csv_file)

    return csv_file

def generate_filename(queryset, append_timestamp=False):
    """
    Takes a queryset and returns a default
    base filename based on the underlying model
    """
    base_filename = slugify(unicode(queryset.model.__name__)) + 'export'

    if append_timestamp:
        base_filename = _timestamp_filename(base_filename)

    return base_filename + '.csv'


########################################
# queryset reader/csv writer functions
########################################

class CSVException(Exception):
    pass

def _write_csv_data(queryset, file_obj, verbose_field_names=None):
    if isinstance(queryset, ValuesQuerySet):
        values_qs = queryset
    else:
        values_qs = queryset.values()

    try:
        header_row = values_qs.field_names
    except AttributeError:
        raise CSVException("Empty queryset provided to exporter.")

    writer = csv.DictWriter(file_obj, header_row)
    writer.writeheader()

    for record in values_qs:
        record = _sanitize_unicode_record(record)
        writer.writerow(record)

########################################
# utility functions
########################################

def _validate_and_clean_filename(filename):

    if filename.count('.'):
        if not filename.endswith('.csv'):
            raise ValidationError('the only accepted file extension is .csv')
        else:
            filename = filename[:-4]

    filename = slugify(filename)
    return filename

def _sanitize_unicode_record(record):
    obj = {}
    for key, val in record.iteritems():
        if val:
            if isinstance(val, unicode):
                newval = val.encode("utf-8")
            else:
                newval = str(val)
            obj[key] = newval
    return obj

def _timestamp_filename(filename):
    """
    takes a filename and returns a new filename with the
    current formatted date appended to it.

    raises an exception if it receives a filename with an exception.
    validation/preprocessing must be called separately.
    """
    if filename != _validate_and_clean_filename:
        raise ValidationError('cannot timestamp unvalidated filename')
    
    formatted_datestring = datetime.date.today().strftime("%Y%m%d")
    return '%s_%s' % (filename, formatted_datestring)

