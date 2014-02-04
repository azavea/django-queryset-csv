import csv
import datetime

from django.core.exceptions import ValidationError
from django.templatetags.l10n import localize
from django.utils.text import slugify
from django.http import HttpResponse

from django.conf import settings
if not settings.configured:
    # required to import ValuesQuerySet
    settings.configure() # pragma: no cover

from django.db.models.query import ValuesQuerySet

from django.utils import six

""" A simple python package for turning django models into csvs """


class CSVException(Exception):
    pass


def render_to_csv_response(queryset, filename=None, append_datestamp=False,
                           field_header_map=None, use_verbose_names=True,
                           field_order=None):
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

    write_csv(queryset, response, field_header_map, use_verbose_names, field_order)

    return response


def write_csv(queryset, file_obj, field_header_map=None,
              use_verbose_names=True, field_order=None):
    """
    The main worker function. Writes CSV data to a file object based on the
    contents of the queryset.
    """

    # add BOM to suppor CSVs in MS Excel
    file_obj.write(u'\ufeff'.encode('utf8'))

    # the CSV must always be built from a values queryset
    # in order to introspect the necessary fields.
    if isinstance(queryset, ValuesQuerySet):
        values_qs = queryset
    else:
        values_qs = queryset.values()

    try:
        field_names = values_qs.field_names

    except AttributeError:
        # in django1.5, empty querysets trigger
        # this exception, but not django 1.6
        raise CSVException("Empty queryset provided to exporter.")

    extra_columns = list(values_qs.query.extra_select)
    if extra_columns:
        field_names += extra_columns

    if field_order:
        # go through the field_names and put the ones
        # that appear in the ordering list first
        field_names = ([field for field in field_order
                       if field in field_names] +
                       [field for field in field_names
                        if field not in field_order])


    writer = csv.DictWriter(file_obj, field_names)

    # verbose_name defaults to the raw field name, so in either case
    # this will produce a complete mapping of field names to column names
    name_map = {field: field for field in field_names}
    if use_verbose_names:
        name_map.update({field.name: unicode(field.verbose_name)
                         for field in queryset.model._meta.fields
                         if field.name in field_names})

    # merge the custom field headers into the verbose/raw defaults, if provided
    _field_header_map = field_header_map or {}
    merged_header_map = name_map.copy()
    merged_header_map.update(_field_header_map)
    if extra_columns:
        merged_header_map.update({k: k for k in extra_columns})
    writer.writerow(merged_header_map)

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
    for key, val in six.iteritems(record):
        if val is not None:
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
