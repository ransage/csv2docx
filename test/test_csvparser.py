from csv2docx import CsvParser, MySettings, JsonError
import unittest
from sys import stderr as err
import os

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

JSON_FILE = os.path.join(THIS_FOLDER, 'test_settings.json')

CSV_AS_STRING = '''ID,???,HeadingLevel,HeadingNumber,Heading,Body
0,,,,,text in front of first heading...
1,,1,1.,H1,
2,,,,,Text after first heading
7,,2,1.1,H2,
6,,,,,"Text after second heading reference to section {#7}, {H7} (1.1, H2) and to section {#9},{H9} (1.1.1.1, H4)"
3,,3,1.1.1,H3,
8,,,,,Text after third heading
9,,4,1.1.1.1,H4,
14,,,,,{test/images/480px-Smiley.svg.png}
24,,,,,Text after fourth heading
34,,,,,"Here is an image, {test/images/240px-Smiley.svg.png}, which I am attempting to put inline with a paragraph"
23,,1,2.,If you don't see the images,
21,,2,2.1,you may be encountering the relative path bug,
'''

class TestCleanBackslashR(unittest.TestCase):
    
    def setUp(self):
        print '__setup__'
        self.s = MySettings()
        self.s.read_json_file(JSON_FILE)
        self.parser = CsvParser(self.s)
        self.clean_row = ['6',
               '',
               '',
               '',
               '',
               'Text after second heading reference to section {#7}, {H7} (1.1, H2) and to section {#9},{H9} (1.1.1.1, H4)',
           ]

        self.slashed_row = ['6',
               '',
               '',
               '',
               '',
               'Text after\r second heading reference\r to section {#7}, {H7} (1.1, H2) and\r to section {#9},{H9} (1.1.1.1, H4)',
           ]

        #err.write('\nTestParse_setup...')

    def tearDown(self):
        #err.write('.TestParse_teardown...')
        pass



    def test_read_json_file(self):
        json_dict = self.s.json_file_to_dict(JSON_FILE)
        for key in json_dict.keys():
            self.assertTrue(hasattr(self.s,key),
                            msg='Testing key: %s'%key)

    #err.write((self.slashed_row[:]).__str__())

    def test_dont_change_if_no_indices(self):
        self.s.indices_to_replace_backslash_r = []
        cleaned_row = self.parser.clean_backslash_r(self.slashed_row[:])
        self.assertEqual(self.slashed_row,cleaned_row)

    def test_dont_change_if_no_index_setting(self):
        #err.write(self.s.__dict__)
        delattr(self.s,'indices_to_replace_backslash_r')
        cleaned_row = self.parser.clean_backslash_r(self.slashed_row[:])
        self.assertEqual(self.slashed_row,cleaned_row)

    def test_raises_if_index_but_no_paired_field(self):
        self.parser.s.indices_to_replace_backslash_r = [4, 5]
        attr_to_delete = 'replace_backslash_r_with'
        delattr(self.parser.s,attr_to_delete)

        # Confirm deleted before testing
        self.assertFalse(hasattr(self.parser.s,attr_to_delete))
        with self.assertRaises( JsonError ):
            self.parser.clean_backslash_r(self.slashed_row[:])

    def test_raises_if_non_integer_index(self):
        self.parser.s.indices_to_replace_backslash_r = [4,'a']
        with self.assertRaises( JsonError ):
            self.parser.clean_backslash_r(self.slashed_row[:])

    def test_raises_if_index_greater_than_length(self):
        self.parser.s.indices_to_replace_backslash_r = [4,27]
        with self.assertRaises( JsonError ):
            self.parser.clean_backslash_r(self.slashed_row[:])

    def test_raises_if_index_less_than_negative_length(self):
        self.parser.s.indices_to_replace_backslash_r = [-4,-27]
        with self.assertRaises( JsonError ):
            self.parser.clean_backslash_r(self.slashed_row[:])

    def test_dont_change_clean_row(self):
        cleaned_row = self.parser.clean_backslash_r(self.clean_row[:])
        self.assertEqual(self.clean_row[:],cleaned_row)

    def test_changes_backslash(self):
        # err.write("Replace indices %s\n" % str(self.parser.s.indices_to_replace_backslash_r))
        # err.write("Replace with (in ||): |%s|\n" % self.parser.s.replace_backslash_r_with)
        cleaned_row = self.parser.clean_backslash_r(self.slashed_row[:], True)
        # err.write("\n"+"\n".join(cleaned_row))
        err.write("\nTODO: add better testing of \\r cleanup\n")
        self.assertNotEqual(self.slashed_row,cleaned_row)
