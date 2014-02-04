from django.test import TestCase
from django.core.exceptions import ValidationError

from django import VERSION as DJANGO_VERSION

import csv
import itertools

from .context import djqscsv

from .models import Person

from .util import create_people_and_get_queryset

from django.utils import six

if six.PY3:
    from functools import filter
    from io import StringIO
else:
    from StringIO import StringIO


class ValidateCleanFilenameTests(TestCase):

    def assertValidatedEquals(self, filename, expected_value):
        validated = djqscsv._validate_and_clean_filename(filename)
        self.assertEqual(validated, expected_value)

    def test_validate_no_dots(self):
        self.assertValidatedEquals('karg', 'karg.csv')

    def test_validate_multiple_dots_csv(self):
        self.assertValidatedEquals('hort.town.csv',
                                   'horttown.csv')

    def test_validate_regular_csv(self):
        self.assertValidatedEquals('roke-knoll.csv',
                                   'roke-knoll.csv')

    def test_non_csv_raises(self):
        self.assertRaises(ValidationError,
                          djqscsv._validate_and_clean_filename,
                          'gont.island')

    def test_non_csv_raises_2(self):
        self.assertRaises(ValidationError,
                          djqscsv._validate_and_clean_filename,
                          'gont.csv.island')


class SanitizeUnicodeRecordTests(TestCase):
    def test_sanitize(self):
        record = {'name': 'Tenar',
                  'nickname': u'\ufeffThe White Lady of Gont'}
        sanitized = djqscsv._sanitize_unicode_record(record)
        self.assertEqual(sanitized,
                         {'name': 'Tenar',
                          'nickname': '\xef\xbb\xbfThe White Lady of Gont'})


class AppendDatestampTests(TestCase):

    def test_clean_returns(self):
        filename = "the_reach.csv"
        stamped = djqscsv._append_datestamp(filename)
        self.assertRegexpMatches(stamped, r'the_reach_[0-9]{8}.csv')

    def test_no_extension_raises(self):
        filename = "iffish"
        self.assertRaises(ValidationError,
                          djqscsv._append_datestamp,
                          filename)

    def test_unclean_extension_raises(self):
        filename = "hort.town"
        self.assertRaises(ValidationError,
                          djqscsv._append_datestamp,
                          filename)


class GenerateFilenameTests(TestCase):
    def test_generate_filename(self):
        qs = create_people_and_get_queryset()

        self.assertEqual(djqscsv.generate_filename(qs),
                         'person_export.csv')

        self.assertRegexpMatches(djqscsv.generate_filename(qs, True),
                                 r'person_export_[0-9]{8}.csv')


class CSVTestCase(TestCase):

    def assertMatchesCsv(self, csv_file, expected_data):
        csv_data = csv.reader(csv_file)
        iteration_happened = False
        test_pairs = itertools.izip_longest(csv_data, expected_data,
                                            fillvalue=[])
        for csv_row, expected_row in test_pairs:
            iteration_happened = True
            self.assertEqual(csv_row, expected_row)

        self.assertTrue(iteration_happened, "The CSV does not contain data.")

    BIGGEST_POSSIBLE_CSV = [
            ['\xef\xbb\xbfID', 'Person\'s name', 'address',
             'Info on Person', 'Most Powerful'],
            ['1', 'vetch', 'iffish', 'wizard', '0'],
            ['2', 'nemmerle', 'roke', 'deceased arch mage', '1'],
            ['3', 'ged', 'gont', 'former arch mage', '1']]


class WriteCSVDataTests(CSVTestCase):

    def setUp(self):
        self.qs = create_people_and_get_queryset()

        self.full_verbose_csv = [row[:-1] for row in CSVTestCase.BIGGEST_POSSIBLE_CSV]

        self.full_csv = ([['\xef\xbb\xbfid', 'name', 'address', 'info']] +
                         self.full_verbose_csv[1:])

        self.limited_verbose_csv = (
            [['\xef\xbb\xbfPerson\'s name', 'address', 'Info on Person']] +
            [row[1:] for row in self.full_verbose_csv[1:]])

        self.limited_csv = (
            [['\xef\xbb\xbfname', 'address', 'info']] +
            self.limited_verbose_csv[1:])

    def test_write_csv_full_terse(self):
        obj = StringIO()
        djqscsv.write_csv(self.qs, obj, use_verbose_names=False)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.full_csv)

    def test_write_csv_full_verbose(self):
        obj = StringIO()
        djqscsv.write_csv(self.qs, obj)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.full_verbose_csv)

    def test_write_csv_limited_terse(self):
        qs = self.qs.values('name', 'address', 'info')
        obj = StringIO()
        djqscsv.write_csv(qs, obj, use_verbose_names=False)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.limited_csv)

    def test_write_csv_limited_verbose(self):
        qs = self.qs.values('name', 'address', 'info')
        obj = StringIO()
        djqscsv.write_csv(qs, obj)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.limited_verbose_csv)

    def test_render_to_csv_response_with_filename_and_datestamp(self):
        filename = "the_reach.csv"

        response = djqscsv.render_to_csv_response(self.qs,
                                                  filename=filename,
                                                  append_datestamp=True)

        self.assertRegexpMatches(response['Content-Disposition'],
                                 r'attachment; filename=the_reach_[0-9]{8}.csv;')

    def test_render_to_csv_response_no_filename(self):
        response = djqscsv.render_to_csv_response(self.qs,
                                                  use_verbose_names=False)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertMatchesCsv(response.content.split('\n'),
                              self.full_csv)

        self.assertRegexpMatches(response['Content-Disposition'],
                                 r'attachment; filename=person_export.csv;')


    def test_render_to_csv_response(self):
        response = djqscsv.render_to_csv_response(self.qs,
                                                  filename="test_csv",
                                                  use_verbose_names=False)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertMatchesCsv(response.content.split('\n'),
                              self.full_csv)

    def test_empty_queryset(self):
        qs = self.qs.none()
        obj = StringIO()
        if DJANGO_VERSION[:2] == (1, 5):
            with self.assertRaises(djqscsv.CSVException):
                djqscsv.write_csv(qs, obj)
        elif DJANGO_VERSION[:2] == (1, 6):
            djqscsv.write_csv(qs, obj, use_verbose_names=False)
            self.assertEqual(obj.getvalue(),
                             '\xef\xbb\xbfid,name,address,info\r\n')


class OrderingTests(CSVTestCase):
    def setUp(self):
        self.qs = create_people_and_get_queryset().extra(
            select={'Most Powerful':"info LIKE '%arch mage%'"})

        self.csv_with_extra = CSVTestCase.BIGGEST_POSSIBLE_CSV

        self.custom_order_csv = [[row[0], row[4]] + row[1:4]
                                 for row in self.csv_with_extra]

    def test_extra_select(self):
        obj = StringIO()
        djqscsv.write_csv(self.qs, obj)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.csv_with_extra)

    def test_extra_select_ordering(self):
        obj = StringIO()
        djqscsv.write_csv(self.qs, obj, field_order=['id', 'Most Powerful'])
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, self.custom_order_csv)

