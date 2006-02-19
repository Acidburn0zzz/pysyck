
from __future__ import generators

import unittest
import syck
import StringIO
import test_emitter

try:
    import datetime
except:
    class _datetime:
        def datetime(self, *args):
            return args
    datetime = _datetime()

try:
    Set = set
except:
    try:
        from sets import Set
    except ImportError:
        def Set(items):
            set = {}
            for items in items:
                set[items] = None
            return set

EXAMPLE = {
    'foo': 'bar',
    'sequence': ['alpha', 'beta', 'gamma'],
    'mapping': {'a': 'alpha', 'b': 'beta', 'c': 'gamma'},
}

SIMPLE_EXAMPLE = [
    'Mark McGwire',
    'Sammy Sosa',
    'Ken Griffey',
]

ALIAS_SCALAR = ["foo, bar, and baz"]
ALIAS_SCALAR.append(ALIAS_SCALAR[0])
ALIAS_SCALAR.append(ALIAS_SCALAR[0])
ALIAS_SCALAR.append(ALIAS_SCALAR[0])

ALIAS_SEQ = [['foo', ['bar']]]
ALIAS_SEQ.append(ALIAS_SEQ[0])
ALIAS_SEQ.append(ALIAS_SEQ[0])

ALIAS_MAP = [{'foo': 'bar'}]
ALIAS_MAP.append(ALIAS_MAP[0])

ODD_ALIASES = [
    [None]*2,
    [0]*3,
    [1]*4,
    [100]*5,
    ['']*6,
    ['foo']*7,
]

INF = 1e300000
NAN = INF/INF

SCALARS = [
    None,
    True, False,
    0, 123, -4567,
    123.4e-5, INF, NAN,
    'foo, bar, baz',
    datetime.datetime(2001, 12, 15, 2, 59, 43, 100000),
]

COLLECTIONS = [
    Set(range(10)),
]

class TestOutput(unittest.TestCase):

    def testStringOutput(self):
        source = syck.dump(EXAMPLE)
        object = syck.load(source)
        self.assertEqual(object, EXAMPLE)

    def testFileOutput(self):
        output = StringIO.StringIO()
        syck.dump(EXAMPLE, output)
        output.seek(0)
        object = syck.load(output)
        self.assertEqual(object, EXAMPLE)

    def testNonsenseOutput(self):
        self.assertRaises(AttributeError, lambda: syck.dump(EXAMPLE, 'output'))

class TestDocuments(unittest.TestCase):

    def _get_examples(self):
        yield EXAMPLE
        yield SIMPLE_EXAMPLE
        yield EXAMPLE

    def testStringOutput(self):
        source = syck.dump_documents(self._get_examples())
        documents = syck.load_documents(source)
        self.assertEqual(list(documents), list(self._get_examples()))
        
    def testFileOutput(self):
        output = StringIO.StringIO()
        syck.dump_documents(self._get_examples(), output)
        output.seek(0)
        documents = syck.load_documents(output)
        self.assertEqual(list(documents), list(self._get_examples()))

class TestEmitter(unittest.TestCase):

    def _get_examples(self):
        yield test_emitter.EXAMPLE
        yield test_emitter.EXAMPLE

    def testStringDocument(self):
        source = syck.emit(test_emitter.EXAMPLE)
        node = syck.parse(source)
        self.assertEqual(test_emitter.strip(test_emitter.EXAMPLE),
                test_emitter.strip(node))

    def testFileDocument(self):
        output = StringIO.StringIO()
        syck.emit_documents(self._get_examples(), output)
        output.seek(0)
        nodes = syck.parse_documents(output)
        self.assertEqual(map(test_emitter.strip, self._get_examples()),
                map(test_emitter.strip, nodes))

class TestAliases(unittest.TestCase):

    def testAliases(self):
        self._testAlias(ALIAS_SCALAR)
        self._testAlias(ALIAS_SEQ)
        self._testAlias(ALIAS_MAP)

    def _testAlias(self, objects):
        objects = syck.load(syck.dump(objects))
        for object in objects:
            self.assert_(object is objects[0])

class TestNoOddAliases(unittest.TestCase):

    def testOddAliases(self):
        document = syck.parse(syck.dump(ODD_ALIASES))
        for group in document.value:
            for item in group.value[1:]:
                self.assert_(item is not group.value[0])

class TestScalarTypes(unittest.TestCase):

    def testScalarTypes(self):
        scalars = syck.load(syck.dump(SCALARS))
        for a, b in zip(scalars, SCALARS):
            self.assertEqual(type(a), type(b))
            if type(a) is float:
                self.assertEqual(repr(a), repr(b))
            else:
                self.assertEqual(a, b)

class TestCollectionTypes(unittest.TestCase):

    def testCollectionTypes(self):
        collections = syck.load(syck.dump(COLLECTIONS))
        for a, b in zip(collections, COLLECTIONS):
            self.assertEqual(type(a), type(b))
            self.assertEqual(a, b)


