import csv
import datetime
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


def render_to_csv_response(queryset, filename=None, append_datestamp=False):
    """
    provides the boilerplate for making a CSV http response.
    takes a filename or generates one from the queryset's model.
    """
    if filename:
        filename = _validate_and_clean_filename(filename)
        if append_datestamp:
            filename = _append_datestamp(filename)
    else:
        filename = generate_filename(queryset,
                                     append_datestamp=append_datestamp)

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


def generate_filename(queryset, append_datestamp=False):
    """
    Takes a queryset and returns a default
    base filename based on the underlying model
    """
    base_filename = slugify(unicode(queryset.model.__name__)) + 'export'

    if append_datestamp:
        base_filename = _datestamp_filename(base_filename)

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

    filename = slugify(unicode(filename)) + '.csv'
    return filename


def _sanitize_unicode_record(record):

    def _sanitize_value(value):
        if isinstance(val, unicode):
            return value.encode("utf-8")
        else:
            return str(value)

    obj = {}
    for key, val in record.iteritems():
        if val:
            obj[_sanitize_value(key)] = _sanitize_value(val)

    return obj


def _append_datestamp(filename):
    """
    takes a filename and returns a new filename with the
    current formatted date appended to it.

    raises an exception if it receives an unclean filename.
    validation/preprocessing must be called separately.
    """
    if filename != _validate_and_clean_filename(filename):
        raise ValidationError('cannot datestamp unvalidated filename')

    formatted_datestring = datetime.date.today().strftime("%Y%m%d")
    return '%s_%s.csv' % (filename[:-3], formatted_datestring)
