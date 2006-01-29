# encoding: utf-8

import unittest
import syck

import warnings

STRINGS = [
    ("John Cage", 'tag:yaml.org,2002:str'),
    ("Béla Bartók", 'tag:python.yaml.org,2002:str'),
    ("Валентин Сильвестров", 'tag:python.yaml.org,2002:str'),
    (''.join([chr(k) for k in range(256)]), 'tag:yaml.org,2002:binary')
]

UNICODE_STRINGS = [
    (u"John Cage", 'tag:python.yaml.org,2002:unicode'),
    (u"Béla Bartók", 'tag:yaml.org,2002:str'),
    (u"Валентин Сильвестров", 'tag:yaml.org,2002:str'),
    (u''.join([unichr(k) for k in range(512)]), 'tag:yaml.org,2002:str')
]

DOCUMENT = """
- John Cage
- Béla Bartók
- Валентин Сильвестров
- \x80\x81\x82\x83\x84\x85\x86\x87
""", ["John Cage", u"Béla Bartók", u"Валентин Сильвестров", '\x80\x81\x82\x83\x84\x85\x86\x87']


class TestUnicode(unittest.TestCase):

    def testDumpStr(self):
        for string, tag in STRINGS:
            #print string
            document = syck.dump(string)
            #print document
            new_tag = syck.parse(document).tag
            new_string = syck.load(document)
            self.assertEqual(string, new_string)
            self.assertEqual(type(string), type(new_string))
            self.assertEqual(tag, new_tag)

    def testDumpUnicode(self):
        for string, tag in UNICODE_STRINGS:
            #print string
            document = syck.dump(string)
            #print document
            new_tag = syck.parse(document).tag
            new_string = syck.load(document)
            self.assertEqual(string, new_string)
            self.assertEqual(type(string), type(new_string))
            self.assertEqual(tag, new_tag)

    def testLoad(self):
        self._testWarning()
        document, values = DOCUMENT
        new_values = syck.load(document)
        for string, new_string in zip(values, new_values):
            self.assertEqual(string, new_string)
            self.assertEqual(type(string), type(new_string))

    def _testWarning(self):
        warnings.simplefilter('error')
        document = '\x80\x81\x82\x83\x84\x85\x86\x87'
        self.assertRaises(syck.NotUnicodeInputWarning, lambda: syck.load(document))
        warnings.resetwarnings()


