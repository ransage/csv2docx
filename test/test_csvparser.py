from csv2docx import CsvParser, MySettings, JsonError, CrossRefError, utils
import unittest
from sys import stderr as err
import os
import csv
import inspect

THIS_FOLDER = os.path.abspath(os.path.dirname(__file__))

JSON_FILE = os.path.join(THIS_FOLDER, 'test_settings.json')
DEFAULT_INPUT_FILE = 'input.csv'
DEFAULT_OUTPUT_FILE = 'output.csv'

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

# TODO: make delimeter and quotechar json settings
def build_ref_dict(filename):
    ref_dict = {}
    with open(filename,'U') as csvfile:
        delim = ','
        reader = csv.reader(csvfile, delimiter=delim, quotechar='"')
        for row in reader:
            if len(row):
                id = utils.int_repr(row[0])
                if id == None:
                    continue
                ref_dict[id] = row
            # end if
        # end for
    # end with
    return ref_dict
# end build_ref_dict



class TestParser(unittest.TestCase):
  
    def setUp(self):
        self.s = MySettings()
        self.s.read_json_file(JSON_FILE)
        self.s.INPUT_FILE = DEFAULT_INPUT_FILE
        self.s.OUTPUT_FILE = DEFAULT_OUTPUT_FILE
        
        self.ref_dict = build_ref_dict(self.s.INPUT_FILE)
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
    # end setUp

    def tearDown(self):
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

    def test_parse_token_throws_if_key_not_found(self): 
        
        large_num = 99999
        with self.assertRaises( CrossRefError ):
            test_token = (self.s.l_delim + self.s.heading_text_symbol + str(large_num) + self.s.r_delim)
            result = self.parser.parse_token(test_token)
            
        

    def test_parse_token(self):
        header_dict = self.parser.build_header_dict()
        self.assertTrue(len(header_dict) > 1, 
                        'Constructed header_dict does not have >1 entries')
        self.parser.header_dict = header_dict
        for key in header_dict.keys():
            for code in (self.s.heading_number_symbol,self.s.heading_text_symbol):
                test_token = (self.s.l_delim +
                            code +
                            str(key) +
                            self.s.r_delim)
                # try:
                result = self.parser.parse_token(test_token)
                # if len(result.value):
                #    err.write ( '%s: %s\n' % (test_token, result.value) )
                if len(self.ref_dict[key]) > code:
                    self.assertEqual(result.value, self.ref_dict[key][code])
                #except CrossRefError as ex:
                #    err.write ( '%s: %s\n' % (test_token, ex.message) )
                #    break
            # end for
        # end for
    # end test_parse_token 
    
    def test_parse_string_with_token(self):
        header_dict = self.parser.build_header_dict()
        self.assertTrue(len(header_dict) > 1, 
                        'Constructed header_dict does not have >1 entries')
        self.parser.header_dict = header_dict
        text = ('Text after second heading reference to section {#7}, {H7} '+
                '(1.1, H2) and to section {#9},{H9} (1.1.1.1, H4)')
        expected_subst_text = (text.replace('{#7}', '1.1').replace('{H7}','H2')
                               ).replace('{#9}','1.1.1.1').replace('{H9}','H4')
        subst_text = ''.join(self.parser.replace_cross_refs(text, None))
        self.assertEqual(expected_subst_text, subst_text, 
                         ("Failed to get expected subst_text in %s" % 
                          inspect.stack()[0][3]))
    #end test_parse_string_with_token
    
    def test_parse_string_with_token_incl_image(self):
        header_dict = self.parser.build_header_dict()
        self.assertTrue(len(header_dict) > 1, 
                        'Constructed header_dict does not have >1 entries')
        self.parser.header_dict = header_dict
        text = ('Text with {bad_text} and reference to section {#7}, {H7} '+
                '(1.1, H2) and to section {#9},{H9} (1.1.1.1, H4)')
        expected_subst_text = (text.replace('{#7}', '1.1').replace('{H7}','H2')
                               ).replace('{#9}','1.1.1.1').replace('{H9}','H4')
        subst_list = self.parser.replace_cross_refs(text, None)
        
        subst_list_image_ignored = []
        for entry in subst_list:
            if isinstance(entry, CsvParser.ParsedToken):
                subst_list_image_ignored.append(self.s.l_delim +
                                                entry.value + 
                                                self.s.r_delim)
            else:
                subst_list_image_ignored.append(entry)

        subst_text = ''.join(subst_list_image_ignored)
        self.assertEqual(expected_subst_text, subst_text, 
                         ("Failed to get expected subst_text in %s" % 
                          inspect.stack()[0][3]))
    #end test_parse_string_with_token
# end TestParser
