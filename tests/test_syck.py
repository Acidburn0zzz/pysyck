
import unittest
import _syck, syck
import StringIO

EXAMPLE = """
-
  avg: 0.278
  hr: 65
  name: Mark McGwire
-
  avg: 0.288
  hr: 63
  name: Sammy Sosa
"""

INVALID = """
 - invalid
- document
""", 2, 0

COMPARE1 = """
one: foo
two: bar
three: baz
""", {
    'one': 'foo',
    'two': 'bar',
    'three': 'baz',
}

COMPARE2 = """
- Mark McGwire
- Sammy Sosa
- Ken Griffey
""", [
    'Mark McGwire',
    'Sammy Sosa',
    'Ken Griffey',
]

COMPARE3 = """
american:
  - Boston Red Sox
  - Detroit Tigers
  - New York Yankees
national:
  - New York Mets
  - Chicago Cubs
  - Atlanta Braves
""", {
    'american': [
        'Boston Red Sox',
        'Detroit Tigers',
        'New York Yankees',
    ],
    'national': [
        'New York Mets',
        'Chicago Cubs',
        'Atlanta Braves',
    ],
}

DOCUMENTS0 = ""

DOCUMENTS1 = """
---
Time: 2001-11-23 15:01:42 -05:00
User: ed
Warning: >
  This is an error message
  for the log file
"""

DOCUMENTS2 = """
---
Time: 2001-11-23 15:01:42 -05:00
User: ed
Warning: >
  This is an error message
  for the log file
---
Time: 2001-11-23 15:02:31 -05:00
User: ed
Warning: >
  A slightly different error
  message.
"""

DOCUMENTS3 = """
---
Time: 2001-11-23 15:01:42 -05:00
User: ed
Warning: >
  This is an error message
  for the log file
---
Time: 2001-11-23 15:02:31 -05:00
User: ed
Warning: >
  A slightly different error
  message.
---
Date: 2001-11-23 15:03:17 -05:00
User: ed
Fatal: >
  Unknown variable "bar"
Stack:
  - file: TopClass.py
    line: 23
    code: |
      x = MoreObject("345\\n")
  - file: MoreClass.py
    line: 58
    code: |-
      foo = bar
"""

IMPLICIT_TYPING = """
- 'foo'
- >-
  bar
- baz
- 123
- 3.14
- true
- false
- []
- {}
""", [
    ('str', True),
    ('str', True),
    ('str', False),
    ('int', False),
    ('float#fix', False),
    ('bool#yes', False),
    ('bool#no', False),
    (None, False),
    (None, False),
]

EXPLICIT_TYPING = """
- !int '123'
- !yamltype 'foo'
- !python/type 'bar'
- !domain.tld,2002/type 'baz'
- !!private 'private'
- !map {}
- !seq []
""", [
    'tag:yaml.org,2002:int',
    'tag:yaml.org,2002:yamltype',
    'tag:python.yaml.org,2002:type',
    'tag:domain.tld,2002:type',
    'x-private:private',
    'tag:yaml.org,2002:map',
    'tag:yaml.org,2002:seq',
]

class TestTypes(unittest.TestCase):

    def testParserType(self):
        parser = _syck.Parser(EXAMPLE)
        self.assertEqual(type(parser), _syck.ParserType)
        parser.close()

    def testNodeType(self):
        parser = _syck.Parser(EXAMPLE)
        document = parser.parse()
        self.assertEqual(type(document), _syck.NodeType)
        parser.close()

    def testNodeType2(self):
        self.assertRaises(TypeError, (lambda: _syck.Node()))

class TestErrors(unittest.TestCase):

    def testError(self):
        parser = _syck.Parser(INVALID[0])
        self.assertRaises(_syck.error, (lambda: parser.parse()))
        parser.close()

    def testErrorLocation(self):
        source, line, column = INVALID
        parser = _syck.Parser(source)
        try:
            parser.parse()
            raise Exception
        except _syck.error, e:
            self.assertEqual(e.args[1], line)
            self.assertEqual(e.args[2], column)

class TestValuesAndSources(unittest.TestCase):

    def testValues1(self):
        self._testValues(COMPARE1)

    def testValues2(self):
        self._testValues(COMPARE2)

    def testValues3(self):
        self._testValues(COMPARE3)

    def testFileValues1(self):
        self._testFileValues(COMPARE1)

    def testFileValues2(self):
        self._testFileValues(COMPARE2)

    def testFileValues3(self):
        self._testFileValues(COMPARE3)

    def testNonsense(self):
        parser = _syck.Parser(None)
        self.assertRaises(AttributeError, (lambda: parser.parse()))
        parser.close()

    def _testValues(self, (source, structure)):
        parser = _syck.Parser(source)
        document = parser.parse()
        self.assertEqualStructure(document, structure)
        parser.close()

    def _testFileValues(self, (source, structure)):
        parser = _syck.Parser(StringIO.StringIO(source))
        document = parser.parse()
        self.assertEqualStructure(document, structure)
        parser.close()

    def assertEqualStructure(self, node, structure):
        if node.kind == 'scalar':
            self.assertEqual(type(structure), str)
            self.assertEqual(node.value, structure)
        elif node.kind == 'seq':
            self.assertEqual(type(structure), list)
            self.assertEqual(len(node.value), len(structure))
            for i, item in enumerate(node.value):
                self.assertEqualStructure(item, structure[i])
        elif node.kind == 'map':
            self.assertEqual(type(structure), dict)
            self.assertEqual(len(node.value), len(structure))
            for key in node.value:
                self.assert_(key.value in structure)
                self.assertEqualStructure(node.value[key], structure[key.value])

class TestDocuments(unittest.TestCase):

    def testDocuments0(self):
        self._testDocuments(DOCUMENTS0, 0)

    def testDocuments1(self):
        self._testDocuments(DOCUMENTS1, 1)

    def testDocuments2(self):
        self._testDocuments(DOCUMENTS2, 2)

    def testDocuments3(self):
        self._testDocuments(DOCUMENTS3, 3)

    def _testDocuments(self, source, length):
        parser = _syck.Parser(source)
        documents = parser.parse_documents()
        self.assertEqual(len(documents), length)
        parser.close()
        parser = _syck.Parser(source)
        for k in range(length):
            document = parser.parse()
            self.assert_(document)
        self.assertEqual(parser.parse(), None)
        parser.close()

class TestImplicitTyping(unittest.TestCase):

    def testImplicitAndExpansionTyping(self):
        self._testTyping(True, True)

    def testImplicitTyping(self):
        self._testTyping(True, False)

    def testExpansionTyping(self):
        self._testTyping(False, True)

    def testNoTyping(self):
        self._testTyping(False, False)

    def _testTyping(self, implicit_typing, taguri_expansion):
        parser = _syck.Parser(IMPLICIT_TYPING[0], implicit_typing, taguri_expansion)
        for node, (type_id, explicit) in zip(parser.parse().value, IMPLICIT_TYPING[1]):
            if type_id is not None and taguri_expansion:
                type_id = 'tag:yaml.org,2002:%s' % type_id
            if implicit_typing or explicit:
                self.assertEqual(node.type_id, type_id)
            else:
                self.assertEqual(node.type_id, None)

class TestExplicitTyping(unittest.TestCase):

    def testExplicitTyping(self):
        parser = _syck.Parser(EXPLICIT_TYPING[0])
        for node, type_id in zip(parser.parse().value, EXPLICIT_TYPING[1]):
            self.assertEqual(node.type_id, type_id)

def main(module='__main__'):
    unittest.main(module)

if __name__ == '__main__':
    main()

