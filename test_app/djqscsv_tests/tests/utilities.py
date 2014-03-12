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


