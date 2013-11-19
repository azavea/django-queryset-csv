from unittest import TestCase, main
from django.core.exceptions import ValidationError

from context import djqscsv

from utils import Person, MockQuerySet

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
        record = {'name': 'Ged',
                  'nickname': u'\ufeffSparrowhawk'}
        sanitized = djqscsv._sanitize_unicode_record(record)
        self.assertEqual(sanitized,
                         {'name': 'Ged',
                          'nickname': '\xef\xbb\xbfSparrowhawk'})


    

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
        people = [Person('vetch', 'iffish', 'wizard'),
                  Person('nemmerle', 'roke', 'arch mage')]

        qs = MockQuerySet(people)

        self.assertEqual(djqscsv.generate_filename(qs),
                         'person_export.csv')

        self.assertRegexpMatches(djqscsv.generate_filename(qs, True),
                                 r'person_export_[0-9]{8}.csv')


if __name__ == '__main__':
    main()
