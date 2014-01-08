import csv
import datetime

from django.core.exceptions import ValidationError
from django.templatetags.l10n import localize
from django.utils.text import slugify
from django.http import HttpResponse

from django.conf import settings
if not settings.configured:
    # required to import ValuesQuerySet
    settings.configure()

from django.db.models.query import ValuesQuerySet

""" A simple python package for turning django models into csvs """


class CSVException(Exception):
    pass


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


    """
    """

def _write_csv_data(queryset, file_obj):

    # add BOM to suppor CSVs in MS Excel
    file_obj.write(u'\ufeff'.encode('utf8'))

    # the CSV must always be built from a values queryset
    # in order to introspect the necessary fields.
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


def generate_filename(queryset, append_datestamp=False):
    """
    Takes a queryset and returns a default
    base filename based on the underlying model
    """
    base_filename = slugify(unicode(queryset.model.__name__)) + '_export.csv'

    if append_datestamp:
        base_filename = _append_datestamp(base_filename)

    return base_filename

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
            return localize(value)

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
    return '%s_%s.csv' % (filename[:-4], formatted_datestring)
