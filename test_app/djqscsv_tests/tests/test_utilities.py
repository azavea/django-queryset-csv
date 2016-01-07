# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.core.exceptions import ValidationError

from djqscsv_tests.context import djqscsv

from djqscsv_tests.util import create_people_and_get_queryset

# Test the various helper functions that assist the
# csv creation process, but don't participate in it
# directly.


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
        sanitized = djqscsv._sanitize_unicode_record({}, record)
        self.assertEqual(sanitized,
                         {'name': 'Tenar',
                          'nickname': b'\xef\xbb\xbfThe White Lady of Gont'.decode('utf-8')})

    def test_sanitize_date(self):
        record = {'name': 'Tenar',
                  'created': datetime.datetime(1, 1, 1)}
        sanitized = djqscsv._sanitize_unicode_record({}, record)
        self.assertEqual(sanitized,
                         {'name': 'Tenar',
                          'created': '0001-01-01T00:00:00'})

    def test_sanitize_date_with_non_string_formatter(self):
        """
        This test is only to make sure an edge case provides a sane
        default and works as expected. It is not recommended to follow
        this practice.
        """
        record = {'name': 'Tenar'}
        serializer = {'name': lambda d: len(d)}
        sanitized = djqscsv._sanitize_unicode_record(serializer, record)
        self.assertEqual(sanitized, {'name': b'5'})

    def test_sanitize_date_with_formatter(self):
        record = {'name': 'Tenar',
                  'created': datetime.datetime(1973, 5, 13)}
        serializer = {'created': lambda d: d.strftime('%Y-%m-%d')}
        sanitized = djqscsv._sanitize_unicode_record(serializer, record)
        self.assertEqual(sanitized,
                         {'name': 'Tenar',
                          'created': '1973-05-13'})

    def test_sanitize_date_with_bad_formatter(self):
        record = {'name': 'Tenar',
                  'created': datetime.datetime(1973, 5, 13)}
        formatter = lambda d: d.day
        with self.assertRaises(AttributeError):
            djqscsv._sanitize_unicode_record(formatter, record)


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


class SafeUtf8EncodeTest(TestCase):
    def test_safe_utf8_encode(self):

        class Foo(object):
            def __str__(self):
                return u'¯\_(ツ)_/¯'
            def __str_(self):
                return self.__str__().encode('utf-8')
        for val in (u'¯\_(ツ)_/¯', 'plain', r'raw',
                    b'123', 11312312312313, False,
                    datetime.datetime(2001, 1, 1),
                    4, None, [], set(), Foo):

            first_pass = djqscsv._safe_utf8_stringify(val)
            second_pass = djqscsv._safe_utf8_stringify(first_pass)
            third_pass = djqscsv._safe_utf8_stringify(second_pass)
            self.assertEqual(first_pass, second_pass)
            self.assertEqual(second_pass, third_pass)
            self.assertEqual(type(first_pass), type(third_pass))
