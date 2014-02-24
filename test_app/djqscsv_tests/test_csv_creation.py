from django.test import TestCase
from django.core.exceptions import ValidationError

from django import VERSION as DJANGO_VERSION

import csv
import itertools

from .context import djqscsv

from .context import SELECT, EXCLUDE, AS

from .models import Person

from .util import create_people_and_get_queryset

from django.utils import six

if six.PY3:
    from functools import filter
    from io import StringIO
else:
    from StringIO import StringIO

class CSVTestCase(TestCase):

    def setUp(self):
        self.qs = create_people_and_get_queryset()

    def assertMatchesCsv(self, csv_file, expected_data):
        csv_data = csv.reader(csv_file)
        iteration_happened = False
        is_first = True
        test_pairs = itertools.izip_longest(csv_data, expected_data,
                                            fillvalue=[])
        for csv_row, expected_row in test_pairs:
            if is_first:
                # add the BOM to the data
                expected_row = ['\xef\xbb\xbf' + expected_row[0]] + expected_row[1:]
                is_first = False
            iteration_happened = True
            self.assertEqual(csv_row, expected_row)

        self.assertTrue(iteration_happened, "The CSV does not contain data.")

    def assertQuerySetBecomesCsv(self, qs, expected_data, **kwargs):
        obj = StringIO()
        djqscsv.write_csv(qs, obj, **kwargs)
        csv_file = filter(None, obj.getvalue().split('\n'))
        self.assertMatchesCsv(csv_file, expected_data)

    def assertEmptyQuerySetMatches(self, expected_data, **kwargs):
        qs = self.qs.none()
        obj = StringIO()
        if DJANGO_VERSION[:2] == (1, 5):
            with self.assertRaises(djqscsv.CSVException):
                djqscsv.write_csv(qs, obj)
        elif DJANGO_VERSION[:2] == (1, 6):
            djqscsv.write_csv(qs, obj,
                              **kwargs)
            self.assertEqual(obj.getvalue(), expected_data)


    # the csv data that is returned by the most inclusive query under test.
    # use this data structure to build smaller data sets
    BASE_CSV = [
        ['id', 'name', 'address',
         'info', 'hobby_id', 'hobby__name', 'Most Powerful'],
        ['1', 'vetch', 'iffish', 'wizard', '1', 'Doing Magic', '0'],
        ['2', 'nemmerle', 'roke', 'deceased arch mage', '2', 'Resting', '1'],
        ['3', 'ged', 'gont', 'former arch mage', '2', 'Resting', '1']]

    FULL_PERSON_CSV_WITH_RELATED = SELECT(BASE_CSV,
                                          AS('id', 'ID'),
                                          AS('name', 'Person\'s name'),
                                          'address',
                                          AS('info', 'Info on Person'),
                                          'hobby_id',
                                          'hobby__name')

    FULL_PERSON_CSV = EXCLUDE(FULL_PERSON_CSV_WITH_RELATED,
                              'hobby__name')

    FULL_PERSON_CSV_NO_VERBOSE = EXCLUDE(BASE_CSV,
                                         'hobby__name',
                                         'Most Powerful')

    LIMITED_PERSON_CSV = SELECT(FULL_PERSON_CSV,
                                'Person\'s name', 'address', 'Info on Person')

    LIMITED_PERSON_CSV_NO_VERBOSE = SELECT(BASE_CSV,
                                           'name', 'address', 'info')


class WriteCSVDataNoVerboseNamesTests(CSVTestCase):

    def test_write_csv_full_no_verbose(self):
        self.assertQuerySetBecomesCsv(self.qs,
                                      self.FULL_PERSON_CSV_NO_VERBOSE,
                                      use_verbose_names=False)

    def test_write_csv_limited_no_verbose(self):
        qs = self.qs.values('name', 'address', 'info')
        self.assertQuerySetBecomesCsv(qs, self.LIMITED_PERSON_CSV_NO_VERBOSE,
                                          use_verbose_names=False)

    def test_empty_queryset_no_verbose(self):
        self.assertEmptyQuerySetMatches(
            '\xef\xbb\xbfid,name,address,info,hobby_id\r\n',
            use_verbose_names=False)


class WriteCSVDataTests(CSVTestCase):

    def test_write_csv_full(self):
        self.assertQuerySetBecomesCsv(self.qs, self.FULL_PERSON_CSV)

    def test_write_csv_limited(self):
        qs = self.qs.values('name', 'address', 'info')
        self.assertQuerySetBecomesCsv(qs, self.LIMITED_PERSON_CSV)

    def test_empty_queryset(self):
        self.assertEmptyQuerySetMatches(
            '\xef\xbb\xbfID,Person\'s name,address,'
            'Info on Person,hobby_id\r\n')

class FieldHeaderMapTests(CSVTestCase):
    def test_write_csv_full_custom_headers(self):
        overridden_info_csv = ([['ID', "Person's name", 'address',
                               'INFORMATION', 'hobby_id']] +
                               self.FULL_PERSON_CSV[1:])

        self.assertQuerySetBecomesCsv(
            self.qs, overridden_info_csv,
            field_header_map={'info': 'INFORMATION'})

    def test_write_csv_limited_custom_headers(self):
        overridden_info_csv = SELECT(self.LIMITED_PERSON_CSV,
                                     "Person's name", 'address',
                                     AS('Info on Person', 'INFORMATION'))
        qs = self.qs.values('name', 'address', 'info')

        self.assertQuerySetBecomesCsv(
            qs, overridden_info_csv,
            field_header_map={ 'info': 'INFORMATION' })


    def test_write_csv_with_related_custom_headers(self):
        overridden_csv = SELECT(self.FULL_PERSON_CSV_WITH_RELATED,
                                'ID', "Person's name",
                                AS('hobby__name', 'Name of Activity'))
        qs = self.qs.values('id', 'name', 'hobby__name')

        self.assertQuerySetBecomesCsv(
            qs, overridden_csv,
            field_header_map={ 'hobby__name': 'Name of Activity' })

    def test_empty_queryset_custom_headers(self):
        self.assertEmptyQuerySetMatches(
            '\xef\xbb\xbfID,Person\'s name,address,INFORMATION,hobby_id\r\n',
            field_header_map={ 'info': 'INFORMATION' })


class WalkRelationshipTests(CSVTestCase):

    def test_with_related(self):

        qs = self.qs.values('id', 'name', 'address', 'info',
                            'hobby_id', 'hobby__name')

        self.assertQuerySetBecomesCsv(qs, self.FULL_PERSON_CSV_WITH_RELATED)


class OrderingTests(CSVTestCase):

    def setUp(self):
        self.qs = create_people_and_get_queryset().extra(
            select={'Most Powerful':"info LIKE '%arch mage%'"})

    def test_extra_select(self):
        csv_with_extra = SELECT(self.BASE_CSV,
                                AS('id', 'ID'),
                                AS('name', "Person's name"),
                                'address',
                                AS('info', 'Info on Person'),
                                'hobby_id',
                                'Most Powerful')

        self.assertQuerySetBecomesCsv(self.qs, csv_with_extra)


    def test_extra_select_ordering(self):
        custom_order_csv = SELECT(self.BASE_CSV,
                                  AS('id', 'ID'),
                                  'Most Powerful',
                                  AS('name', "Person's name"),
                                  'address',
                                  AS('info', 'Info on Person'),
                                  'hobby_id')

        self.assertQuerySetBecomesCsv(self.qs, custom_order_csv,
                                      field_order=['id', 'Most Powerful'])

class RenderToCSVResponseTests(CSVTestCase):

    def test_render_to_csv_response_with_filename_and_datestamp(self):
        filename = "the_reach.csv"

        response = djqscsv.render_to_csv_response(self.qs,
                                                  filename=filename,
                                                  append_datestamp=True)

        self.assertRegexpMatches(
            response['Content-Disposition'],
            r'attachment; filename=the_reach_[0-9]{8}.csv;')

    def test_render_to_csv_response_no_filename(self):
        response = djqscsv.render_to_csv_response(self.qs,
                                                  use_verbose_names=False)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertMatchesCsv(response.content.split('\n'),
                              self.FULL_PERSON_CSV_NO_VERBOSE)

        self.assertRegexpMatches(response['Content-Disposition'],
                                 r'attachment; filename=person_export.csv;')


    def test_render_to_csv_response(self):
        response = djqscsv.render_to_csv_response(self.qs,
                                                  filename="test_csv",
                                                  use_verbose_names=False)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertMatchesCsv(response.content.split('\n'),
                              self.FULL_PERSON_CSV_NO_VERBOSE)

